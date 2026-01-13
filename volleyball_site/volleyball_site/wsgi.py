"""
WSGI config for volleyball_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'volleyball_site.settings')

application = get_wsgi_application()

# Wrap with WhiteNoise for serving static AND media files
# This is essential for Railway deployment where media files need to be served
try:
    from whitenoise import WhiteNoise
    from django.conf import settings
    
    # Custom mimetypes for video files
    video_mimetypes = {
        '.mp4': 'video/mp4',
        '.mov': 'video/quicktime',
        '.mkv': 'video/x-matroska',
        '.webm': 'video/webm',
        '.avi': 'video/x-msvideo',
        '.m4v': 'video/mp4',
    }
    
    # First wrap for static files
    application = WhiteNoise(
        application,
        root=str(settings.STATIC_ROOT),
        index_file=True,
        mimetypes=video_mimetypes
    )
    
    # CRITICAL: Also add media files to WhiteNoise for production serving
    # This fixes the video loading issue on Railway
    media_root = str(settings.MEDIA_ROOT)
    if os.path.isdir(media_root):
        application.add_files(media_root, prefix=settings.MEDIA_URL)
        
except ImportError:
    pass
