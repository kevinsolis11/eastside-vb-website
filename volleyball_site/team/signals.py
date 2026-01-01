"""Django signals for GameVideo model - handles automatic MP4 conversion."""
import os
import threading
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from team.models import GameVideo
from team.video_converter import should_convert_to_mp4, get_mp4_filename, convert_to_mp4
from django.conf import settings


def convert_video_async(video_id: int, original_file_path: str, output_file_path: str):
    """
    Convert video in background thread.
    
    Args:
        video_id: GameVideo instance ID
        original_file_path: Full path to original video file
        output_file_path: Full path where MP4 should be saved
    """
    try:
        # Perform conversion
        if convert_to_mp4(original_file_path, output_file_path):
            # Update database with new filename
            video = GameVideo.objects.get(id=video_id)
            
            # Get relative path from media root
            media_root = settings.MEDIA_ROOT
            if isinstance(media_root, str):
                relative_path = os.path.relpath(output_file_path, media_root)
            else:
                relative_path = os.path.relpath(output_file_path, str(media_root))
            
            # Update video file
            video.video.name = relative_path
            video.save(update_fields=['video', 'updated_at'])
            
            print(f"✓ Video {video_id} converted and database updated")
        else:
            print(f"✗ Failed to convert video {video_id}")
    
    except Exception as e:
        print(f"✗ Error in background conversion: {str(e)}")


@receiver(post_save, sender=GameVideo)
def convert_video_on_upload(sender, instance, created, **kwargs):
    """
    Signal handler: Convert video to MP4 after upload if needed.
    Runs conversion in background thread to avoid blocking the upload.
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
    
    # Start conversion in background thread (non-blocking)
    thread = threading.Thread(
        target=convert_video_async,
        args=(instance.id, original_file_path, output_file_path),
        daemon=True
    )
    thread.start()
    
    print(f"→ Conversion queued for {filename} → {mp4_filename}")
