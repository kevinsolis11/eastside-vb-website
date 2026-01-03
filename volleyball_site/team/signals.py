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
    Signal handler: Convert video to MP4 after upload if needed.
    Tries Celery first (async), falls back to synchronous conversion.
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
    
    # Try async conversion via Celery first
    if CELERY_AVAILABLE:
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
            return
            
        except Exception as e:
            logger.warning(f"⚠️ Celery not available, falling back to synchronous conversion: {str(e)}")
    
    # Fallback: Convert synchronously (blocks request, but ensures videos work)
    logger.info(f"🔄 Converting video {instance.id} synchronously (Celery unavailable)")
    try:
        # Update log to show conversion starting
        try:
            log = VideoConversionLog.objects.get(video=instance)
            log.status = VideoConversionLog.STATUS_PROCESSING
            log.debug_log += f"\n🔄 Starting synchronous conversion (Celery unavailable)\nStartTime: {timezone.now().isoformat()}\n"
            log.started_at = timezone.now()
            log.save()
        except VideoConversionLog.DoesNotExist:
            pass
        
        # Do synchronous conversion
        from team.video_converter import convert_to_mp4
        if convert_to_mp4(original_file_path, output_file_path):
            # Update video file path
            instance.video.name = relative_path
            instance.save(update_fields=['video', 'updated_at'])
            
            logger.info(f"✅ Video {instance.id} successfully converted synchronously")
            
            # Update conversion log
            try:
                log = VideoConversionLog.objects.get(video=instance)
                log.status = VideoConversionLog.STATUS_SUCCESS
                log.converted_size_mb = os.path.getsize(output_file_path) / (1024 * 1024)
                log.debug_log += f"✅ Synchronous conversion completed\nOutput file: {mp4_filename}\nConverted size: {log.converted_size_mb:.1f} MB\nCompleted: {timezone.now().isoformat()}\n"
                log.completed_at = timezone.now()
                log.save()
            except VideoConversionLog.DoesNotExist:
                pass
        else:
            error_msg = "FFmpeg conversion failed"
            logger.error(f"❌ {error_msg} for video {instance.id}")
            
            try:
                log = VideoConversionLog.objects.get(video=instance)
                log.status = VideoConversionLog.STATUS_FAILED
                log.error_message = error_msg
                log.debug_log += f"\n❌ ERROR: {error_msg}\nCompleted: {timezone.now().isoformat()}\n"
                log.completed_at = timezone.now()
                log.save()
            except VideoConversionLog.DoesNotExist:
                pass
    
    except Exception as e:
        logger.exception(f"❌ Synchronous conversion failed for video {instance.id}: {str(e)}")
        
        try:
            log = VideoConversionLog.objects.get(video=instance)
            log.status = VideoConversionLog.STATUS_FAILED
            log.error_message = f"Synchronous conversion error: {str(e)}"
            log.debug_log += f"\n❌ ERROR: {str(e)}\nCompleted: {timezone.now().isoformat()}\n"
            log.completed_at = timezone.now()
            log.save()
        except VideoConversionLog.DoesNotExist:
            pass
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

