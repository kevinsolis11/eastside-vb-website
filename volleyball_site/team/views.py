from django.views.generic import ListView, DetailView, CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.conf import settings
from django.utils import timezone
from django.http import Http404, HttpResponse, StreamingHttpResponse
from datetime import timedelta
from . import tasks
from .tasks import send_invite_mail_sync
import logging
import os

from .models import Player, AccessCode, PlayerProfile, GameVideo, PlayerStats, AISummary, VideoAnalysis, VideoConversionLog
from .forms import SignUpForm, GameVideoUploadForm, PlayerStatsForm, AISummaryForm, AnnouncementForm
from django.contrib.auth import logout as auth_logout
from django.shortcuts import resolve_url

logger = logging.getLogger(__name__)


class PlayerListView(ListView):
    model = Player
    template_name = "team/player_list.html"
    context_object_name = "players"
    
    def dispatch(self, request, *args, **kwargs):
        # Only coaches (staff) can view player list
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "You don't have permission to view the player list.")
            return redirect('team:player_dashboard')
        return super().dispatch(request, *args, **kwargs)


class PlayerDetailView(DetailView):
    model = Player
    template_name = "team/player_detail.html"
    context_object_name = "player"
    
    def dispatch(self, request, *args, **kwargs):
        # Get the player being viewed
        player = self.get_object()
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Check if this is the user's own profile or if user is a coach
        try:
            user_profile = request.user.playerprofile  # type: ignore
            is_own_profile = user_profile.player == player
        except (PlayerProfile.DoesNotExist, AttributeError):
            is_own_profile = False
        
        is_coach_user = request.user.is_staff or request.user.is_superuser
        
        # Only allow viewing if it's own profile or user is a coach
        if not (is_own_profile or is_coach_user):
            messages.error(request, "You can only view your own profile.")
            return redirect('team:player_dashboard')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = self.object  # type: ignore
        
        # Get player profile and AI summary if available
        try:
            # Try to find PlayerProfile linked to this Player
            player_profile = PlayerProfile.objects.get(player=player)
            context['player_profile'] = player_profile
            
            # Get AI summary if exists
            try:
                ai_summary = AISummary.objects.get(player=player_profile)
                context['ai_summary'] = ai_summary
            except AISummary.DoesNotExist:
                context['ai_summary'] = None
        except PlayerProfile.DoesNotExist:
            context['player_profile'] = None
            context['ai_summary'] = None
        
        # Check if user is a coach
        context['is_coach'] = is_coach(self.request.user)
        
        return context


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get('email')
            user.save()

            # access_code is stored as an instance by the form
            access_code = form.cleaned_data.get('access_code')
            if access_code:
                # assign manager role automatically
                if access_code.role == AccessCode.ROLE_MANAGER:
                    user.is_staff = True
                    user.is_superuser = False
                    user.save()

                access_code.is_used = True
                access_code.save()
                messages.success(request, "Account created — your access code was applied.")

            # create empty profile for all users (players may link a Player later)
            PlayerProfile.objects.create(user=user)

            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'team/signup.html', {'form': form})


class GenerateCodeForm(forms.Form):
    role = forms.ChoiceField(choices=AccessCode.ROLE_CHOICES)
    count = forms.IntegerField(min_value=1, max_value=50, initial=1)
    expiry_days = forms.IntegerField(required=False, min_value=1, max_value=365, help_text="Optional expiry in days")
    email = forms.EmailField(required=False, help_text="Optional: send code(s) to this email and tie to it")


def staff_check(user):
    return user.is_active and user.is_staff


