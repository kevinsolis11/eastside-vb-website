# 🎥 Video System Test Guide

**Status**: ✅ **READY FOR TESTING**

---

## Quick Start

### Web Server
- **Running**: ✅ YES
- **URL**: http://127.0.0.1:8000/
- **Logs**: `/tmp/django_server.log`

### Test Account
- **Username**: `testcoach`
- **Password**: `TestPass123!`
- **Email**: `coach@test.com`
- **Role**: Superuser/Coach

---

## Test Steps

### 1. Login
1. Go to http://127.0.0.1:8000/accounts/login/
2. Enter credentials:
   - Username: `testcoach`
   - Password: `TestPass123!`
3. Click "Sign in"

### 2. View Video List
1. After login, go to http://127.0.0.1:8000/videos/
2. You'll see an empty list (no videos yet)
3. Look for "Upload Video" button

### 3. Upload a Test Video
1. Click "Upload Video" or go to http://127.0.0.1:8000/videos/upload/
2. Fill in the form:
   - **Title**: "Test Game vs Lincoln High"
   - **Type**: Full Game (dropdown)
   - **Game Date**: 2025-12-23
   - **Opponent**: Lincoln High
   - **Video**: Choose a video file (MP4/MOV, max 2GB)
   - **Thumbnail**: (optional) JPG/PNG, max 5MB
   - **Is Featured**: Check to feature on home page
3. Click "Upload Video"

### 4. View Uploaded Video
1. You'll be redirected to the video list
2. Your new video should appear as a card with:
   - Thumbnail image
   - Title
   - Game date
   - Opponent
   - View count (0 initially)
3. Click the card to watch the video

### 5. Edit Video
1. On the video detail page (while watching), click "Edit Video"
2. You can change:
   - Title
   - Description
   - Game type
   - Game date
   - Opponent
   - Featured status
3. **Note**: Cannot change the video file itself (by design)
4. Click "Update Video"

### 6. Delete Video
1. On the video detail page, click "Delete Video"
2. Confirm deletion on the confirmation page
3. Video will be removed from database and storage

### 7. Admin Interface
1. Go to http://127.0.0.1:8000/admin/
2. Click "Game Videos" under "Team"
3. You'll see:
   - List of all uploaded videos
   - Filtering by type, featured, private, date
   - Search by title, opponent, description
   - Rich editing interface
   - File size, view count, uploader info (read-only)

---

## What to Test

### ✅ Upload Functionality
- [ ] Form displays correctly
- [ ] All fields are present (title, type, date, opponent, video, thumbnail)
- [ ] File validation works (reject files over 2GB, wrong format)
- [ ] Video is stored in `volleyball_site/media/videos/YYYY/MM/`
- [ ] Thumbnail is stored in `volleyball_site/media/video_thumbnails/YYYY/MM/`

### ✅ Video Playback
- [ ] Video plays using HTML5 player
- [ ] Audio works
- [ ] Can pause/resume/seek
- [ ] Can fullscreen
- [ ] View count increments when watching (per session)

### ✅ Metadata Display
- [ ] Title shows correctly
- [ ] Game type displays (Full Game/Highlights/Practice)
- [ ] Game date displays
- [ ] Opponent name shows
- [ ] View count is visible
- [ ] Uploader name displays
- [ ] Uploaded timestamp shows

### ✅ Permissions
- [ ] Coach can upload videos
- [ ] Coach can edit own videos
- [ ] Coach can delete own videos
- [ ] Coach can see all videos
- [ ] Players (with PlayerProfile) can view team videos
- [ ] Anonymous users cannot access video pages
- [ ] Only coaches see "Edit" and "Delete" buttons

### ✅ Admin Interface
- [ ] Videos appear in admin
- [ ] Can filter by game type
- [ ] Can filter by featured/private
- [ ] Can search by title, opponent, description
- [ ] Can edit metadata (not file)
- [ ] File size is calculated and displayed
- [ ] View count is tracked
- [ ] Timestamps are accurate

### ✅ Edge Cases
- [ ] Upload very small video (MB)
- [ ] Upload large video (near 2GB limit)
- [ ] Upload unsupported format (should reject)
- [ ] Upload with no thumbnail
- [ ] Edit video while playing
- [ ] Delete featured video
- [ ] Multiple uploads in sequence

---

## Expected Behavior

### Upload Form
```
Title:        [text input]
Description:  [textarea]
Type:         [dropdown: Full Game, Highlights, Practice]
Game Date:    [date picker]
Opponent:     [text input]
Video:        [file upload - MP4/MOV/MKV/AVI/WebM, max 2GB]
Thumbnail:    [file upload - JPG/PNG/WebP, max 5MB, optional]
Featured:     [checkbox]
```

### Video List
- Shows cards in responsive grid (3 columns on desktop)
- Each card displays:
  - Thumbnail image (or placeholder)
  - Title
  - Game date (highlighted)
  - Opponent name
  - View count badge
  - "Featured" badge (if featured)
- Coaches see "Edit" and "Delete" buttons on cards
- Ordered by newest first

