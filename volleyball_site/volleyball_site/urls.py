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