@login_required
@user_passes_test(staff_check)
def coach_codes(request):
    try:
        codes = AccessCode.objects.order_by('-created_at')[:100]
        created = []

        if request.method == 'POST':
            form = GenerateCodeForm(request.POST)
            if form.is_valid():
                role = form.cleaned_data['role']
                count = form.cleaned_data['count']
                expiry_days = form.cleaned_data.get('expiry_days')
                email = form.cleaned_data.get('email')
                for _ in range(count):
                    raw = AccessCode.generate(role=role)
                    if expiry_days:
                        expires_at = timezone.now() + timedelta(days=expiry_days)
                        ac = AccessCode.objects.create(code=raw, role=role, expires_at=expires_at, allowed_email=email)
                    else:
                        ac = AccessCode.objects.create(code=raw, role=role, allowed_email=email)
                    created.append(ac)
                messages.success(request, f"Generated {count} {role} code(s).")
                # send email invites via Celery when an email was provided
                if email:
                    codes_list = [c.code for c in created]
                    signup_url = request.build_absolute_uri(reverse_lazy('signup'))
                    
                    # Check if email is configured before attempting to send
                    email_host = getattr(settings, 'EMAIL_HOST', '').strip()
                    email_user = getattr(settings, 'EMAIL_HOST_USER', '').strip()
                    
                    if not email_host or email_host == 'localhost' or not email_user:
                        messages.error(
                            request, 
                            "⚠️ Email not configured on server. "
                            "Invite codes generated but NOT sent via email. "
                            "Please distribute codes manually or contact admin to configure email."
                        )
                    else:
                        try:
                            # Prefer asynchronous scheduling, but in DEBUG (or when Celery isn't running)
                            # send synchronously so tests and local development see immediate results.
                            if getattr(settings, 'DEBUG', False):
                                send_invite_mail_sync(codes_list, email, signup_url)
                                messages.success(request, f"✓ Invite email(s) sent to {email}.")
                            else:
                                try:
                                    tasks.send_invite_mail.apply_async(args=[codes_list, email, signup_url])  # type: ignore
                                    messages.success(request, f"✓ Invite email(s) queued for {email}. Should arrive within 1 minute.")
                                except Exception as e:
                                    # Fallback to synchronous send if scheduling fails
                                    try:
                                        send_invite_mail_sync(codes_list, email, signup_url)
                                        messages.success(request, f"✓ Invite email(s) sent to {email}.")
                                    except Exception as email_err:
                                        messages.error(
                                            request,
                                            f"❌ Failed to send invite email to {email}: {str(email_err)}. "
                                            f"Codes generated but not sent. Please distribute manually."
                                        )
                        except Exception as e:
                            messages.error(request, f"❌ Error processing email request: {str(e)}")
        else:
            form = GenerateCodeForm()

        return render(request, 'team/coach_codes.html', {'form': form, 'codes': codes, 'created': created})
    except Exception as e:
        logger.exception(f"Error in coach_codes view: {str(e)}")
        return render(request, 'team/coach_codes.html', {
            'form': GenerateCodeForm(), 
            'codes': [], 
            'created': [],
            'error': str(e)
        })


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        # redirect staff users to coach area
        user = self.request.user
        if user.is_active and user.is_staff:
            return reverse_lazy('team:coach_codes')
        return settings.LOGIN_REDIRECT_URL


def logout_get(request):
    """Perform logout via GET and redirect to LOGOUT_REDIRECT_URL (convenience).

    Note: the standard logout URL requires POST for CSRF safety; this view
    provides an explicit GET endpoint when callers want a simple link.
    """
    auth_logout(request)
    next_url = getattr(settings, 'LOGOUT_REDIRECT_URL', None) or settings.LOGIN_URL
    return redirect(next_url)


# ============= Video Upload & Streaming =============

def is_coach(user):
    """Check if user is a coach (staff member)."""
    if not user.is_authenticated:
        return False
    return user.is_staff or user.is_superuser


def is_team_member(user):
    """Check if user is a team member (has PlayerProfile)."""
    if user.is_staff or user.is_superuser:
        return True
    return hasattr(user, 'playerprofile') and user.playerprofile is not None


