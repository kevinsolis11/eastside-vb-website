#!/bin/bash
# Check production server status

echo ""
echo "======================================"
echo "🔍 SERVER STATUS CHECK"
echo "======================================"
echo ""

# Check if service is loaded
if launchctl list | grep -q "com.eastsidevolleyball.server.production"; then
    echo "✅ Service is loaded in launchd"
else
    echo "❌ Service is NOT loaded"
fi

# Check if processes are running
PROCESS_COUNT=$(ps aux | grep gunicorn | grep -v grep | wc -l)
if [ $PROCESS_COUNT -gt 0 ]; then
    echo "✅ Gunicorn processes running: $PROCESS_COUNT (1 master + 3-4 workers)"
else
    echo "❌ No Gunicorn processes found"
fi

# Check if port 8000 is listening
if lsof -i :8000 >/dev/null 2>&1; then
    echo "✅ Port 8000 is listening"
else
    echo "❌ Port 8000 is NOT listening"
fi

# Try to reach the server
echo ""
echo "Testing server response..."
RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000 2>&1 | tail -1)
if [ "$RESPONSE" == "302" ] || [ "$RESPONSE" == "200" ] || [ "$RESPONSE" == "301" ]; then
    echo "✅ Server is responding (HTTP $RESPONSE)"
else
    echo "⚠️  Server response: $RESPONSE"
fi

echo ""
echo "======================================"
echo "📊 PROCESS DETAILS:"
echo "======================================"
ps aux | grep gunicorn | grep -v grep | head -1

echo ""
echo "======================================"
echo "📋 RECENT LOGS:"
echo "======================================"
echo "Last 5 lines of error log:"
tail -5 "/Users/klaysolis/eastside vb website/logs/gunicorn_error.log" 2>/dev/null || echo "No errors logged"

echo ""
echo "======================================"
echo "🌐 ACCESS:"
echo "======================================"
echo "URL: http://localhost:8000"
echo "Admin: http://localhost:8000/admin/"
echo ""
