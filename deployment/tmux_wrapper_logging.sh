#!/usr/bin/env bash
set -euo pipefail

# Wrapper to create a tmux session running the webserver, celery worker, and beat
# Each pane's output is piped to a log file under LOG_DIR.
# Expects optional /etc/default/volleyball_site.env to set APP_ROOT, VENV_PATH, TMUX_SESSION

ENV_FILE=/etc/default/volleyball_site.env
if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC1090
  . "$ENV_FILE" || true
fi

APP_ROOT="${APP_ROOT:-/opt/volleyball_site}"
VENV_PATH="${VENV_PATH:-$APP_ROOT/.venv}"
TMUX_SESSION="${TMUX_SESSION:-evb}"
LOG_DIR="${LOG_DIR:-$APP_ROOT/logs}"

mkdir -p "$LOG_DIR"
chmod 750 "$LOG_DIR"

echo "Starting tmux session '$TMUX_SESSION' with logs in $LOG_DIR"

# Kill any existing session to ensure clean logs
/usr/bin/tmux kill-session -t "$TMUX_SESSION" 2>/dev/null || true

# Start web server in pane 0
/usr/bin/tmux new-session -d -s "$TMUX_SESSION" -c "$APP_ROOT" \
  "bash -lc '$VENV_PATH/bin/python volleyball_site/manage.py runserver 127.0.0.1:8000 2>&1 | tee -a $LOG_DIR/web.log'"

# Worker in right pane
/usr/bin/tmux split-window -h -t "$TMUX_SESSION" -c "$APP_ROOT" \
  "bash -lc '$VENV_PATH/bin/celery -A volleyball_site worker --loglevel=info 2>&1 | tee -a $LOG_DIR/worker.log'"

# Beat in pane below left
/usr/bin/tmux select-pane -t "$TMUX_SESSION":0.0
/usr/bin/tmux split-window -v -t "$TMUX_SESSION":0.0 -c "$APP_ROOT" \
  "bash -lc '$VENV_PATH/bin/celery -A volleyball_site beat --loglevel=info 2>&1 | tee -a $LOG_DIR/beat.log'"

/usr/bin/tmux select-layout -t "$TMUX_SESSION" tiled

echo "tmux session '$TMUX_SESSION' started. Logs:"
echo "  $LOG_DIR/web.log"
echo "  $LOG_DIR/worker.log"
echo "  $LOG_DIR/beat.log"

exit 0