@login_required
@user_passes_test(is_coach)
def video_upload(request):
    """Coach uploads game videos."""
    if request.method == 'POST':
        form = GameVideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.uploaded_by = request.user
            
            # Calculate file size in MB
            if video.video:
                video.file_size_mb = video.video.size / (1024 * 1024)
            
            video.save()
            
            # Create conversion log immediately
            filename = os.path.basename(video.video.name)
            file_ext = os.path.splitext(filename)[1].lstrip('.').upper() or 'UNKNOWN'
            
            conversion_log = VideoConversionLog.objects.create(
                video=video,
                original_filename=filename,
                original_format=file_ext,
                original_size_mb=video.file_size_mb,
                debug_log=f"📹 Video uploaded by {request.user.username}\n"
                          f"Filename: {filename}\n"
                          f"Format: {file_ext}\n"
                          f"Size: {video.file_size_mb:.1f} MB\n"
                          f"Timestamp: {timezone.now().isoformat()}\n"
            )
            
            logger.info(
                f"✅ Video uploaded: {video.title} (ID: {video.id}) "
                f"by {request.user.username} | File: {filename} | Size: {video.file_size_mb:.1f} MB"
            )
            
            messages.success(request, f'✅ Video "{video.title}" uploaded successfully! Processing will begin shortly.')
            return redirect('team:video_list')
    else:
        form = GameVideoUploadForm()
    
    return render(request, 'team/video_upload.html', {'form': form})



@login_required
@user_passes_test(is_team_member)
def video_list(request):
    """List all team videos (coaches see all, players see private ones)."""
    if is_coach(request.user):
        # Coaches see all videos
        videos = GameVideo.objects.all().order_by('-game_date', '-uploaded_at')
    else:
        # Players see only private team videos
        videos = GameVideo.objects.filter(private=True).order_by('-game_date', '-uploaded_at')
    
    context = {
        'videos': videos,
        'is_coach': is_coach(request.user),
    }
    return render(request, 'team/video_list.html', context)


@login_required
@user_passes_test(is_team_member)
def video_detail(request, pk):
    """View video details and stream."""
    video = get_object_or_404(GameVideo, pk=pk)
    
    # Check access
    if not video.can_view(request.user):
        raise Http404("Video not found or you don't have permission to view it.")
    
    # Increment view count
    if request.method == 'GET' and 'view_count_incremented' not in request.session:
        video.view_count += 1
        video.save(update_fields=['view_count'])
        request.session['view_count_incremented'] = True
    
    # Detect video format
    video_mime_type = 'video/mp4'
    if video.video:
        video_url = video.video.url.lower()
        if video_url.endswith('.mov'):
            video_mime_type = 'video/quicktime'
        elif video_url.endswith('.mkv'):
            video_mime_type = 'video/x-matroska'
        elif video_url.endswith('.webm'):
            video_mime_type = 'video/webm'
        elif video_url.endswith('.avi'):
            video_mime_type = 'video/x-msvideo'
    
    context = {
        'video': video,
        'is_coach': is_coach(request.user),
        'is_uploader': video.uploaded_by == request.user or is_coach(request.user),
        'video_mime_type': video_mime_type,
    }
    return render(request, 'team/video_detail.html', context)


@login_required
@user_passes_test(is_coach)
def video_edit(request, pk):
    """Coach edits video metadata."""
    video = get_object_or_404(GameVideo, pk=pk)
    
    # Only uploader can edit
    if video.uploaded_by != request.user and not request.user.is_superuser:
        raise Http404("You don't have permission to edit this video.")
    
    if request.method == 'POST':
        form = GameVideoUploadForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            video = form.save()
            messages.success(request, f'Video "{video.title}" updated successfully!')
            return redirect('team:video_detail', pk=video.pk)
    else:
        form = GameVideoUploadForm(instance=video)
    
    return render(request, 'team/video_edit.html', {'form': form, 'video': video})


@login_required
@user_passes_test(is_coach)
def video_delete(request, pk):
    """Coach deletes a video."""
    video = get_object_or_404(GameVideo, pk=pk)
    
    # Only uploader can delete
    if video.uploaded_by != request.user and not request.user.is_superuser:
        raise Http404("You don't have permission to delete this video.")
    
    if request.method == 'POST':
        video_title = video.title
        video.delete()
        messages.success(request, f'Video "{video_title}" deleted successfully!')
        return redirect('team:video_list')
    
    return render(request, 'team/video_delete_confirm.html', {'video': video})


# ═══════════════════════════════════════════════════════════════════════════
# PLAYER STATS VIEWS
# ═══════════════════════════════════════════════════════════════════════════


