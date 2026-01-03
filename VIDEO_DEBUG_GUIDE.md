# 🎥 Video Upload Debugging Guide

## Overview

The video upload system now includes comprehensive debugging information to help troubleshoot issues on Railway. Every video upload is logged and tracked from upload through conversion to playback.

## What Gets Logged

### 1. **Upload Event Logging**
When a coach uploads a video, the system captures:
- ✅ Coach username who uploaded
- ✅ Video filename and format
- ✅ File size (MB)
- ✅ Upload timestamp
- ✅ Video ID in database

### 2. **Conversion Status Tracking** 
Every uploaded video gets a `VideoConversionLog` entry tracking:
- **Status**: Pending → Processing → Success/Failed/Skipped
- **Original Format**: MP4, MOV, MKV, AVI, WebM
- **File Sizes**: Original and converted sizes
- **Compression Ratio**: How much smaller the MP4 is
- **Task ID**: Celery task UUID for tracking background jobs
- **Timestamps**: When conversion started/completed
- **Error Messages**: Detailed error if conversion fails
- **Debug Log**: Complete ffmpeg output for troubleshooting

### 3. **Railway Web Service Logs**
All operations are logged to Railway's logging system. To view:
1. Go to https://railway.app/dashboard
2. Click your project
3. Select "web" service
4. Click "Logs" tab
5. Search for:
   - `✅ Video uploaded:` - Video upload events
   - `🎬 Starting video conversion` - Conversion started
   - `❌` - Errors
   - `✓ Celery task queued` - Task queued successfully

## Using the Debug Interface

### On Video List Page (`/team/videos/`)
Each video card shows a conversion status badge:

- 🔄 **Converting...** (yellow) - Video is being converted to MP4
- ✅ **Ready** (green) - Video converted successfully and ready to play
- ❌ **Conversion Failed** (red) - Conversion failed, check details
- ℹ️ **MP4** (blue) - Video was already MP4, no conversion needed

### On Video Detail Page (`/team/videos/<id>/`)
Click on any video to see comprehensive debug information:

#### Conversion Status Panel Shows:
- **Status Badge**: Current state of conversion
- **Original Format**: What format the video was uploaded in
- **File Sizes**: Original and converted sizes
- **Compression**: How much space was saved (%)
- **Task ID**: Celery task identifier
- **Timestamps**: When conversion started and finished
- **Error Details**: If conversion failed, the exact error
- **📋 Debug Log**: Expandable detailed log with ffmpeg output

#### Example Debug Log Output:
```
📹 Video uploaded by kevinsolis
Filename: ScreenRecording_12-25-2025_21-58-04_1.mov
Format: MOV
Size: 14.1 MB
Timestamp: 2025-01-03T15:30:45.123456+00:00

🔄 Celery task queued
Task ID: abc123def456ghi789jkl012mno345pqr
Scheduled: 2025-01-03T15:30:46.234567+00:00

🎬 Conversion started at 2025-01-03T15:30:47.345678+00:00

✅ Conversion completed successfully
Output file size: 7.4 MB
Compression: 47.5% reduction
Completed at: 2025-01-03T15:31:12.456789+00:00
```

## Common Issues & Solutions

### Issue: "🔄 Converting..." badge stuck forever
**Cause**: Celery worker not running on Railway
**Solution**: 
1. Check Railway dashboard → worker service status
2. Ensure `Procfile` has worker process defined
3. Check worker logs for errors

### Issue: "❌ Conversion Failed"
**Possible Causes**:
1. **ffmpeg not installed**: Check if nixpacks.toml exists
2. **File permissions**: Video file not readable
3. **Disk space**: No space to write converted file
4. **ffmpeg crash**: Check debug log for error details

**Solution**:
1. Click "Conversion Failed" badge to expand details
2. Read the "📋 Detailed Debug Log" 
3. Common errors:
   - `ffmpeg: command not found` → Add ffmpeg to nixpacks.toml
   - `Permission denied` → Check media directory permissions
   - `No space left on device` → Clear old files or increase storage

### Issue: Video won't play after "Ready" status
**Cause**: MP4 file might be corrupted
**Solution**:
1. Download the converted MP4 file from debug panel
2. Test locally with: `ffmpeg -i videos/converted.mp4`
3. If corrupted, delete and re-upload

## Monitoring Videos on Railway

### Step 1: Deploy Latest Code
```bash
git push origin main
# Railway auto-deploys within 1 minute
```

### Step 2: Upload a Test Video
1. Go to https://eastside-vb-website-production.up.railway.app
2. Login with: kevinsolis / admin123
3. Go to Coach Dashboard → Upload Video
4. Choose a non-MP4 file (MOV, MKV, etc.)

### Step 3: Check Status
- **Immediately**: Badge shows "🔄 Converting..."
- **Click video**: See conversion started timestamp
- **Wait 30 seconds**: Badge updates to ✅ or ❌
- **Full debug log**: Click "Detailed Debug Log" to expand

### Step 4: Check Railway Logs
1. https://railway.app/dashboard
2. Select "web" service
3. Click "Logs"
4. Search for video ID:
   ```
   Video ID: 12
   ```

## Debug Fields in Database

The `VideoConversionLog` model tracks:

```
- video (ForeignKey) - The GameVideo being converted
- status - One of: pending, processing, success, failed, skipped
- original_filename - Name of uploaded file
- original_format - MOV, MKV, MP4, etc.
- original_size_mb - File size in MB
- converted_size_mb - Final MP4 size
- celery_task_id - Background job ID
- error_message - Error if failed
- debug_log - Complete conversion log
- started_at - When conversion started
- completed_at - When it finished
- created_at - When record created
- updated_at - Last update time
```

## For Coaches: How to Troubleshoot

When a video upload fails:

1. **Check the badge color**:
   - Red = Conversion error
   - Yellow = Still converting
   - Green = Ready to play

2. **Click the video** to see detail page

3. **Read "Conversion Status" panel**:
   - Shows exact error message
   - Shows when it failed
   - Shows what format the original was

4. **Expand "Detailed Debug Log"**:
   - Shows ffmpeg command that was run
   - Shows exact error from ffmpeg
   - Shows file sizes before/after

5. **Common fixes**:
   - If MOV file: Upload as MP4 instead
   - If very large: Compress locally first
   - If permission error: Contact admin

## For Admins: Railway Configuration

### Required for video conversion:
1. **nixpacks.toml** - Installs ffmpeg
2. **Procfile** - Has worker process
3. **railway.json** - Configures web and worker services
4. **CELERY_BROKER_URL** - Redis URL (auto-set by Railway)

### Check this is working:
```bash
# In Railway logs
curl https://eastside-vb-website-production.up.railway.app/admin/
# Upload a test video
# Check logs for: ✅ Celery task queued
```

## Performance Notes

- **Small videos** (< 100MB): 10-30 seconds
- **Large videos** (100MB-2GB): 1-10 minutes  
- **Huge videos** (2GB+): May timeout

Videos are converted asynchronously, so:
- Upload returns immediately ✅
- Conversion happens in background 🔄
- Can watch progress by refreshing page

## Next Steps

If everything is working:
1. Upload test video to https://eastside-vb-website-production.up.railway.app
2. Confirm badge shows "Ready" ✅
3. Try playing the video
4. Share site with college admissions

If something fails:
1. Check debug log for error details
2. Check Railway logs for more context
3. Share error message with admin for fixing

---

**Need Help?**
- Check the debug log output first
- Look for 🔄, ✅, ❌, ⚠️ emojis for status hints
- Search Railway logs by video ID
- Expand "Detailed Debug Log" to see complete ffmpeg output
