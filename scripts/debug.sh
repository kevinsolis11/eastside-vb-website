#!/usr/bin/env bash
set -euo pipefail

# Small wrapper to run the Django development server under debugpy
# Usage: ./scripts/debug.sh [runserver-args]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON="${PYTHON:-python}"

exec "$PYTHON" -m debugpy --listen 5678 --wait-for-client "$PROJECT_ROOT/volleyball_site/manage.py" runserver "$@"
