"""Django signals for GameVideo model - handles automatic MP4 conversion."""
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from team.models import GameVideo
from team.video_converter import should_convert_to_mp4, get_mp4_filename
from django.conf import settings

# Try to import Celery task, fall back gracefully if not available
try:
    from team.tasks import convert_video_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    print("⚠️ Warning: Celery not available, video conversion will be skipped")


@receiver(post_save, sender=GameVideo)
def convert_video_on_upload(sender, instance, created, **kwargs):
    """
    Signal handler: Queue video conversion to MP4 after upload if needed.
    Uses Celery for reliable background task processing.
    Falls back gracefully if Celery is not available.
    """
    if not created:
        return  # Only convert on initial upload, not on updates
    
    video_file = instance.video
    if not video_file or not video_file.name:
        return  # No video file
    
    filename = os.path.basename(video_file.name)
    
    # Check if conversion is needed
    if not should_convert_to_mp4(filename):
        print(f"ℹ Video {filename} is already MP4 or not convertible")
        return
    
    print(f"⏳ Video {filename} needs conversion to MP4")
    
    # Get full paths
    original_file_path = video_file.path
    mp4_filename = get_mp4_filename(filename)
    output_directory = os.path.dirname(original_file_path)
    output_file_path = os.path.join(output_directory, mp4_filename)
    
    # Get relative path for database
    media_root = settings.MEDIA_ROOT
    if isinstance(media_root, str):
        relative_path = os.path.relpath(output_file_path, media_root)
    else:
        relative_path = os.path.relpath(output_file_path, str(media_root))
    
    if CELERY_AVAILABLE:
        # Queue Celery task for conversion (non-blocking, persistent)
        try:
            convert_video_task.delay(
                video_id=instance.id,
                original_file_path=original_file_path,
                output_file_path=output_file_path
            )
            print(f"→ Celery task queued for {filename} → {mp4_filename}")
        except Exception as e:
            print(f"✗ Failed to queue Celery task: {str(e)}")
    else:
        print(f"⚠️ Celery not available: {filename} will not be converted to MP4")
