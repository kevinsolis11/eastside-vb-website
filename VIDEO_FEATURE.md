# 🎥 Video Upload & Streaming Feature - Complete

## ✅ What's Implemented

### Models
- **Enhanced GameVideo Model** with:
  - Title, description, game type (Full Game/Highlights/Practice)
  - Game date & opponent tracking
  - Thumbnail image support
  - File size & duration metadata
  - View counter
  - Featured flag for homepage display
  - Created/updated timestamps
  - Ordering by date for easy browsing

### Views & Permissions
- **video_upload()** — Coach-only form to upload videos
- **video_list()** — List all videos (coaches see all, players see team-only)
- **video_detail()** — Stream video with metadata, view tracking
- **video_edit()** — Coach edits video info (title, description, date, etc)
- **video_delete()** — Coach deletes video with confirmation
- Permission checks: `is_coach()` and `is_team_member()` helpers

### Forms
- **GameVideoUploadForm** with:
  - File size validation (max 2GB video, 5MB thumbnail)
  - Format validation (MP4, MOV, MKV, AVI, WebM)
  - Auto-computed file size
  - Bootstrap styling

### Templates
- **video_upload.html** — Coach upload form with tips & file size info
- **video_list.html** — Grid layout with cards, featured badge, view count
- **video_detail.html** — Full video player, metadata, edit/delete buttons (coaches)
- **video_edit.html** — Edit video info while keeping file
- **video_delete_confirm.html** — Safety confirmation before delete

### Admin Interface
- Enhanced GameVideoAdmin with:
  - Organized fieldsets
  - Rich filtering (type, featured, private, date, uploader)
  - Search by title/opponent/description
  - Auto-sets uploaded_by to current user on creation
  - Readonly timestamps

### Database
- Migration applied (0007) with indexes on game_date and uploaded_at
- Optimized queries with select_related/prefetch_related ready

---

## 🚀 URLs

```
/team/videos/                    → List all videos (team members)
/team/videos/upload/             → Upload form (coaches only)
/team/videos/<id>/               → Watch video
/team/videos/<id>/edit/          → Edit metadata (coach who uploaded)
/team/videos/<id>/delete/        → Delete (coach who uploaded)
```

---

## 🎬 How to Use

### Coaches: Upload a Video
1. Login as a staff/coach user
2. Visit `/team/videos/upload/`
3. Fill in:
   - **Title**: "State Championship vs Lincoln High"
   - **Type**: Full Game / Highlights / Practice
   - **Date**: Date game was played
   - **Opponent**: Team name
   - **Video file**: MP4/MOV/MKV (max 2GB)
   - **Thumbnail**: Optional image (max 5MB)
   - **Featured**: Check to show on homepage
4. Click "Upload Video"
5. Video appears instantly in the list

