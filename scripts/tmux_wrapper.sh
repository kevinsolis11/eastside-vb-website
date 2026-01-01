#!/bin/sh
# Wrapper script to launch tmux with pane output redirected to log files.
# Environment variables:
#   APP_ROOT - application root directory (default: /opt/volleyball_site)
#   TMUX_SESSION - tmux session name (default: evb)
#   VENV_PATH - path to virtualenv (default: $APP_ROOT/.venv)
#   LOG_DIR - directory for log files (default: $APP_ROOT/logs)

set -e

APP_ROOT="${APP_ROOT:-/opt/volleyball_site}"
TMUX_SESSION="${TMUX_SESSION:-evb}"
VENV_PATH="${VENV_PATH:-$APP_ROOT/.venv}"
LOG_DIR="${LOG_DIR:-$APP_ROOT/logs}"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"
cd "$APP_ROOT" || exit 1

# Kill existing session if it exists
if /usr/bin/tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
  /usr/bin/tmux kill-session -t "$TMUX_SESSION"
fi

# Create new tmux session
/usr/bin/tmux new-session -d -s "$TMUX_SESSION" -c "$APP_ROOT"

# Pane 0: Django dev server (web)
/usr/bin/tmux send-keys -t "$TMUX_SESSION:0.0" \
  "$VENV_PATH/bin/python volleyball_site/manage.py runserver 127.0.0.1:8000 >> '$LOG_DIR/web.log' 2>&1" C-m

# Split horizontally for worker
/usr/bin/tmux split-window -h -t "$TMUX_SESSION" -c "$APP_ROOT"

# Pane 1: Celery worker
/usr/bin/tmux send-keys -t "$TMUX_SESSION:0.1" \
  "$VENV_PATH/bin/celery -A volleyball_site worker --loglevel=info >> '$LOG_DIR/celery-worker.log' 2>&1" C-m

# Select left pane and split vertically for beat
/usr/bin/tmux select-pane -t "$TMUX_SESSION:0.0"
/usr/bin/tmux split-window -v -t "$TMUX_SESSION:0.0" -c "$APP_ROOT"

# Pane 2: Celery beat
/usr/bin/tmux send-keys -t "$TMUX_SESSION:0.2" \
  "$VENV_PATH/bin/celery -A volleyball_site beat --loglevel=info >> '$LOG_DIR/celery-beat.log' 2>&1" C-m

# Layout
/usr/bin/tmux select-layout -t "$TMUX_SESSION" tiled

echo "tmux session '$TMUX_SESSION' started with panes redirected to $LOG_DIR"
exit 0
