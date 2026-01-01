#!/bin/bash
set -e

cd volleyball_site

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
gunicorn \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 4 \
  --worker-class sync \
  --max-requests 1000 \
  --timeout 60 \
  volleyball_site.wsgi:application
