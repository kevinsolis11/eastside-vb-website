"""Django signals for GameVideo model - handles automatic MP4 conversion."""
import os
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from team.models import GameVideo, VideoConversionLog
from team.video_converter import should_convert_to_mp4, get_mp4_filename
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Try to import Celery task, fall back gracefully if not available
try:
    from team.tasks import convert_video_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    logger.warning("⚠️ Celery not available, video conversion will be skipped")



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
        logger.warning(f"⚠️ No video file for GameVideo {instance.id}")
        return  # No video file
    
    filename = os.path.basename(video_file.name)
    
    # Check if conversion is needed
    if not should_convert_to_mp4(filename):
        logger.info(f"ℹ️ Video {filename} is already MP4 or not convertible - skipping conversion")
        # Update conversion log
        try:
            log = VideoConversionLog.objects.get(video=instance)
            log.status = VideoConversionLog.STATUS_SKIPPED
            log.debug_log += f"\n✓ File is already MP4 format, no conversion needed\n"
            log.completed_at = timezone.now()
            log.save()
        except VideoConversionLog.DoesNotExist:
            pass
        return
    
    logger.info(f"⏳ Video {filename} needs conversion to MP4")
    
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
            task = convert_video_task.delay(
                video_id=instance.id,
                original_file_path=original_file_path,
                output_file_path=output_file_path
            )
            logger.info(f"✅ Celery task queued for video {instance.id}: Task ID {task.id}")
            
            # Update conversion log with task ID
            try:
                log = VideoConversionLog.objects.get(video=instance)
                log.celery_task_id = task.id
                log.status = VideoConversionLog.STATUS_PROCESSING
                log.debug_log += f"\n🔄 Celery task queued\nTask ID: {task.id}\nScheduled: {timezone.now().isoformat()}\n"
                log.started_at = timezone.now()
                log.save()
            except VideoConversionLog.DoesNotExist:
                pass
            
        except Exception as e:
            logger.error(f"❌ Failed to queue Celery task for video {instance.id}: {str(e)}")
            # Update conversion log with error
            try:
                log = VideoConversionLog.objects.get(video=instance)
                log.status = VideoConversionLog.STATUS_FAILED
                log.error_message = f"Failed to queue conversion task: {str(e)}"
                log.debug_log += f"\n❌ ERROR: Could not queue Celery task\n{str(e)}\n"
                log.completed_at = timezone.now()
                log.save()
            except VideoConversionLog.DoesNotExist:
                pass
    else:
        logger.warning(f"⚠️ Celery not available - video {instance.id} will not be converted")
        try:
            log = VideoConversionLog.objects.get(video=instance)
            log.status = VideoConversionLog.STATUS_FAILED
            log.error_message = "Celery task queue not available"
            log.debug_log += f"\n⚠️ WARNING: Celery is not available on this server\n"
            log.completed_at = timezone.now()
            log.save()
        except VideoConversionLog.DoesNotExist:
            pass

