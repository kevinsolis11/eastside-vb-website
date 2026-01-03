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

# Wrap with WhiteNoise for serving static files and media files
try:
    from whitenoise import WhiteNoise
    from django.conf import settings
    from pathlib import Path
    
    mimetypes = {
        '.mp4': 'video/mp4',
        '.mov': 'video/quicktime',
        '.mkv': 'video/x-matroska',
        '.webm': 'video/webm',
        '.avi': 'video/x-msvideo',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }
    
    # Create WhiteNoise app that serves static files
    application = WhiteNoise(
        application,
        root=str(settings.STATIC_ROOT),
        index_file=True,
        mimetypes=mimetypes
    )
    
    # Add media directory to WhiteNoise if it exists on Railway
    media_root = Path(settings.MEDIA_ROOT)
    if media_root.exists():
        application.add_files(str(media_root), prefix='/media/')
    
except ImportError:
    pass
