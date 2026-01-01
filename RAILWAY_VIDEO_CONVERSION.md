# Railway Auto-MP4 Conversion - Complete Setup

## Issues Fixed ✅

### 1. **ffmpeg Not Available in Railway** ⚠️ CRITICAL
**Problem:** Railway's default NIXPACKS environment doesn't include ffmpeg
**Solution:** Added `nixpacks.toml` that explicitly requests ffmpeg from Nix packages
```toml
{ pkgs }:
with pkgs; [
  ffmpeg          # Video conversion library
  python314
]
```
**Result:** FFmpeg will be installed during Railway build

---

### 2. **Threading Reliability on Railway** ⚠️ MEDIUM
**Problem:** Background threads can be interrupted if container restarts
**Solution:** Switched from `threading.Thread` to Celery task queue
**Benefits:**
- Persistent task queue (persists across container restarts)
- Automatic retry logic (up to 3 retries with exponential backoff)
- Proper error handling and logging
- Scalable to multiple workers

---

### 3. **Long-Running Conversion Process** ⚠️ MEDIUM
**Problem:** Large videos (2GB) take hours to convert; HTTP requests timeout
**Solution:** Celery runs asynchronously outside the request/response cycle
**Process Flow:**
1. User uploads video
2. Django saves file, fires signal
3. Signal queues Celery task immediately (non-blocking)
4. HTTP response returns instantly
5. Celery worker processes conversion in background
6. Database updates when complete

---

## How It Works

### Deployment Architecture
```
┌─────────────────────────────────────┐
│        Railway Container            │
├─────────────────────────────────────┤
│  Web Process (Gunicorn)             │ ← Handles HTTP requests
│  ├─ 1 replica                       │
│  └─ Port 8000                       │
├─────────────────────────────────────┤
│  Worker Process (Celery)            │ ← Converts videos
│  ├─ 1 replica                       │
│  └─ Concurrency: 2 workers          │
├─────────────────────────────────────┤
│  Redis (CELERY_BROKER_URL)          │ ← Task queue
│  └─ Stores pending conversions      │
├─────────────────────────────────────┤
│  Persistent Volume: /data/media     │ ← Stores videos
│  └─ Both original & MP4 files       │
└─────────────────────────────────────┘
```

### Video Upload Flow
```
1. Coach uploads .mov/.mkv/.avi file
   ↓
2. Django saves to /data/media/videos/
   ↓
3. Post-save signal fires
   ↓
4. Signal queues Celery task (non-blocking)
   ↓
5. Upload response sent immediately ✓
   ↓
6. Celery worker picks up task
   ↓
7. ffmpeg converts to MP4
   ↓
8. Database updated with MP4 filename
   ↓
9. Players see MP4 in browser ✓
```

---

## Configuration Files Changed

### 1. `nixpacks.toml` (NEW)
- Tells Railway to install ffmpeg
- Will be executed during build phase
- Increases build time by ~2-3 minutes but needed for conversion

### 2. `Procfile` (UPDATED)
- Added `worker` process type
- Railway will automatically start Celery worker when deployed

```bash
web: cd volleyball_site && gunicorn volleyball_site.wsgi --bind 0.0.0.0:8000
release: cd volleyball_site && python manage.py migrate --noinput
worker: cd volleyball_site && celery -A volleyball_site worker -l info --concurrency=2
```

### 3. `railway.json` (UPDATED)
- Specifies `web` and `worker` services
- Railway will manage both processes

### 4. `team/signals.py` (UPDATED)
- Removed: `threading.Thread` implementation
- Added: Celery task queue integration
- Graceful fallback if Celery unavailable

### 5. `team/tasks.py` (UPDATED)
- Added: `convert_video_task` Celery task
- Handles MP4 conversion with retry logic

---

## Testing Checklist ✓

- [x] Django check passes
- [x] Celery tasks imported successfully
- [x] Signals registered properly
- [x] Code committed to main branch
- [x] Railway build configured

### To Test on Railway

1. **Deploy changes**
   ```bash
   git push origin main  # Already done ✓
   ```

2. **Monitor Railway deployment**
   - Watch build logs for ffmpeg installation
   - Watch worker process starting

3. **Upload test video**
   - Upload .mov or .mkv file
   - Should see conversion queued in logs
   - Browser should display MP4 when ready

4. **Check logs**
   ```
   Railway Dashboard → Logs
   ```
   Look for:
   - ✓ ffmpeg installed
   - ✓ Celery worker started
   - ✓ Task processed

---

## Supported Video Formats

**Converted automatically to MP4:**
- `.mov` (QuickTime)
- `.mkv` (Matroska)
- `.avi` (Audio Video Interleave)
- `.webm` (WebM)
- `.flv` (Flash Video)
- `.wmv` (Windows Media)
- `.m4v` (iTunes Video)
- `.ts`, `.mts` (MPEG Transport Stream)

**Already compatible (no conversion needed):**
- `.mp4` (MPEG-4) ✓

---

## Performance Notes

### Conversion Times (Approximate)
- Small video (100MB): 2-5 minutes
- Medium video (500MB): 10-20 minutes
- Large video (2GB): 30-60+ minutes

### Resource Usage
- ffmpeg: CPU-intensive (uses available cores)
- Storage: Original + MP4 copies (disk space requirement doubles temporarily)
- Memory: ~100-500MB per conversion

### Railway Limits
- Storage: Default 10GB ephemeral + persistent /data/media
- CPU: Shared with web process
- Concurrency: Set to 2 workers to avoid resource contention

---

## Troubleshooting

### Issue: "ffmpeg not found"
**Cause:** Railway build didn't include ffmpeg
**Fix:** 
1. Check `nixpacks.toml` exists
2. Trigger new Railway build
3. Wait for ffmpeg installation in logs

### Issue: Celery tasks not processing
**Cause:** Worker process not running
**Fix:**
1. Restart Railway deployment
2. Check worker logs in Railway dashboard
3. Verify Redis connection

### Issue: MP4 file not being created
**Cause:** ffmpeg conversion failed
**Check logs:**
```
Railway Dashboard → Logs → Search for "Error in video conversion"
```

### Issue: Slow conversion
**Cause:** Other tasks or web requests using CPU
**Fix:**
- Increase worker concurrency (in production)
- Use separate Railway environment for workers
- Optimize ffmpeg flags (currently preset=fast)

---

## Next Steps (Optional)

### For Production Scale
1. **Separate Worker Service**
   - Create dedicated Railway service for Celery workers
   - Allows independent scaling

2. **Celery Beat Scheduler**
   - Schedule cleanup tasks
   - Monitor conversion progress

3. **Progress Tracking**
   - Store conversion progress in database
   - Display to users in real-time

4. **Video Quality Options**
   - High (CRF 18, larger file)
   - Medium (CRF 23, balanced) ← Current
   - Low (CRF 28, smaller file)

---

## Environment Variables Required

Ensure these are set in Railway:

```
CELERY_BROKER_URL=redis://...  (Auto-configured by Railway)
CELERY_RESULT_BACKEND=redis://...  (Auto-configured by Railway)
MEDIA_ROOT=/data/media  (Persistent volume)
```

All others configured in `settings_prod.py` ✓

---

## Deploy to Railway

Already committed! Just monitor:

```bash
# Check deployment status
git log --oneline | head -5
# Should show: 9ecd875 Fix Railway deployment: Add ffmpeg and Celery
```

Railway will automatically build and deploy with:
- ✅ ffmpeg installed
- ✅ Celery worker running
- ✅ Auto-conversion enabled

