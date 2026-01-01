#!/bin/bash
# Production-grade startup script for Eastside Volleyball Django server
# This script:
# - Kills any existing processes on port 8000
# - Waits for the port to be free
# - Collects static files
# - Runs database migrations
# - Starts Gunicorn with 4 worker processes
# - Has automatic restart on crash

set -e

ROOT_DIR="/Users/klaysolis/eastside vb website"
VENV_PATH="$ROOT_DIR/.venv"
APP_DIR="$ROOT_DIR/volleyball_site"
LOG_DIR="$ROOT_DIR/logs"
PORT=8000

# Ensure logs directory exists
mkdir -p "$LOG_DIR"

# Kill any existing processes on the port
echo "[$(date)] Cleaning up port $PORT..."
lsof -i :$PORT 2>/dev/null | grep -v COMMAND | awk '{print $2}' | xargs kill -9 2>/dev/null || true

# Wait for port to be free
echo "[$(date)] Waiting for port to be free..."
for i in {1..10}; do
  if ! lsof -i :$PORT >/dev/null 2>&1; then
    echo "[$(date)] Port is free!"
    break
  fi
  echo "[$(date)] Port still in use, waiting... ($i/10)"
  sleep 1
done

# Navigate to app directory
cd "$APP_DIR" || exit 1

# Activate virtual environment
export PATH="$VENV_PATH/bin:$PATH"

# Run migrations
echo "[$(date)] Running database migrations..."
python manage.py migrate --noinput 2>&1 | tee -a "$LOG_DIR/startup.log"

# Collect static files
echo "[$(date)] Collecting static files..."
python manage.py collectstatic --noinput 2>&1 | tee -a "$LOG_DIR/startup.log"

# Start Gunicorn with proper configuration
echo "[$(date)] Starting Gunicorn server..."
exec gunicorn \
  --bind 0.0.0.0:$PORT \
  --workers 4 \
  --worker-class sync \
  --worker-connections 100 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --timeout 60 \
  --access-logfile "$LOG_DIR/gunicorn_access.log" \
  --error-logfile "$LOG_DIR/gunicorn_error.log" \
  --log-level info \
  volleyball_site.wsgi:application
