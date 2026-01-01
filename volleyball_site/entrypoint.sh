#!/bin/sh
set -e

# Run migrations (including django_celery_beat)
echo "Running migrations..."
python manage.py migrate --noinput

echo "Ensuring periodic task exists (create_cleanup_periodic)..."
python manage.py create_cleanup_periodic || true

exec "$@"
