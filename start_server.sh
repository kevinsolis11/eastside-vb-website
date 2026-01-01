#!/bin/bash

# Eastside Volleyball Server Startup Script
# This script runs the Django server in a stable way

cd "/Users/klaysolis/eastside vb website/volleyball_site"

# Set environment variables
export PYTHONUNBUFFERED=1
export DJANGO_SETTINGS_MODULE=volleyball_site.settings

# Ensure database migrations are applied
echo "📦 Applying database migrations..."
"/Users/klaysolis/eastside vb website/.venv/bin/python" manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
"/Users/klaysolis/eastside vb website/.venv/bin/python" manage.py collectstatic --noinput

# Start server with Gunicorn (more stable than runserver)
echo "🚀 Starting server on http://127.0.0.1:8000"
exec "/Users/klaysolis/eastside vb website/.venv/bin/gunicorn" \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --threads 2 \
    --worker-class gthread \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    volleyball_site.wsgi:application
