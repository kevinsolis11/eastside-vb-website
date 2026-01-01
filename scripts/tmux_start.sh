#!/bin/sh
# Start a tmux session with panes for Django dev server, Celery worker, and Celery beat.
# Usage: ./scripts/tmux_start.sh

SESSION="evb"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux is not installed. Install tmux to use this script." >&2
  exit 1
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "Session '$SESSION' already exists. Attaching..."
  exec tmux attach -t "$SESSION"
fi

echo "Creating tmux session '$SESSION'..."
tmux new-session -d -s "$SESSION" -c "$ROOT_DIR"
tmux rename-window -t "$SESSION:0" web

# Pane 0: Django dev server
tmux send-keys -t "$SESSION:0.0" ".venv/bin/python volleyball_site/manage.py runserver 127.0.0.1:8000" C-m

# Split horizontally for worker
tmux split-window -h -t "$SESSION:0" -c "$ROOT_DIR"
tmux send-keys -t "$SESSION:0.1" ".venv/bin/celery -A volleyball_site worker --loglevel=info" C-m

# Create a pane below the left pane for beat
tmux select-pane -t "$SESSION:0.0"
tmux split-window -v -t "$SESSION:0.0" -c "$ROOT_DIR"
tmux send-keys -t "$SESSION:0.2" ".venv/bin/celery -A volleyball_site beat --loglevel=info" C-m

tmux select-layout -t "$SESSION" tiled

echo "Attaching to session '$SESSION'"
exec tmux attach -t "$SESSION"
