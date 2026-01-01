from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import Q
from .models import PlayerProfile, PlayerStats, GameVideo, AISummary, Announcement, VideoAnalysis, Player
from .serializers import (
    PlayerProfileSerializer, PlayerStatsSerializer, GameVideoSerializer,
    AISummarySerializer, AnnouncementSerializer, LoginSerializer, UserSerializer
)
import re
from typing import Any, Dict

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request) -> Response:
    """Login endpoint - returns user data and token."""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data: Dict[str, Any] = serializer.validated_data  # type: ignore
    username = validated_data.get('username')
    password = validated_data.get('password')
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    if not user:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Rotate token on login for security
    Token.objects.filter(user=user).delete()
    token = Token.objects.create(user=user)
    
    # Get user's player profile if exists
    player_profile = None
    try:
        # PlayerProfile has a user field, so this is the correct lookup
        player_profile = PlayerProfile.objects.get(user=user)
        profile_data = PlayerProfileSerializer(player_profile).data
    except PlayerProfile.DoesNotExist:
        profile_data = None
    
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data,
        'profile': profile_data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request) -> Response:
    """Logout endpoint - deletes user token."""
    try:
        request.user.auth_token.delete()
    except Token.DoesNotExist:
        pass
    return Response({'message': 'Logged out successfully'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_player_profile(request) -> Response:
    """Get current user's player profile."""
    try:
        profile = PlayerProfile.objects.select_related('player').get(player__user=request.user)
        serializer = PlayerProfileSerializer(profile)
        return Response(serializer.data)
    except PlayerProfile.DoesNotExist:
        return Response(
            {'error': 'Player profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_player_stats(request) -> Response:
    """Get current user's player stats."""
    try:
        profile = PlayerProfile.objects.select_related('player').get(player__user=request.user)
        # Use latest stats if multiple rows exist (OneToOne field might be broken)
        stats = PlayerStats.objects.filter(player=profile).order_by('-updated_at').first()
        if stats:
            serializer = PlayerStatsSerializer(stats)
            return Response(serializer.data)
        else:
            # No stats found, return defaults
            return Response({
                'kills': 0,
                'blocks': 0,
                'aces': 0,
                'digs': 0,
                'updated_at': None
            })
    except PlayerProfile.DoesNotExist:
        # Return empty/default stats if none exist
        return Response({
            'kills': 0,
            'blocks': 0,
            'aces': 0,
            'digs': 0,
            'updated_at': None
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_announcements(request) -> Response:
    """Get all announcements for the team."""
    announcements = Announcement.objects.all()
    serializer = AnnouncementSerializer(announcements, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_game_videos(request) -> Response:
    """Get all game videos the user can view (only coaches see all, players see team videos)."""
    videos = GameVideo.objects.all()
    # TODO: Implement per-team/per-user access control
    # For now, all authenticated users see all videos
    serializer = GameVideoSerializer(videos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ai_summary(request) -> Response:
    """Get AI summary for current user."""
    try:
        profile = PlayerProfile.objects.select_related('player').get(player__user=request.user)
        summary = AISummary.objects.get(player=profile)
        serializer = AISummarySerializer(summary)
        return Response(serializer.data)
    except (PlayerProfile.DoesNotExist, AISummary.DoesNotExist):
        return Response({'summary': 'No summary available yet'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_video_analysis(request, video_id) -> Response:
    """Request ChatGPT video analysis for a game video.
    
    Only coaches can request analysis.
    """
    try:
        video = GameVideo.objects.get(id=video_id)
        
        # Check if user is coach (staff/superuser or uploaded the video)
        if not (request.user.is_staff or request.user.is_superuser or video.uploaded_by == request.user):
            return Response(
                {'error': 'Only coaches can request video analysis'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if analysis already exists
        analysis, created = VideoAnalysis.objects.get_or_create(
            video=video,
            defaults={'requested_by': request.user}
        )
        
        if created or analysis.status == VideoAnalysis.STATUS_FAILED:
            # Queue the analysis task
            from .tasks import analyze_video_task
            analyze_video_task.delay(video_id=video_id)  # type: ignore
            analysis.status = VideoAnalysis.STATUS_PENDING
            analysis.requested_by = request.user
            analysis.save()
            message = 'Video analysis queued successfully'
        else:
            message = f'Analysis already {analysis.status}'
        
        return Response({
            'message': message,
            'status': analysis.status,
            'analysis_id': getattr(analysis, 'id', None)
        })
    
    except GameVideo.DoesNotExist:
        return Response(
            {'error': 'Video not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_analysis(request, video_id) -> Response:
    """Get video analysis results if available."""
    try:
        video = GameVideo.objects.get(id=video_id)
        
        # Check if user can view this video (if method exists)
        if hasattr(video, 'can_view') and not video.can_view(request.user):
            return Response(
                {'error': 'You do not have permission to view this video'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        analysis = VideoAnalysis.objects.get(video=video)
        
        return Response({
            'status': analysis.status,
            'analysis': analysis.analysis,
            'highlights': analysis.highlights,
            'player_performance': analysis.player_performance,
            'tactical_notes': analysis.tactical_notes,
            'analysis_model': analysis.analysis_model,
            'created_at': analysis.created_at,
            'completed_at': analysis.completed_at,
            'error': analysis.error_message if analysis.status == VideoAnalysis.STATUS_FAILED else None
        })
    
    except GameVideo.DoesNotExist:
        return Response(
            {'error': 'Video not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except VideoAnalysis.DoesNotExist:
        return Response(
            {'error': 'No analysis available for this video'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat(request) -> Response:
    """AI chatbot endpoint that responds to queries about players."""
    # Allow any authenticated user for now (will be restricted to coaches later)
    # Removed staff/superuser check to allow all authenticated users
    
    # Get and validate query - request.data is dict-like in DRF (QueryDict)
    try:
        query = request.data.get('query', '').strip().lower()
    except (AttributeError, TypeError):
        return Response({'error': 'Invalid request format'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate query length
    if not query:
        return Response({'error': 'Please provide a query'}, status=status.HTTP_400_BAD_REQUEST)
    if len(query) > 500:
        return Response({'error': 'Query too long (max 500 characters)'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Parse the query and find relevant players
        players_data = []
        response_text = ""
        
        # Handle greetings and casual conversation (word boundary to avoid false matches)
        greetings = ['hi', 'hello', 'hey', 'sup', 'yo', 'what\'s up', 'whats up', 'wassup']
        greeting_pattern = r'\b(' + '|'.join(re.escape(g) for g in greetings) + r')\b'
        if re.search(greeting_pattern, query):
            response_text = "Hey there! 👋 I'm your AI assistant for the team. I can help you find player info, stats, and more. What would you like to know?"
            return Response({'response': response_text, 'players': []})
        
        # Handle thanks
        if any(word in query for word in ['thanks', 'thank you', 'thx', 'appreciate']):
            response_text = "You're welcome! Happy to help anytime. Need anything else?"
            return Response({'response': response_text, 'players': []})
        
        # Handle how are you
        if 'how are you' in query or 'how r u' in query:
            response_text = "I'm doing great, thanks for asking! Ready to help you with any player info you need. What can I do for you?"
            return Response({'response': response_text, 'players': []})
        
        # Check for "how many" or "count" queries
        if 'how many' in query or 'count' in query or 'total' in query:
            count = PlayerProfile.objects.count()
            if count == 0:
                response_text = "You don't have any players on the roster yet! Ready to add your first player? Just click 'Add New Player' above or use the admin panel."
            elif count == 1:
                response_text = "You have 1 player on your team right now. Would you like to see their info? Just say 'show all players'!"
            else:
                response_text = f"You currently have {count} players on your team! Want to see the full roster? Just ask me 'show all players'."
            return Response({'response': response_text, 'players': []})
        
        # Check for "show all players" or "list players"
        if 'show all' in query or 'list all' in query or 'all players' in query:
            profiles = list(PlayerProfile.objects.select_related('player', 'user').all()[:100])  # Limit to 100 for safety
            profile_count = len(profiles)
            if profile_count == 0:
                response_text = "I don't see any players on the roster yet. Would you like to add some players first? You can do that through the admin panel or by clicking 'Add New Player' above."
                return Response({'response': response_text, 'players': []})
            
            # Build player list
            for profile in profiles:
                if profile and profile.player:  # Extra safety check
                    player_info = extract_player_info(profile)
                    if player_info:  # Ensure extract returned valid data
                        players_data.append(player_info)
            
            # Set response after collecting data
            players_found = len(players_data)
            response_text = f"Of course! I found {players_found} player{'s' if players_found != 1 else ''} on your team. Let me show you everyone:"
            if not players_data:
                response_text = "I found players in the system but none have complete profiles. Please try adding more player data."
        
        # Check for player number (#15, number 15, player 15, just 15, etc.)
        elif '#' in query or 'number' in query or 'player' in query:
            number_match = re.search(r'(?:player\s+|#)?(\d+)', query)
            if number_match:
                number = int(number_match.group(1))
                player = Player.objects.filter(number=number).first()
                if player:
                    profile = PlayerProfile.objects.select_related('player', 'user').filter(player=player).first()
                    if profile:
                        response_text = f"Great question! Let me pull up the details for player #{number}:"
                        player_info = extract_player_info(profile)
                        if player_info:
                            players_data.append(player_info)
                    else:
                        response_text = f"Found player #{number} but their profile is incomplete."
                else:
                    response_text = f"Hmm, I don't see anyone wearing #{number} on the roster. Would you like to see all players instead? Just ask me 'show all players'."
            else:
                response_text = "I couldn't find a player number in your query. Try asking 'Show player #15' or 'Tell me about number 7'"
        
        # Check for position queries
        elif any(pos in query for pos in ['outside', 'setter', 'middle', 'libero', 'opposite', 'hitter']):
            position_map = {
                'outside': 'Outside Hitter',
                'setter': 'Setter',
                'middle': 'Middle Blocker',
                'libero': 'Libero',
                'opposite': 'Opposite'
            }
            
            response_text = "I'd love to help with that position query!"
            found_position = False
            
            for key, position in position_map.items():
                if key in query:
                    profiles = list(PlayerProfile.objects.select_related('player', 'user').filter(position__iexact=position))
                    profile_count = len(profiles)
                    if profile_count > 0:
                        response_text = f"I found {profile_count} {position}{'s' if profile_count != 1 else ''} on your team:"
                        for profile in profiles:
                            player_info = extract_player_info(profile)
                            if player_info:
                                players_data.append(player_info)
                    else:
                        response_text = f"I don't see any {position}s on the current roster. Would you like to see all players or search for a different position?"
                    found_position = True
                    break
            
            if not found_position:
                response_text = "I detected a position query but couldn't parse it. Try 'Who are the setters?' or 'Show all outside hitters'"
        
        # Search for player by name
        else:
            # Extract potential names from query (exclude common words and positions)
            words = query.split()
            # Enhanced stopword list includes common query words and position names
            stopwords = {'tell', 'about', 'show', 'info', 'stats', 'for', 'the', 'what', 'are', 'is', 'me', 'our', 'all', 'and', 'or', 'outside', 'setter', 'middle', 'libero', 'opposite', 'hitter', 'blockers', 'player'}
            name_candidates = [w for w in words if len(w) > 2 and w not in stopwords]
            
            if name_candidates:
                q = Q()
                for name in name_candidates:
                    q |= Q(player__first_name__icontains=name) | Q(player__last_name__icontains=name)
                
                profiles = list(PlayerProfile.objects.select_related('player', 'user').filter(q)[:5])  # Limit to 5 results
                profile_count = len(profiles)
                
                if profile_count > 0:
                    if profile_count == 1:
                        profile = profiles[0]
                        if profile and profile.player:
                            response_text = f"Found them! Here's everything I know about {profile.player.first_name} {profile.player.last_name}:"
                            player_info = extract_player_info(profile)
                            if player_info:
                                players_data.append(player_info)
                        else:
                            response_text = "Found a profile but it seems incomplete. Could you try a different search?"
                    else:
                        response_text = f"I found {profile_count} players that match! Let me show you all of them:"
                        for profile in profiles:
                            if profile and profile.player:
                                player_info = extract_player_info(profile)
                                if player_info:
                                    players_data.append(player_info)
                else:
                    response_text = "Hmm, I couldn't find anyone by that name on the roster. Could you double-check the spelling? Or if you'd like, I can show you all players - just say 'show all players'."
            else:
                response_text = "I'd love to help! You can ask me things like:\n• 'Show all players'\n• 'Tell me about player #15'\n• 'Who are the setters?'\n• Or search by any player's name!"
        
        return Response({
            'response': response_text,
            'players': players_data
        })
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        # Log with full traceback for debugging
        logger.exception(f"AI chat endpoint error: {type(e).__name__}: {str(e)}")
        return Response(
            {'error': 'An error occurred while processing your request. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def extract_player_info(profile) -> dict:
    """Extract relevant player information for AI chat response."""
    # Handle None player
    if not profile or not profile.player:
        return {
            'name': 'Unknown Player',
            'number': None,
            'position': 'Not specified',
            'height': 'Not specified',
            'summary': None,
            'stats': {
                'kills': 0,
                'blocks': 0,
                'digs': 0,
                'aces': 0
            }
        }
    
    player_info = {
        'name': f"{profile.player.first_name} {profile.player.last_name}",
        'number': profile.player.number,
        'position': profile.position or 'Not specified',
        'height': profile.height or 'Not specified',
        'summary': None,
        'stats': {}
    }
    
    # Get AI summary if exists
    try:
        ai_summary = AISummary.objects.get(player=profile)
        player_info['summary'] = ai_summary.summary
    except AISummary.DoesNotExist:
        pass
    
    # Get latest stats - always return all stat keys for consistency
    player_info['stats'] = {
        'kills': 0,
        'blocks': 0,
        'digs': 0,
        'aces': 0
    }
    latest_stats = PlayerStats.objects.filter(player=profile).order_by('-updated_at').first()
    if latest_stats:
        player_info['stats'] = {
            'kills': latest_stats.kills,
            'blocks': latest_stats.blocks,
            'digs': latest_stats.digs,
            'aces': latest_stats.aces,
        }
    
    return player_info
