#!/bin/sh
set -e

# Helper to install systemd units and example env file for volleyball_site
# Usage: sudo ./deployment/install_systemd.sh [--force] [--user USER]
# If --force is passed, existing /etc/default/volleyball_site.env will be overwritten.
# If --user is provided, the script will chown the env file to that user and
# create systemd drop-in override files that set `User=` for the services.

ENV_SRC="$(pwd)/deployment/volleyball_site.env.example"
ENV_DEST="/etc/default/volleyball_site.env"
SERVICES_DIR="/etc/systemd/system"

FORCE=0
RUN_AS_USER=""
RUN_AS_GROUP=""

usage() {
  echo "Usage: sudo $0 [--force] [--user USER]" >&2
  exit 1
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --force)
      FORCE=1; shift ;;
    --user)
      shift; if [ -z "$1" ]; then usage; fi; RUN_AS_USER="$1"; shift ;;
    --user=*) RUN_AS_USER="${1#--user=}"; shift ;;
    --group)
      shift; if [ -z "$1" ]; then usage; fi; RUN_AS_GROUP="$1"; shift ;;
    --group=*) RUN_AS_GROUP="${1#--group=}"; shift ;;
    -h|--help) usage ;;
    *) echo "Unknown arg: $1"; usage ;;
  esac
done

if [ -f "$ENV_DEST" ] && [ "$FORCE" -ne 1 ]; then
  echo "Env file $ENV_DEST already exists. Refusing to overwrite." >&2
  echo "Rerun with --force to overwrite, or edit $ENV_DEST manually." >&2
  exit 1
fi

echo "Copying example env to $ENV_DEST"
cp "$ENV_SRC" "$ENV_DEST"
chmod 640 "$ENV_DEST"

if [ -n "$RUN_AS_USER" ]; then
  echo "Setting ownership of $ENV_DEST to $RUN_AS_USER"
  chown "$RUN_AS_USER":"$RUN_AS_USER" "$ENV_DEST" || true
fi

# Source the copied env file to read APP_ROOT/VENV_PATH if present
# shellcheck disable=SC1090
if [ -f "$ENV_DEST" ]; then
  # allow failures if the env file doesn't set expected vars
  . "$ENV_DEST" || true
fi
APP_ROOT="${APP_ROOT:-/opt/volleyball_site}"
VENV_PATH="${VENV_PATH:-$APP_ROOT/.venv}"

echo "Copying systemd service files to $SERVICES_DIR"
cp deployment/*.service "$SERVICES_DIR/"

echo "Copying wrapper scripts to $APP_ROOT/scripts"
mkdir -p "$APP_ROOT/scripts"
cp scripts/tmux_wrapper.sh "$APP_ROOT/scripts/"
chmod 755 "$APP_ROOT/scripts/tmux_wrapper.sh"

if [ -n "$RUN_AS_USER" ]; then
  echo "Setting ownership of $APP_ROOT/scripts to $RUN_AS_USER"
  chown -R "$RUN_AS_USER:${RUN_AS_GROUP:-$RUN_AS_USER}" "$APP_ROOT/scripts" || true
fi

if [ -n "$RUN_AS_USER" ]; then
  echo "Creating systemd drop-in override files to run services as $RUN_AS_USER"
  for svc in evb-tmux.service evb-tmux-logs.service gunicorn.service celery.service celery-beat.service; do
    dir="$SERVICES_DIR/$svc.d"
    mkdir -p "$dir"
    echo "Writing override for $svc -> $dir/override.conf"
    if [ -n "$RUN_AS_GROUP" ]; then
      cat > "$dir/override.conf" <<EOF
[Service]
User=$RUN_AS_USER
Group=$RUN_AS_GROUP
WorkingDirectory=$APP_ROOT
EnvironmentFile=$ENV_DEST
EOF
    else
      cat > "$dir/override.conf" <<EOF
[Service]
User=$RUN_AS_USER
WorkingDirectory=$APP_ROOT
EnvironmentFile=$ENV_DEST
EOF
    fi
  done
fi

echo "Reloading systemd daemon and enabling services"
systemctl daemon-reload
systemctl enable --now gunicorn.service || true
systemctl enable --now celery.service || true
systemctl enable --now celery-beat.service || true
systemctl enable --now evb-tmux.service || true
systemctl enable --now evb-tmux-logs.service || true

echo "All done. Check service status with:"
echo "  systemctl status gunicorn.service"
echo "  systemctl status celery.service"
echo "  systemctl status celery-beat.service"
echo "  systemctl status evb-tmux.service"
echo "  systemctl status evb-tmux-logs.service"
echo ""
echo "View logs with:"
echo "  tail -f $APP_ROOT/logs/web.log"
echo "  tail -f $APP_ROOT/logs/celery-worker.log"
echo "  tail -f $APP_ROOT/logs/celery-beat.log"

exit 0
