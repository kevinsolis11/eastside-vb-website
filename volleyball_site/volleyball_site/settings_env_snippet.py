"""
Snippet to apply to `settings.py` to load production values from environment.

Paste the following lines near the top of your `settings.py`, replacing the
existing `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` assignments.

from os import environ

# Read sensitive/host-specific settings from environment
SECRET_KEY = environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-please-change-this-default",
)

DEBUG = environ.get("DJANGO_DEBUG", "False") == "True"

ALLOWED_HOSTS = [h for h in environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h]

# Use STATIC_ROOT for collectstatic in production
STATIC_ROOT = Path(__file__).resolve().parent.parent / "staticfiles"

"""