@login_required
@user_passes_test(is_coach)
def player_stats_list(request):
    """Coach views all team member stats."""
    # Get all player profiles with their stats
    player_profiles = PlayerProfile.objects.select_related('player', 'user', 'playerstats').all()
    
    stats_list = []
    for profile in player_profiles:
        try:
            stats = profile.playerstats  # type: ignore
        except PlayerStats.DoesNotExist:
            # Create empty stats if doesn't exist
            stats = PlayerStats.objects.create(player=profile)
        
        stats_list.append({
            'profile': profile,
            'stats': stats,
            'player': profile.player,
        })
    
    # Sort by player number
    stats_list.sort(key=lambda x: x['player'].number if x['player'] and x['player'].number else 999)
    
    # Calculate totals
    total_kills = sum(s['stats'].kills for s in stats_list if s['stats'])
    total_blocks = sum(s['stats'].blocks for s in stats_list if s['stats'])
    total_aces = sum(s['stats'].aces for s in stats_list if s['stats'])
    total_digs = sum(s['stats'].digs for s in stats_list if s['stats'])
    
    context = {
        'stats_list': stats_list,
        'total_kills': total_kills,
        'total_blocks': total_blocks,
        'total_aces': total_aces,
        'total_digs': total_digs,
    }
    return render(request, 'team/player_stats_list.html', context)


@login_required
@user_passes_test(is_coach)
def player_stats_edit(request, player_id):
    """Coach edits player stats."""
    player_profile = get_object_or_404(PlayerProfile, pk=player_id)
    
    # Get or create PlayerStats
    stats, created = PlayerStats.objects.get_or_create(player=player_profile)
    
    if request.method == 'POST':
        form = PlayerStatsForm(request.POST, instance=stats)
        if form.is_valid():
            form.save()
            player_name = player_profile.player.first_name if player_profile.player else player_profile.user.username
            messages.success(request, f'Stats for {player_name} updated successfully!')
            return redirect('team:player_stats_list')
    else:
        form = PlayerStatsForm(instance=stats)
    
    player_name = player_profile.player.first_name if player_profile.player else player_profile.user.username
    if player_profile.player and player_profile.player.last_name:
        player_name += f" {player_profile.player.last_name}"
    
    context = {
        'form': form,
        'player_profile': player_profile,
        'player_name': player_name,
        'stats': stats,
    }
    return render(request, 'team/player_stats_edit.html', context)


@login_required
def player_stats_view(request, player_id):
    """Player views their own stats or coach views any stats."""
    player_profile = get_object_or_404(PlayerProfile, pk=player_id)
    
    # Check permissions: allow viewing if coach OR if viewing own stats
    is_own_profile = player_profile.user == request.user
    is_coach_user = request.user.is_staff or request.user.is_superuser
    
    # Only raise 404 if not a coach AND not viewing own profile
    if not (is_own_profile or is_coach_user):
        raise Http404("You don't have permission to view these stats.")
    
    try:
        stats = player_profile.playerstats  # type: ignore
    except PlayerStats.DoesNotExist:
        stats = None
    
    player_name = player_profile.player.first_name if player_profile.player else player_profile.user.username
    if player_profile.player and player_profile.player.last_name:
        player_name += f" {player_profile.player.last_name}"
    
    context = {
        'player_profile': player_profile,
        'stats': stats,
        'player_name': player_name,
    }
    return render(request, 'team/player_stats_view.html', context)


