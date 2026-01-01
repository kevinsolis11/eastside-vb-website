#!/bin/bash
# Install the Eastside Volleyball server as a macOS LaunchAgent

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PLIST_FILE="$SCRIPT_DIR/com.eastsidevolleyball.server.plist"
INSTALL_PATH="$HOME/Library/LaunchAgents/com.eastsidevolleyball.server.plist"

echo "======================================"
echo "Eastside Volleyball Server Installer"
echo "======================================"

# Create logs directory
echo "Creating logs directory..."
mkdir -p "$ROOT_DIR/logs"

# Check if virtual environment exists
if [ ! -d "$ROOT_DIR/.venv" ]; then
    echo "Error: Virtual environment not found at $ROOT_DIR/.venv"
    echo "Please run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Stop existing service if running
echo "Stopping existing service (if any)..."
launchctl unload "$INSTALL_PATH" 2>/dev/null || true

# Copy plist file
echo "Installing service..."
cp "$PLIST_FILE" "$INSTALL_PATH"

# Load the service
echo "Starting service..."
launchctl load "$INSTALL_PATH"

echo ""
echo "✅ Service installed successfully!"
echo ""
echo "The Django server is now running as a background service."
echo "It will automatically start on boot and restart if it crashes."
echo ""
echo "Useful commands:"
echo "  • View logs:        tail -f $ROOT_DIR/logs/server.log"
echo "  • View errors:      tail -f $ROOT_DIR/logs/server.error.log"
echo "  • Stop service:     launchctl unload $INSTALL_PATH"
echo "  • Start service:    launchctl load $INSTALL_PATH"
echo "  • Restart service:  launchctl kickstart -k gui/\$(id -u)/com.eastsidevolleyball.server"
echo "  • Check status:     launchctl list | grep eastsidevolleyball"
echo "  • Uninstall:        launchctl unload $INSTALL_PATH && rm $INSTALL_PATH"
echo ""
echo "Server URL: http://localhost:8000"
echo ""
