#!/bin/bash
# Install Eastside Volleyball as a production-grade 24/7 service on macOS

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PLIST_FILE="$SCRIPT_DIR/com.eastsidevolleyball.server.production.plist"
INSTALL_PATH="$HOME/Library/LaunchAgents/com.eastsidevolleyball.server.production.plist"

echo "======================================"
echo "🚀 PRODUCTION SERVER INSTALLER 🚀"
echo "======================================"
echo ""

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p "$ROOT_DIR/logs"

# Check if virtual environment exists
if [ ! -d "$ROOT_DIR/.venv" ]; then
    echo "❌ Error: Virtual environment not found at $ROOT_DIR/.venv"
    echo "Please run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Check if gunicorn is installed
if ! "$ROOT_DIR/.venv/bin/python" -c "import gunicorn" 2>/dev/null; then
    echo "⚠️  Gunicorn not found. Installing..."
    "$ROOT_DIR/.venv/bin/pip" install gunicorn -q
fi

# Stop and unload existing service
echo "🛑 Stopping any existing service..."
launchctl unload "$INSTALL_PATH" 2>/dev/null || true
sleep 2

# Kill any lingering processes on port 8000
echo "🧹 Cleaning up port 8000..."
lsof -i :8000 2>/dev/null | grep -v COMMAND | awk '{print $2}' | xargs kill -9 2>/dev/null || true
sleep 2

# Install the new plist
echo "📦 Installing production service..."
cp "$PLIST_FILE" "$INSTALL_PATH"

# Load the service
echo "▶️  Starting production service..."
launchctl load "$INSTALL_PATH"

# Wait for startup
echo "⏳ Waiting for server to start (10 seconds)..."
sleep 10

# Check if service is running
if launchctl list | grep -q "com.eastsidevolleyball.server.production"; then
    echo ""
    echo "✅ ✅ ✅ SERVICE INSTALLED AND RUNNING! ✅ ✅ ✅"
    echo ""
else
    echo ""
    echo "⚠️  Service may not be running. Checking logs..."
    echo ""
fi

echo "======================================"
echo "📊 SERVICE STATUS:"
echo "======================================"
launchctl list | grep eastsidevolleyball || echo "Service not found"

echo ""
echo "======================================"
echo "🔗 URL: http://localhost:8000"
echo "======================================"
echo ""
echo "📋 USEFUL COMMANDS:"
echo ""
echo "   View server logs:"
echo "   tail -f $ROOT_DIR/logs/gunicorn_error.log"
echo ""
echo "   View startup logs:"
echo "   tail -f $ROOT_DIR/logs/launchd.log"
echo ""
echo "   Check server status:"
echo "   launchctl list | grep eastsidevolleyball"
echo ""
echo "   Restart server:"
echo "   launchctl kickstart -k gui/\$(id -u)/com.eastsidevolleyball.server.production"
echo ""
echo "   Stop server:"
echo "   launchctl unload $INSTALL_PATH"
echo ""
echo "   Start server:"
echo "   launchctl load $INSTALL_PATH"
echo ""
echo "   Uninstall completely:"
echo "   launchctl unload $INSTALL_PATH && rm $INSTALL_PATH"
echo ""
echo "======================================"
echo "🎉 Production server is now running 24/7!"
echo "======================================"
echo ""
