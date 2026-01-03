# VIDEO SYSTEM TEST CHECKLIST

## Quick Test (Local Development)

### 1. Video Upload Test
- [ ] Log in as coach
- [ ] Go to "Upload Game Video"
- [ ] Try uploading a test video file (MOV, MKV, or MP4)
- [ ] Fill in title, game date, opponent
- [ ] Click "Upload Video"
- [ ] Should see success message

### 2. Video Player Test
- [ ] Go to "Videos" list
- [ ] Click on the video you uploaded
- [ ] Video detail page should load
- [ ] Video player should display
- [ ] Click play button
- [ ] Video should play in browser (if MP4)
- [ ] Controls should work (play, pause, volume, fullscreen)

### 3. Format Detection Test
**If you uploaded MOV/MKV:**
- [ ] Video detail page should show warning: "MOV files have limited browser support"
- [ ] Fallback "Download Video" link should appear
- [ ] Should be able to download

**If you uploaded MP4:**
- [ ] No warning message
- [ ] Video should play directly in browser
- [ ] No download link needed

### 4. Video Access Control Test
- [ ] Log out (or use different browser)
- [ ] Try to access video directly by URL
- [ ] Should see login page or "Access Denied"
- [ ] Log in as player/coach
- [ ] Should see video

### 5. View Count Test
- [ ] Open video detail page
- [ ] Note the view count
- [ ] Refresh page
- [ ] View count should increment by 1
- [ ] Refresh again
- [ ] View count should increment again

---

## Railway Production Test

### 1. Video Upload on Railway
- [ ] Go to https://your-railway-domain.com
- [ ] Log in as coach
- [ ] Upload test video (preferably MP4)
- [ ] Should complete successfully
- [ ] Video should be stored in persistent volume

### 2. Video Conversion Test (if MOV/MKV uploaded)
- [ ] Check Railway logs for conversion status
- [ ] Look for messages like:
  - "Celery task queued"
  - "Starting video conversion"
  - "FFmpeg conversion successful"
- [ ] After 1-2 minutes, video detail page should show MP4 version

### 3. Video Player on Railway
- [ ] Navigate to video
- [ ] Player should load
- [ ] MP4 should play (not MOV)
- [ ] All controls should work

### 4. Check Storage
- [ ] SSH to Railway (if possible)
- [ ] Check: `ls -lh /data/media/videos/`
- [ ] Should see both original file and MP4 conversion
- [ ] MP4 should be smaller than original MOV

---

## Troubleshooting

### Video Won't Upload
**Symptom:** Upload page hangs or error appears
**Check:**
- [ ] File size < 35GB (as configured)
- [ ] File format supported (MP4, MOV, MKV, AVI, WebM)
- [ ] Django error logs for upload errors

### Video Uploaded but Won't Play
**Symptom:** Page loads but player shows error or blank
**Check:**
- [ ] File is MP4 (MOV/MKV won't play in browser)
- [ ] Video file actually uploaded (check /media/videos/ folder)
- [ ] Browser console for JavaScript errors
- [ ] Browser is Chrome/Firefox/Edge (Safari may have issues with MOV)

### Video Takes Forever to Convert
**Symptom:** MOV/MKV uploaded but conversion hasn't completed
**Check:**
- [ ] Celery worker is running (on Railway, should auto-start)
- [ ] Check Railway logs for ffmpeg process
- [ ] Large files (500MB+) take 10-20 minutes to convert
- [ ] Don't close browser - conversion runs in background

### Video Plays But Controls Don't Work
**Symptom:** Video plays but play/pause/seek buttons don't respond
**Check:**
- [ ] Browser JavaScript enabled
- [ ] No browser extension blocking video controls
- [ ] Try different browser
- [ ] Check browser console for errors

---

## Detailed Log Locations

### Local Development Logs
```
logs/django.log  # Django errors
```

### Railway Logs
Railway Dashboard → Logs:
- Search for "video" → Video conversion logs
- Search for "celery" → Celery worker logs
- Search for "ffmpeg" → FFmpeg conversion logs
- Search for "upload" → Upload errors

---

## What Should Work

✅ **MP4 Videos:**
- Upload instantly
- Play immediately in browser
- All controls functional
- Visible to players with access

✅ **MOV/MKV Videos:**
- Upload instantly (no conversion yet)
- Queued for background conversion
- After 1-2 min: converted to MP4
- Then plays in browser

✅ **Access Control:**
- Players can only see team videos
- Staff can see all videos
- Non-logged-in users redirected to login

✅ **View Tracking:**
- Each page view increments counter
- Counts shown on video detail page

---

## Expected Behavior Timeline

**Coach uploads MOV file at 1:00 PM:**
- 1:00:00 - Upload complete, page shows success
- 1:00:01 - Celery task queued (coach doesn't wait)
- 1:00:02 - Video detail page shows MOV warning
- 1:01:00 - Celery worker starts ffmpeg conversion
- 1:02:30 - Conversion complete, database updated
- 1:02:31 - Video detail page shows MP4, no warning, plays in browser

---

## Test Files to Use

**Small test files (instant conversion):**
- 10-50 MB
- Converts in 30 seconds

**Medium test files (realistic):**
- 100-500 MB
- Converts in 2-5 minutes

**Large test files (load test):**
- 500MB - 2GB
- Converts in 10-60+ minutes
- Don't use unless testing capacity

---

## Success Criteria

All of these should be working:
- [ ] MP4 videos upload and play immediately
- [ ] MOV/MKV videos upload, convert to MP4, then play
- [ ] Video access restricted to team members only
- [ ] View count increments correctly
- [ ] Coaches can manage videos
- [ ] Players can watch videos
- [ ] College admissions can access team videos
- [ ] No error messages on happy path
- [ ] Clear error messages on failure path

If all checked ✓ = System working perfectly!