@login_required
def player_dashboard(request):
    """Player dashboard showing profile, stats, videos, and team info. For coaches, shows admin dashboard."""
    from .models import Announcement
    from django.contrib.auth.models import User
    from rest_framework.authtoken.models import Token
    
    # Get or create token for the user
    token, created = Token.objects.get_or_create(user=request.user)
    
    # Check if user is coach/staff - show coach dashboard
    if is_coach(request.user):
        # Coach Dashboard
        context = {
            'is_coach': True,
            'auth_token': token.key,
            'total_players': Player.objects.count(),
            'total_videos': GameVideo.objects.count(),
            'total_profiles': PlayerProfile.objects.count(),
            'total_users': User.objects.count(),
            'recent_videos': GameVideo.objects.order_by('-uploaded_at')[:5],
            'recent_players': Player.objects.order_by('-id')[:5],
            'access_codes': AccessCode.objects.filter(is_used=False).order_by('-created_at')[:5],
            'announcements': Announcement.objects.order_by('-id')[:5],
        }
        return render(request, 'team/coach_dashboard.html', context)
    
    # Player Dashboard
    # Check if user has a PlayerProfile
    try:
        player_profile = request.user.playerprofile
    except PlayerProfile.DoesNotExist:
        # User is logged in but not a team member
        return render(request, 'team/player_dashboard.html', {
            'player_profile': None,
            'message': 'Your account is not linked to a player profile yet. Please contact a coach.'
        })
    
    # Get player stats
    try:
        stats = player_profile.playerstats
    except PlayerStats.DoesNotExist:
        stats = None
    
    # Get player videos (featuring them or team videos)
    videos = GameVideo.objects.filter(private=True).order_by('-game_date')[:5]
    
    # Get player info
    player = player_profile.player
    
    # Build context
    context = {
        'player_profile': player_profile,
        'player': player,
        'stats': stats,
        'videos': videos,
        'is_coach': is_coach(request.user),
    }
    
    return render(request, 'team/player_dashboard.html', context)


@login_required
@user_passes_test(is_coach)
def player_edit(request, player_id):
    """Coach edits player information (name, number, position, height)."""
    from .forms import PlayerEditForm
    
    player_profile = get_object_or_404(PlayerProfile, pk=player_id)
    player = player_profile.player
    
    if not player:
        messages.error(request, "This player profile is not linked to a player.")
        return redirect('team:player_stats_list')
    
    if request.method == 'POST':
        form = PlayerEditForm(request.POST)
        if form.is_valid():
            # Update Player
            player.first_name = form.cleaned_data['first_name']
            player.last_name = form.cleaned_data['last_name']
            player.number = form.cleaned_data['number'] or None
            player.position = form.cleaned_data['position'] or ''
            player.save()  # type: ignore
            
            # Update PlayerProfile
            player_profile.height = form.cleaned_data['height'] or ''
            player_profile.save()
            
            messages.success(request, f'Player profile for {player.first_name} {player.last_name} updated successfully!')
            return redirect('team:player_stats_list')
    else:
        form = PlayerEditForm(initial={
            'first_name': player.first_name,
            'last_name': player.last_name,
            'number': player.number,
            'position': player.position,
            'height': player_profile.height,
        })
    
    context = {
        'form': form,
        'player_profile': player_profile,
        'player': player,
    }
    return render(request, 'team/player_edit.html', context)


@login_required
@user_passes_test(is_coach)
def player_delete(request, player_id):
    """Coach deletes a player from the team (by PlayerProfile ID)."""
    player_profile = get_object_or_404(PlayerProfile, pk=player_id)
    player = player_profile.player
    user = player_profile.user
    
    player_name = f"{player.first_name} {player.last_name}" if player else user.username
    
    if request.method == 'POST':
        # Delete related objects
        try:
            # Delete PlayerStats if exists
            try:
                player_profile.playerstats.delete()
            except PlayerStats.DoesNotExist:
                pass
            
            # Delete AISummary if exists
            try:
                player_profile.aisummary.delete()
            except AISummary.DoesNotExist:
                pass
            
            # Delete the Player object if exists
            if player:
                player.delete()
            
            # Delete the PlayerProfile
            player_profile.delete()
            
            # Delete the User account
            user.delete()
            
            messages.success(request, f'Player "{player_name}" has been removed from the team.')
            return redirect('team:player_stats_list')
        except Exception as e:
            messages.error(request, f'Error deleting player: {str(e)}')
            return redirect('team:player_stats_list')
    
    # GET request - show confirmation page
    context = {
        'player_profile': player_profile,
        'player': player,
        'player_name': player_name,
    }
    return render(request, 'team/player_delete.html', context)


