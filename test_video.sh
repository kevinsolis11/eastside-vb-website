#!/bin/bash
# Video Playback Test Script

echo "════════════════════════════════════════════════════════════════"
echo "VIDEO PLAYBACK TEST"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if video file exists
VIDEO_FILE="/Users/klaysolis/eastside vb website/volleyball_site/media/videos/2025/12/ScreenRecording_12-25-2025_21-58-04_1.mp4"

echo "1. CHECK FILE EXISTS"
if [ -f "$VIDEO_FILE" ]; then
    echo "✓ Video file found: $VIDEO_FILE"
    SIZE=$(ls -lh "$VIDEO_FILE" | awk '{print $5}')
    echo "  File size: $SIZE"
else
    echo "✗ Video file NOT found"
    exit 1
fi

echo ""
echo "2. CHECK FILE PERMISSIONS"
if [ -r "$VIDEO_FILE" ]; then
    echo "✓ File is readable"
else
    echo "✗ File is NOT readable"
    exit 1
fi

echo ""
echo "3. CHECK VIDEO FILE FORMAT"
file "$VIDEO_FILE"

echo ""
echo "4. CHECK FFMPEG CAN READ IT"
which ffmpeg > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ ffmpeg is installed"
    echo "  Checking video codec..."
    ffmpeg -i "$VIDEO_FILE" 2>&1 | grep -E "Video:|Duration:" | head -2
else
    echo "⚠ ffmpeg not installed (video should still play in browser)"
fi

echo ""
echo "5. CHECK SERVER IS RUNNING"
curl -s http://localhost:8000/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Django server is running at http://localhost:8000"
else
    echo "✗ Django server NOT responding"
    exit 1
fi

echo ""
echo "6. CHECK VIDEO URL IS ACCESSIBLE"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/media/videos/2025/12/ScreenRecording_12-25-2025_21-58-04_1.mp4)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Video URL accessible (HTTP $HTTP_CODE)"
    echo "  URL: http://localhost:8000/media/videos/2025/12/ScreenRecording_12-25-2025_21-58-04_1.mp4"
else
    echo "✗ Video URL NOT accessible (HTTP $HTTP_CODE)"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ VIDEO IS READY TO PLAY"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "NEXT STEPS:"
echo "1. Open http://localhost:8000/ in your browser"
echo "2. Log in as coach (kevinsolis / admin123)"
echo "3. Go to 'Videos' or 'View Videos'"
echo "4. Click on 'volleyball game' video"
echo "5. Video should play in the browser"
echo ""