### Video Detail
- Full-width HTML5 video player
- Metadata sidebar with:
  - Title
  - Description
  - Type
  - Game date
  - Opponent
  - View count
  - Uploaded by (coach name)
  - Upload time
- Edit/Delete buttons (coaches only)
- Back to videos button

---

## Database

### Tables Updated
- `team_gamevideo` - Enhanced with 10 new fields

### New Fields
```
description          VARCHAR (optional)
game_type           VARCHAR (FULL/HIGHLIGHT/PRACTICE)
game_date           DATE
opponent            VARCHAR
thumbnail           ImageField
duration_seconds    INT
file_size_mb        FLOAT (auto-calculated)
is_featured         BOOLEAN
view_count          INT (default 0)
updated_at          DATETIME (auto-updated)
```

### Indexes
- idx_game_date DESC (for fast sorting)
- idx_uploaded_at DESC (for fast sorting)

---

## Troubleshooting

### Issue: Video upload page shows 404
**Solution**: Make sure you're logged in as testcoach. Unauthenticated users are redirected to login.

### Issue: Video doesn't play after upload
**Solution**: 
- Check file format (must be MP4, MOV, MKV, AVI, or WebM)
- Verify file isn't corrupted
- Check browser console for JS errors
- Ensure media files can be served by Django (should work in dev)

### Issue: Thumbnail doesn't show
**Solution**:
- Thumbnail is optional - if not provided, a placeholder is used
- If uploaded, check file format (JPG, PNG, WebP)
- Check file size (max 5MB)
- Verify image file isn't corrupted

### Issue: Permission denied when uploading
**Solution**:
- Make sure you're logged in as testcoach (superuser/coach)
- Check if your account is marked as staff in admin
- Create a new superuser if needed: `manage.py createsuperuser`

### Issue: View count not incrementing
**Solution**:
- View count is tracked per session (not per user)
- Open video in new private/incognito window to test
- Counter increments each time you visit the video detail page

### Issue: File size shows 0 or incorrect
**Solution**:
- File size is calculated from `video.video.size` in MB
- Should be calculated automatically on upload
- Check Django logs for errors during upload

---

## Admin Testing

### Access
- URL: http://127.0.0.1:8000/admin/
- Username: `testcoach`
- Password: `TestPass123!`

### Test in Admin
1. Go to "Team" section
2. Click "Game Videos"
3. You should see:
   - List of uploaded videos
   - Columns: Title, Game Date, Opponent, Type, Uploader, Views, Featured, Private, Uploaded
   - Filter sidebar with options
   - Search box
4. Click on any video to edit
5. Test the fieldsets:
   - **Video Info**: title, description, video file, thumbnail
   - **Game Details**: type, date, opponent
   - **Metadata**: file size (read-only), duration, view count (read-only)
   - **Settings**: uploaded by (auto), featured, private, timestamps

---

## Performance Notes

- Videos are served via Django's static file serving (adequate for dev)
- For production, use S3 or CDN:
  - Modify `MEDIA_URL` and `MEDIA_ROOT` in settings.py
  - Use `django-storages` for S3 backend
  - See `settings_prod.py` for example configuration

---

## Next Steps (Post-Testing)

After confirming video system works:

1. **Create More Test Data**
   - Upload multiple videos
   - Create test player accounts
   - Test viewing as different user types

2. **Player Stats Input Form** (Next Feature)
   - Coaches input kills, blocks, aces, digs per player
   - Link stats to games/videos
   - Display stats on player profiles

3. **Player Dashboard**
   - Show player their stats
   - Display featured videos
   - Show team information

4. **Coach Dashboard**
   - View all players and their stats
   - Analyze team trends
   - Access video library

5. **AI Summaries**
   - Generate performance summaries from stats
   - Display on player dashboard

---

## Files & Locations

### Code
- Models: `volleyball_site/team/models.py`
- Forms: `volleyball_site/team/forms.py`
- Views: `volleyball_site/team/views.py`
- URLs: `volleyball_site/team/urls.py`
- Admin: `volleyball_site/team/admin.py`

### Templates
- Upload form: `volleyball_site/team/templates/team/video_upload.html`
- Video list: `volleyball_site/team/templates/team/video_list.html`
- Video detail: `volleyball_site/team/templates/team/video_detail.html`
- Edit form: `volleyball_site/team/templates/team/video_edit.html`
- Delete confirm: `volleyball_site/team/templates/team/video_delete_confirm.html`

### Database
- SQLite: `volleyball_site/db.sqlite3`
- Migrations: `volleyball_site/team/migrations/0007_*.py`

### Media
- Videos: `volleyball_site/media/videos/YYYY/MM/`
- Thumbnails: `volleyball_site/media/video_thumbnails/YYYY/MM/`

### Logs
- Server: `/tmp/django_server.log`

---

**Last Updated**: 2025-12-23
**Feature Status**: ✅ Complete & Ready for Testing
**Django**: 6.0
**Database**: SQLite (dev), PostgreSQL-ready (prod)
