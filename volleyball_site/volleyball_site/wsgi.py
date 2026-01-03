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

# Wrap with WhiteNoise for serving static files (and media via Django)
try:
    from whitenoise import WhiteNoise
    from django.conf import settings
    
    application = WhiteNoise(
        application,
        root=str(settings.STATIC_ROOT),
        index_file=True,
        mimetypes={
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.mkv': 'video/x-matroska',
            '.webm': 'video/webm',
            '.avi': 'video/x-msvideo'
        }
    )
except ImportError:
    pass