### Coaches: Edit a Video
1. Click "Edit" button on video card or detail page
2. Change title, description, date, etc (can't change file)
3. Click "Save Changes"

### Coaches: Delete a Video
1. Click "Delete" button
2. Confirm on safety page
3. Video is removed with all metadata

### Players: Watch Videos
1. Login as a player (PlayerProfile)
2. Visit `/team/videos/`
3. Click any video card to play
4. View metadata, see who uploaded it
5. View count increments automatically

### Admin: Manage Videos
1. Login to Django admin `/admin/`
2. Go to "Team > Game Videos"
3. See all videos with filtering/search
4. Edit or delete from admin interface
5. View stats (uploads per coach, featured videos, etc)

---

## 🔒 Security & Permissions

### Access Control
```python
def can_view(user):
    # Coaches (staff): ✅ Can view all
    # Players (PlayerProfile): ✅ Can view private=True videos
    # Anonymous/logged-out: ❌ Cannot view
```

### Role-Based Features
| Action | Player | Coach |
|--------|--------|-------|
| View videos | ✅ | ✅ |
| Upload video | ❌ | ✅ |
| Edit video | ❌ | ✅ (own only) |
| Delete video | ❌ | ✅ (own only) |
| See view count | ✅ | ✅ |
| See uploader | ✅ | ✅ |

---

## 📊 File Storage

### Default: Local Storage
- Videos stored in: `volleyball_site/media/videos/YYYY/MM/`
- Thumbnails in: `volleyball_site/media/video_thumbnails/YYYY/MM/`
- Max video: 2GB (configurable)
- Max thumbnail: 5MB (configurable)

### Production: AWS S3 (Optional)
Update `settings.py`:
```python
# Install: pip install boto3 django-storages
STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
        'OPTIONS': {
            'AWS_STORAGE_BUCKET_NAME': 'your-bucket',
            'AWS_S3_REGION_NAME': 'us-east-1',
        }
    }
}
```

---

## 🎯 Database Schema

```sql
team_gamevideo {
  id INT PRIMARY KEY
  title VARCHAR(200)
  description TEXT
  game_type ENUM('full', 'highlight', 'practice')
  game_date DATE NULL
  opponent VARCHAR(200)
  video FileField (path)
  thumbnail ImageField (path) NULL
  duration_seconds INT DEFAULT 0
  file_size_mb FLOAT DEFAULT 0
  uploaded_by FK→User
  is_featured BOOL DEFAULT False
  view_count INT DEFAULT 0
  private BOOL DEFAULT True
  uploaded_at DATETIME
  updated_at DATETIME
  
  Indexes:
    - (game_date DESC)
    - (uploaded_at DESC)
}
```

---

## 🧪 Testing

### Create Test Video (Admin Shell)
```bash
.venv/bin/python volleyball_site/manage.py shell

from team.models import GameVideo
from django.contrib.auth.models import User

user = User.objects.filter(is_staff=True).first()
video = GameVideo.objects.create(
    title="Practice Scrimmage",
    game_type="practice",
    uploaded_by=user,
    private=True
)
print(f"Created: {video.id}")
```

### Test Permissions
```python
# In shell
user = User.objects.get(username='player1')
video = GameVideo.objects.first()

# Player (has PlayerProfile): True
print(video.can_view(user))

# Anonymous: False
print(video.can_view(None))
```

---

## 📈 Metrics Tracked

- **View Count**: Increments on first page load per session
- **Upload Count**: Total videos per coach (admin view)
- **Featured**: Promoted videos on homepage
- **Game Date**: Organize by match date
- **File Size**: Track storage usage

---

## 🔧 Configuration (settings.py)

```python
# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# File upload limits
FILE_UPLOAD_MAX_MEMORY_SIZE = 2147483648  # 2GB for videos
DATA_UPLOAD_MAX_MEMORY_SIZE = 2147483648

# Video formats allowed
ALLOWED_VIDEO_FORMATS = ['mp4', 'mov', 'mkv', 'avi', 'webm']
MAX_VIDEO_SIZE_MB = 2048
MAX_THUMBNAIL_SIZE_MB = 5

# Serve media files in development (add to urls.py)
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## ✨ Next Features (In Backlog)

- [ ] Video transcoding (convert to web-friendly formats)
- [ ] Streaming stats (bandwidth, quality, duration watched)
- [ ] Comments/reactions on videos
- [ ] Player stats overlay on video (kills, blocks, etc)
- [ ] Highlight reel generator (auto-compile clips)
- [ ] Video sharing (private links for external viewers)

---

## 🐛 Troubleshooting

### Video won't upload
- **Check file size**: Max 2GB
- **Check format**: Must be MP4, MOV, MKV, AVI, or WebM
- **Check permissions**: User must be staff/coach
- **Check disk space**: Server must have space
- **Check logs**: `tail -f logs/django.log`

### Video won't play
- **Browser support**: Use modern browser with HTML5 video
- **Format**: Some formats need codec support
- **Media files**: Ensure `MEDIA_ROOT` is accessible
- **URL rewrite**: Check Nginx config for `/media/` path

### Access denied
- **Not logged in**: Must login first
- **Not staff**: Player trying to upload
- **Not team member**: Needs PlayerProfile entry
- **Uploader only**: Only coach who uploaded can edit/delete

---

## 📚 Code Files Created/Modified

**New Files:**
- `team/templates/team/video_upload.html`
- `team/templates/team/video_list.html`
- `team/templates/team/video_detail.html`
- `team/templates/team/video_edit.html`
- `team/templates/team/video_delete_confirm.html`

**Modified Files:**
- `team/models.py` — Enhanced GameVideo model
- `team/forms.py` — Added GameVideoUploadForm
- `team/views.py` — Added video views (upload, list, detail, edit, delete)
- `team/urls.py` — Added video URL patterns
- `team/admin.py` — Enhanced GameVideoAdmin

**Database:**
- Migration: `team/migrations/0007_*.py`

---

## 🎉 That's It!

The video upload & streaming system is now fully functional and production-ready.

Next todo: **Player Stats Input Form** or **Player Dashboard**

Questions? Check the admin interface or test in shell.
