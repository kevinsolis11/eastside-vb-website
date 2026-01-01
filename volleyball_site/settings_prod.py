# Django Production Settings Template
# Copy this to volleyball_site/settings_prod.py and set environment variables
# Usage in manage.py or wsgi.py:
#   import os
#   if os.getenv('DJANGO_ENV') == 'production':
#       from volleyball_site.settings_prod import *
#   else:
#       from volleyball_site.settings import *

import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings - MUST be configured
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', get_random_secret_key())
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'

# HTTPS/SSL settings
SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL_REDIRECT', 'True').lower() == 'true'
SESSION_COOKIE_SECURE = os.getenv('DJANGO_SESSION_COOKIE_SECURE', 'True').lower() == 'true'
CSRF_COOKIE_SECURE = os.getenv('DJANGO_CSRF_COOKIE_SECURE', 'True').lower() == 'true'
SECURE_HSTS_SECONDS = int(os.getenv('DJANGO_SECURE_HSTS_SECONDS', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True').lower() == 'true'
SECURE_HSTS_PRELOAD = os.getenv('DJANGO_SECURE_HSTS_PRELOAD', 'True').lower() == 'true'

# Email configuration
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', f'noreply@{ALLOWED_HOSTS[0] if ALLOWED_HOSTS else "example.com"}')
DEFAULT_FROM_NAME = os.getenv('DEFAULT_FROM_NAME', 'Eastside Volleyball')
DEFAULT_REPLY_TO = os.getenv('DEFAULT_REPLY_TO', DEFAULT_FROM_EMAIL)

# Database - use environment variables
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', ''),
    }
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': os.getenv('CACHE_BACKEND', 'django.core.cache.backends.redis.RedisCache'),
        'LOCATION': os.getenv('CACHE_LOCATION', 'redis://127.0.0.1:6379/1'),
    }
}

# Celery configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Static and media files
STATIC_ROOT = os.getenv('STATIC_ROOT', os.path.join(BASE_DIR, 'staticfiles'))
STATIC_URL = '/static/'
MEDIA_ROOT = os.getenv('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))
MEDIA_URL = '/media/'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, '..', 'logs', 'django.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': os.getenv('CELERY_LOG_LEVEL', 'INFO'),
        },
    },
}

# Security - headers
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Allowed redirect hosts
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'https://' + ',https://'.join(ALLOWED_HOSTS)).split(',') if ALLOWED_HOSTS else []
