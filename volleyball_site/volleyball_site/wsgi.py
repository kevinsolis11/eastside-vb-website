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

# Add WhiteNoise middleware to serve static and media files in production
try:
    from whitenoise import WhiteNoise
    from django.conf import settings
    
    # Serve both static and media files
    application = WhiteNoise(
        application,
        root=str(settings.STATIC_ROOT),
        index_file=True,
        mimetypes={'.mp4': 'video/mp4', '.mov': 'video/quicktime', '.mkv': 'video/x-matroska'}
    )
    
    # Also add media directory if it exists
    if settings.MEDIA_ROOT:
        application.add_files(str(settings.MEDIA_ROOT), prefix='/media/')
except ImportError:
    pass