@login_required
def player_delete_by_player(request, player_id):
    """Coach deletes a player from the team (by Player ID - for player list page)."""
    # Manual coach check with proper error message
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "You don't have permission to delete players.")
        return redirect('team:player-list')
    
    player = get_object_or_404(Player, pk=player_id)
    
    # Find the PlayerProfile for this player
    try:
        player_profile = PlayerProfile.objects.get(player=player)
        user = player_profile.user
    except PlayerProfile.DoesNotExist:
        player_profile = None
        user = None
    
    player_name = f"{player.first_name} {player.last_name}"
    
    if request.method == 'POST':
        try:
            # Delete related objects
            if player_profile:
                # Delete PlayerStats if exists
                try:
                    player_profile.playerstats.delete()
                except PlayerStats.DoesNotExist:
                    pass
                
                # Delete AISummary if exists
                try:
                    player_profile.aisummary.delete()
                except AISummary.DoesNotExist:
                    pass
                
                # Delete the PlayerProfile
                player_profile.delete()
                
                # Delete the User account
                if user:
                    user.delete()
            
            # Delete the Player object
            player.delete()
            
            messages.success(request, f'Player "{player_name}" has been removed from the team.')
            return redirect('team:player-list')
        except Exception as e:
            messages.error(request, f'Error deleting player: {str(e)}')
            return redirect('team:player-list')
    
    # GET request - show confirmation page
    context = {
        'player_profile': player_profile,
        'player': player,
        'player_name': player_name,
    }
    return render(request, 'team/player_delete.html', context)


@login_required
@user_passes_test(is_coach)
def generate_ai_summary(request, player_profile_id):
    """Coach generates AI performance summary for a player."""
    player_profile = get_object_or_404(PlayerProfile, id=player_profile_id)
    
    if request.method == 'POST':
        form = AISummaryForm(request.POST)
        if form.is_valid():
            game_context = form.cleaned_data.get('game_context') or ''
            
            # Try to generate synchronously in DEBUG mode, else use Celery
            if settings.DEBUG:
                result = tasks.generate_ai_summary_sync(player_profile.id, game_context)  # type: ignore
                if result['success']:
                    messages.success(request, f"AI summary generated for {player_profile}!")
                    player_id = player_profile.player.id if player_profile.player else player_profile.id  # type: ignore
                    return redirect('team:player_detail', pk=player_id)
                else:
                    messages.error(request, f"Error generating summary: {result.get('error', 'Unknown error')}")
            else:
                # Queue async task
                tasks.generate_ai_summary_task.apply_async(args=[player_profile.id, game_context])  # type: ignore
                messages.info(request, f"Summary generation queued for {player_profile}. Check back soon!")
                player_id = player_profile.player.id if player_profile.player else player_profile.id  # type: ignore
                return redirect('team:player_detail', pk=player_id)
    else:
        form = AISummaryForm()
    
    context = {
        'form': form,
        'player_profile': player_profile,
    }
    return render(request, 'team/generate_ai_summary.html', context)


# ============= Video Analysis (ChatGPT 5) =============

@login_required
@user_passes_test(is_coach)
def request_video_analysis(request, video_id):
    """Coach requests ChatGPT video analysis for a game video."""
    video = get_object_or_404(GameVideo, pk=video_id)
    
    # Only uploader or superuser can request analysis
    if video.uploaded_by != request.user and not request.user.is_superuser:
        messages.error(request, "Only the uploader can request analysis for this video.")
        return redirect('team:video_detail', pk=video_id)
    
    # Get or create analysis record
    analysis, created = VideoAnalysis.objects.get_or_create(
        video=video,
        defaults={'requested_by': request.user}
    )
    
    # Queue analysis task if not already processing
    if analysis.status in [VideoAnalysis.STATUS_PENDING, VideoAnalysis.STATUS_FAILED]:
        from .tasks import analyze_video_task
        try:
            analyze_video_task.apply_async(args=[video_id])  # type: ignore
            analysis.status = VideoAnalysis.STATUS_PENDING
            analysis.requested_by = request.user
            analysis.save()
            messages.success(request, f"Video analysis queued for '{video.title}'. Check back soon!")
        except Exception as e:
            messages.error(request, f"Failed to queue analysis: {str(e)}")
    else:
        messages.info(request, f"Analysis is already {analysis.status}.")
    
    return redirect('team:video_analysis_detail', video_id=video_id)


