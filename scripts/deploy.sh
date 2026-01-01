#!/bin/bash
# Quick production deployment script for Eastside VB Website
# Usage: sudo ./scripts/deploy.sh [--user volleyball] [--group volleyball]
# Assumes: repo is cloned, script is in scripts/ folder

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Parse arguments
RUN_USER="volleyball"
RUN_GROUP="volleyball"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --user) shift; RUN_USER="$1"; shift ;;
    --user=*) RUN_USER="${1#--user=}"; shift ;;
    --group) shift; RUN_GROUP="$1"; shift ;;
    --group=*) RUN_GROUP="${1#--group=}"; shift ;;
    *) log_error "Unknown option: $1"; exit 1 ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PATH="$REPO_ROOT/.venv"
MANAGE_PY="$REPO_ROOT/volleyball_site/manage.py"

log_info "Starting production deployment from $REPO_ROOT"

# Step 1: Ensure venv exists
if [ ! -d "$VENV_PATH" ]; then
  log_info "Creating virtualenv..."
  python3 -m venv "$VENV_PATH"
  "$VENV_PATH/bin/python" -m pip install --upgrade pip setuptools wheel
  "$VENV_PATH/bin/python" -m pip install -r "$REPO_ROOT/volleyball_site/requirements.txt"
else
  log_info "Virtualenv already exists, updating packages..."
  "$VENV_PATH/bin/python" -m pip install --upgrade -r "$REPO_ROOT/volleyball_site/requirements.txt"
fi

# Step 2: Run migrations
log_info "Running migrations..."
"$VENV_PATH/bin/python" "$MANAGE_PY" migrate --noinput

# Step 3: Collect static files
log_info "Collecting static files..."
"$VENV_PATH/bin/python" "$MANAGE_PY" collectstatic --noinput

# Step 4: Create periodic cleanup task
log_info "Creating periodic cleanup task..."
"$VENV_PATH/bin/python" "$MANAGE_PY" create_cleanup_periodic || log_warn "Periodic task creation failed (may already exist)"

# Step 5: Install systemd services
log_info "Installing systemd services as $RUN_USER:$RUN_GROUP..."
if [ ! -f /etc/default/volleyball_site.env ]; then
  log_info "Copying environment template to /etc/default/volleyball_site.env..."
  sudo cp "$REPO_ROOT/deployment/volleyball_site.env.example" /etc/default/volleyball_site.env
  sudo chmod 640 /etc/default/volleyball_site.env
  sudo chown "$RUN_USER:$RUN_GROUP" /etc/default/volleyball_site.env
else
  log_warn "/etc/default/volleyball_site.env already exists, not overwriting"
fi

log_info "Installing systemd units..."
sudo "$REPO_ROOT/deployment/install_systemd.sh" --force --user "$RUN_USER" --group "$RUN_GROUP"

# Step 6: Start services
log_info "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable evb-tmux-logs.service || true
sudo systemctl start evb-tmux-logs.service

# Verification
log_info "Waiting for services to start..."
sleep 3

if pgrep -f "runserver" > /dev/null; then
  log_info "✓ Web server is running"
else
  log_error "✗ Web server is NOT running"
fi

if pgrep -f "celery.*worker" > /dev/null; then
  log_info "✓ Celery worker is running"
else
  log_error "✗ Celery worker is NOT running"
fi

if pgrep -f "celery.*beat" > /dev/null; then
  log_info "✓ Celery beat is running"
else
  log_error "✗ Celery beat is NOT running"
fi

# Test healthcheck
if curl -s http://127.0.0.1:8000/healthz/ | grep -q "OK"; then
  log_info "✓ Healthcheck endpoint responding"
else
  log_warn "✗ Healthcheck endpoint not responding (may need a moment)"
fi

log_info ""
log_info "=== Deployment Complete ==="
log_info ""
log_info "Next steps:"
log_info "1. View logs: tail -f $REPO_ROOT/logs/web.log"
log_info "2. Verify status: sudo systemctl status evb-tmux-logs.service"
log_info "3. Configure Nginx (see PRODUCTION_DEPLOY.md)"
log_info "4. Set up SSL with Let's Encrypt"
log_info ""
log_info "For issues, check: sudo journalctl -u evb-tmux-logs.service -n 50"
