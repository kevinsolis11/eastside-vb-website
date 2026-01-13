"""
URL configuration for volleyball_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from team.views import CustomLoginView, signup, logout_get
from django.http import JsonResponse, FileResponse, Http404
from django.views.static import serve
from django.shortcuts import render
import os
import logging

logger = logging.getLogger('team')


# Custom error handlers
def custom_500(request):
    """Custom 500 error page with logging."""
    logger.error(f"500 error on {request.path} for user {request.user}")
    return render(request, '500.html', status=500)


def custom_404(request, exception):
    """Custom 404 error page."""
    return render(request, '404.html', status=404)


def reset_admin(request):
    """One-time endpoint to reset/create admin account. DELETE THIS AFTER USE."""
    from django.contrib.auth.models import User
    
    results = []
    
    # Create or reset admin user
    try:
        user, created = User.objects.get_or_create(username='admin')
        user.set_password('admin123')
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.email = 'admin@eastsidevb.com'
        user.save()
        results.append(f"✅ admin: {'created' if created else 'reset'} - password: admin123")
    except Exception as e:
        results.append(f"❌ admin error: {str(e)}")
    
    # Reset kevinsolis password
    try:
        user = User.objects.get(username='kevinsolis')
        user.set_password('kevin123')
        user.is_superuser = True
        user.save()
        results.append("✅ kevinsolis: password reset to kevin123")
    except User.DoesNotExist:
        results.append("⚠️ kevinsolis: not found")
    except Exception as e:
        results.append(f"❌ kevinsolis error: {str(e)}")
    
    # Reset testadmin password  
    try:
        user = User.objects.get(username='testadmin')
        user.set_password('testadmin123')
        user.is_superuser = True
        user.save()
        results.append("✅ testadmin: password reset to testadmin123")
    except User.DoesNotExist:
        results.append("⚠️ testadmin: not found")
    except Exception as e:
        results.append(f"❌ testadmin error: {str(e)}")
    
    return JsonResponse({
        'message': 'Admin accounts reset!',
        'results': results,
        'login_options': [
            {'username': 'admin', 'password': 'admin123'},
            {'username': 'kevinsolis', 'password': 'kevin123'},
            {'username': 'testadmin', 'password': 'testadmin123'},
        ],
        'admin_url': '/admin/',
        'WARNING': '⚠️ DELETE THIS ENDPOINT AFTER USE FOR SECURITY!'
    })


def dashboard_debug(request):
    """Debug the dashboard to find what's causing the 500 error."""
    import traceback
    from django.contrib.auth.models import User
    from team.models import Player, GameVideo, PlayerProfile, AccessCode, Announcement
    
    results = {'steps': []}
    
    try:
        results['steps'].append('1. Starting debug...')
        results['user'] = str(request.user)
        results['is_authenticated'] = request.user.is_authenticated
        
        if request.user.is_authenticated:
            results['is_staff'] = request.user.is_staff
            results['is_superuser'] = request.user.is_superuser
            
            results['steps'].append('2. Checking Token...')
            try:
                from rest_framework.authtoken.models import Token
                token, created = Token.objects.get_or_create(user=request.user)
                results['token'] = 'OK'
            except Exception as e:
                results['token_error'] = str(e)
            
            results['steps'].append('3. Checking counts...')
            results['player_count'] = Player.objects.count()
            results['video_count'] = GameVideo.objects.count()
            results['profile_count'] = PlayerProfile.objects.count()
            results['user_count'] = User.objects.count()
            
            results['steps'].append('4. Checking queries...')
            results['recent_videos'] = list(GameVideo.objects.order_by('-uploaded_at')[:5].values('id', 'title'))
            results['recent_players'] = list(Player.objects.order_by('-id')[:5].values('id', 'first_name'))
            results['access_codes'] = AccessCode.objects.filter(is_used=False).count()
            results['announcements'] = Announcement.objects.count()
            
            results['steps'].append('5. Testing template...')
            try:
                from django.template.loader import get_template
                template = get_template('team/coach_dashboard.html')
                results['template'] = 'OK - found'
            except Exception as e:
                results['template_error'] = str(e)
            
            results['steps'].append('6. All checks passed!')
            results['status'] = 'OK'
        else:
            results['status'] = 'Not authenticated'
    except Exception as e:
        results['error'] = str(e)
        results['traceback'] = traceback.format_exc()
    
    return JsonResponse(results)


def healthz(request):
    return JsonResponse({'status': 'ok'})