@login_required
@user_passes_test(is_team_member)
def video_analysis_detail(request, video_id):
    """View video analysis results."""
    video = get_object_or_404(GameVideo, pk=video_id)
    
    # Check if user can view this video
    if not video.can_view(request.user):
        raise Http404("Video not found or you don't have permission to view it.")
    
    # Get analysis if it exists
    try:
        analysis = VideoAnalysis.objects.get(video=video)
    except VideoAnalysis.DoesNotExist:
        analysis = None
    
    context = {
        'video': video,
        'analysis': analysis,
        'is_coach': is_coach(request.user),
        'can_request_analysis': is_coach(request.user) and (video.uploaded_by == request.user or request.user.is_superuser),
    }
    return render(request, 'team/video_analysis_detail.html', context)


# ============= Announcements =============

@login_required
@user_passes_test(is_coach)
def announcement_list(request):
    """Coach views all announcements."""
    from .models import Announcement
    
    announcements = Announcement.objects.filter(coach=request.user).order_by('-created_at')
    
    context = {
        'announcements': announcements,
    }
    return render(request, 'team/announcement_list.html', context)


@login_required
@user_passes_test(is_coach)
def announcement_create(request):
    """Coach creates a new announcement."""
    from .models import Announcement
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.coach = request.user
            announcement.save()
            messages.success(request, 'Announcement posted successfully!')
            return redirect('team:announcement_list')
    else:
        form = AnnouncementForm()
    
    context = {
        'form': form,
    }
    return render(request, 'team/announcement_form.html', context)


@login_required
@user_passes_test(is_coach)
def announcement_edit(request, announcement_id):
    """Coach edits an announcement."""
    from .models import Announcement
    
    announcement = get_object_or_404(Announcement, pk=announcement_id, coach=request.user)
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated successfully!')
            return redirect('team:announcement_list')
    else:
        form = AnnouncementForm(instance=announcement)
    
    context = {
        'form': form,
        'announcement': announcement,
    }
    return render(request, 'team/announcement_form.html', context)


@login_required
@user_passes_test(is_coach)
def announcement_delete(request, announcement_id):
    """Coach deletes an announcement."""
    from .models import Announcement
    
    announcement = get_object_or_404(Announcement, pk=announcement_id, coach=request.user)
    
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'Announcement deleted successfully!')
        return redirect('team:announcement_list')
    
    context = {
        'announcement': announcement,
    }
    return render(request, 'team/announcement_confirm_delete.html', context)


@login_required
def announcement_feed(request):
    """Players view all announcements (team feed)."""
    from .models import Announcement
    
    # Check if user is a team member
    if not (request.user.is_staff or request.user.is_superuser):
        if not hasattr(request.user, 'playerprofile'):
            messages.error(request, "You must be a team member to view announcements.")
            return redirect('team:player_dashboard')
    
    announcements = Announcement.objects.all().order_by('-created_at')
    
    context = {
        'announcements': announcements,
    }
    return render(request, 'team/announcement_feed.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def ai_chat_view(request):
    """AI chatbot interface for coaches to query player information."""
    from rest_framework.authtoken.models import Token
    
    # Get or create token for the user
    token, created = Token.objects.get_or_create(user=request.user)
    
    context = {
        'auth_token': token.key
    }
    return render(request, 'team/ai_chat.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def settings_view(request):
    """Settings and management page for coaches."""
    from django.utils import timezone
    from .models import Announcement
    
    # Get stats
    total_players = Player.objects.count()
    total_videos = GameVideo.objects.count()
    total_announcements = Announcement.objects.count()
    active_codes = AccessCode.objects.filter(
        is_used=False,
        expires_at__gt=timezone.now()
    ).count()
    
    # Get recent players
    recent_players = Player.objects.select_related('playerprofile').order_by('-id')[:5]
    
    context = {
        'total_players': total_players,
        'total_videos': total_videos,
        'total_announcements': total_announcements,
        'active_codes': active_codes,
        'recent_players': recent_players,
    }
    
    return render(request, 'team/settings.html', context)
