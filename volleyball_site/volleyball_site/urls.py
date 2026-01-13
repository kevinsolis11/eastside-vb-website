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
import os


def healthz(request):
    return JsonResponse({'status': 'ok'})


def user_debug(request):
    """Debug endpoint to check users on the server."""
    from django.contrib.auth.models import User
    from team.models import PlayerProfile
    
    users_info = []
    for user in User.objects.all():
        has_profile = PlayerProfile.objects.filter(user=user).exists()
        users_info.append({
            'username': user.username,
            'is_staff': user.is_staff,
            'is_active': user.is_active,
            'has_playerprofile': has_profile,
        })
    
    return JsonResponse({
        'total_users': User.objects.count(),
        'users': users_info,
    })


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
    path('user-debug/', user_debug),  # Debug endpoint for user troubleshooting
    path('video-debug/', video_debug),  # Debug endpoint for video troubleshooting
    path('signup/', signup, name='signup'),
    path('api/', include('team.api_urls')),
    path('', include('team.urls')),
]

# Serve media files - this works in BOTH debug and production modes
# This is critical for video playback on Railway
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production, use our custom serve_media view for reliable video streaming
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_media, name='serve_media'),
    ]