def server_status(request):
    """Comprehensive server health check for diagnosing issues."""
    import traceback
    from django.db import connection
    from django.conf import settings
    
    status = {
        'status': 'ok',
        'checks': {},
        'errors': []
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status['checks']['database'] = '✅ Connected'
    except Exception as e:
        status['checks']['database'] = f'❌ Error: {str(e)}'
        status['errors'].append(f'Database: {str(e)}')
    
    # Check media directory
    try:
        media_exists = os.path.exists(settings.MEDIA_ROOT)
        media_writable = os.access(settings.MEDIA_ROOT, os.W_OK) if media_exists else False
        status['checks']['media_root'] = f'{"✅" if media_exists else "❌"} Exists: {media_exists}, Writable: {media_writable}'
        status['checks']['media_path'] = str(settings.MEDIA_ROOT)
    except Exception as e:
        status['checks']['media_root'] = f'❌ Error: {str(e)}'
    
    # Check templates
    try:
        from django.template.loader import get_template
        get_template('base.html')
        status['checks']['templates'] = '✅ base.html found'
    except Exception as e:
        status['checks']['templates'] = f'❌ Error: {str(e)}'
        status['errors'].append(f'Templates: {str(e)}')
    
    # Check important models
    try:
        from team.models import Player, PlayerProfile, GameVideo, AccessCode
        status['checks']['models'] = {
            'players': Player.objects.count(),
            'profiles': PlayerProfile.objects.count(),
            'videos': GameVideo.objects.count(),
            'access_codes': AccessCode.objects.count(),
        }
    except Exception as e:
        status['checks']['models'] = f'❌ Error: {str(e)}'
        status['errors'].append(f'Models: {str(e)}')
    
    # Check settings
    status['checks']['debug_mode'] = settings.DEBUG
    status['checks']['railway_env'] = bool(os.environ.get('RAILWAY_ENVIRONMENT'))
    
    if status['errors']:
        status['status'] = 'error'
    
    return JsonResponse(status)


def user_debug(request):
    """Debug endpoint to check users on the server."""
    from django.contrib.auth.models import User
    from team.models import PlayerProfile, AccessCode
    import traceback
    
    try:
        users_info = []
        for user in User.objects.all():
            has_profile = PlayerProfile.objects.filter(user=user).exists()
            users_info.append({
                'username': user.username,
                'is_staff': user.is_staff,
                'is_active': user.is_active,
                'has_playerprofile': has_profile,
            })
        
        # Test AccessCode query (same as coach_codes view)
        access_codes_count = AccessCode.objects.count()
        recent_codes = list(AccessCode.objects.order_by('-created_at')[:5].values('code', 'role', 'is_used'))
        
        return JsonResponse({
            'total_users': User.objects.count(),
            'users': users_info,
            'access_codes_count': access_codes_count,
            'recent_codes': recent_codes,
            'coach_codes_test': 'OK - AccessCode query works',
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc(),
        }, status=500)


def video_debug(request):
    """Debug endpoint to check video files on the server."""
    from team.models import GameVideo
    
    videos_info = []
    for video in GameVideo.objects.all():
        file_path = os.path.join(settings.MEDIA_ROOT, video.video.name) if video.video else None
        exists = os.path.exists(file_path) if file_path else False
        file_size = os.path.getsize(file_path) if file_path and exists else 0
        
        videos_info.append({
            'id': video.pk,
            'title': video.title,
            'file_name': video.video.name if video.video else None,
            'file_url': video.video.url if video.video else None,
            'file_path_on_server': file_path,
            'file_exists': exists,
            'file_size_bytes': file_size,
            'db_size_mb': video.file_size_mb,
        })
    
    # Check media root
    media_root_exists = os.path.exists(settings.MEDIA_ROOT)
    media_root_contents = []
    if media_root_exists:
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, settings.MEDIA_ROOT)
                media_root_contents.append({
                    'path': rel_path,
                    'size': os.path.getsize(full_path)
                })
    
    return JsonResponse({
        'media_root': str(settings.MEDIA_ROOT),
        'media_root_exists': media_root_exists,
        'media_url': settings.MEDIA_URL,
        'debug_mode': settings.DEBUG,
        'videos_in_db': len(videos_info),
        'videos': videos_info,
        'files_on_disk': media_root_contents[:50],  # Limit to 50 files
    })


def serve_media(request, path):
    """
    Serve media files in production.
    This is needed because Django's static() helper only works in DEBUG mode.
    WhiteNoise should handle most requests, but this is a fallback.
    """
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        # Use FileResponse for efficient streaming of large files (videos)
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=None  # Let Django guess based on extension
        )
        # Set content type for video files
        ext = os.path.splitext(path)[1].lower()
        content_types = {
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime', 
            '.mkv': 'video/x-matroska',
            '.webm': 'video/webm',
            '.avi': 'video/x-msvideo',
            '.m4v': 'video/mp4',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
        }
        if ext in content_types:
            response['Content-Type'] = content_types[ext]
        # Allow range requests for video seeking
        response['Accept-Ranges'] = 'bytes'
        return response
    raise Http404("Media file not found")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout-get/', logout_get, name='logout_get'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('healthz/', healthz),
    path('server-status/', server_status),  # Comprehensive server health check
    path('user-debug/', user_debug),  # Debug endpoint for user troubleshooting
    path('video-debug/', video_debug),  # Debug endpoint for video troubleshooting
    path('dashboard-debug/', dashboard_debug),  # Debug dashboard 500 error
    path('reset-admin/', reset_admin),  # ONE-TIME: Reset admin passwords - DELETE AFTER USE!
    path('signup/', signup, name='signup'),
    path('api/', include('team.api_urls')),
    path('', include('team.urls')),
]

# Custom error handlers
handler500 = 'volleyball_site.urls.custom_500'
handler404 = 'volleyball_site.urls.custom_404'

# Serve media files - this works in BOTH debug and production modes
# This is critical for video playback on Railway
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production, use our custom serve_media view for reliable video streaming
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_media, name='serve_media'),
    ]
