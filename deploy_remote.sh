#!/usr/bin/env bash
set -euo pipefail

# Remote deploy helper. Run on the remote host as the deploy user (will use sudo for system-level steps).
# Usage on remote: sudo bash /tmp/deploy_remote.sh /tmp/volleyball_site_deploy.tar.gz

TARBALL=${1:-/tmp/volleyball_site_deploy.tar.gz}
DEPLOY_PATH=/home/ubuntu/volleyball_site
VENV_PATH="$DEPLOY_PATH/.venv"
GUNICORN_SOCKET="$DEPLOY_PATH/gunicorn.sock"
SERVICE_NAME=gunicorn

if [ ! -f "$TARBALL" ]; then
  echo "Tarball $TARBALL not found."
  exit 1
fi

# extract to /tmp then move into place
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

echo "Extracting $TARBALL to $TMPDIR"
tar -xzf "$TARBALL" -C "$TMPDIR"

# The tar should contain a top-level 'volleyball_site' folder
if [ -d "$DEPLOY_PATH" ]; then
  echo "Removing existing $DEPLOY_PATH"
  sudo rm -rf "$DEPLOY_PATH"
fi

sudo mv "$TMPDIR/volleyball_site" "$DEPLOY_PATH"

# Ensure python3 and venv exist
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found on remote. Install Python3 and retry."
  exit 1
fi

# create venv
if [ ! -d "$VENV_PATH" ]; then
  echo "Creating virtualenv at $VENV_PATH"
  python3 -m venv "$VENV_PATH"
fi

# install deps
echo "Installing requirements"
sudo "$VENV_PATH/bin/pip" install --upgrade pip
sudo "$VENV_PATH/bin/pip" install -r "$DEPLOY_PATH/requirements.txt"

# run migrations and collectstatic
echo "Running migrations and collectstatic"
cd "$DEPLOY_PATH"
sudo "$VENV_PATH/bin/python" manage.py migrate --noinput
sudo "$VENV_PATH/bin/python" manage.py collectstatic --noinput

# Install systemd service
if [ -f "$DEPLOY_PATH/deployment/gunicorn.service" ]; then
  echo "Installing systemd service"
  sudo mv "$DEPLOY_PATH/deployment/gunicorn.service" /etc/systemd/system/gunicorn.service
  sudo systemctl daemon-reload
  sudo systemctl enable --now gunicorn.service
  sudo systemctl restart gunicorn.service || true
  sudo systemctl status --no-pager gunicorn.service
else
  echo "Service file not found in $DEPLOY_PATH/deployment/gunicorn.service"
fi

echo "Deploy complete."
