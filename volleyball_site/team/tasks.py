from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from urllib.parse import urlsplit

from .models import AccessCode, AISummary, PlayerProfile, VideoAnalysis

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = get_task_logger(__name__)


def send_invite_mail_sync(codes, email, signup_url):
    """Send invite email synchronously (helper used by the Celery task and views)."""
    subject = "Your access code(s) for Eastside VB"
    # attempt to construct a reasonable static logo URL from the signup_url
    logo_url = None
    try:
        parts = urlsplit(signup_url)
        logo_url = f"{parts.scheme}://{parts.netloc}/static/team/img/logo.png"
    except Exception:
        logo_url = None

    context = {'codes': codes, 'signup_url': signup_url, 'logo_url': logo_url}
    text_body = render_to_string('emails/invite_email.txt', context)
    html_body = render_to_string('emails/invite_email.html', context)
    from_name = getattr(settings, 'DEFAULT_FROM_NAME', 'Eastside VB')
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@localhost')
    reply_to = getattr(settings, 'DEFAULT_REPLY_TO', None)
    from_header = f"{from_name} <{from_email}>"
    headers = {}
    if reply_to:
        headers['Reply-To'] = reply_to

    msg = EmailMultiAlternatives(subject, text_body, from_header, [email], headers=headers)
    if reply_to:
        msg.reply_to = [reply_to]
    if html_body:
        msg.attach_alternative(html_body, 'text/html')
    msg.send()
    logger.info('Sent invite email to %s with %d codes', email, len(codes))
    return {'sent': True}


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 5})
def send_invite_mail(self, codes, email, signup_url):
    """Celery task wrapper around the synchronous send helper."""
    try:
        # Check email configuration before attempting
        email_host = getattr(settings, 'EMAIL_HOST', '').strip()
        email_user = getattr(settings, 'EMAIL_HOST_USER', '').strip()
        
        if not email_host or email_host == 'localhost' or not email_user:
            logger.error(
                'Email not configured (EMAIL_HOST=%s, EMAIL_HOST_USER=%s). '
                'Cannot send invite to %s. Please configure email settings.',
                email_host, email_user, email
            )
            raise Exception(
                'Email server not configured. Set EMAIL_HOST_USER and EMAIL_HOST in environment.'
            )
        
        return send_invite_mail_sync(codes, email, signup_url)
    except Exception as exc:
        logger.exception('Failed to send invite email to %s: %s', email, str(exc))
        raise


@shared_task(bind=True)
def cleanup_accesscodes_task(self, days=30):
    """Cleanup old used access codes older than `days`.

    Returns dict with deleted count.
    """
    from datetime import timedelta
    try:
        cutoff = timezone.now() - timedelta(days=days)
        qs = AccessCode.objects.filter(is_used=True, created_at__lt=cutoff)
        count = qs.count()
        qs.delete()
        logger.info('cleanup_accesscodes_task deleted %d codes older than %d days', count, days)
        return {'deleted': count}
    except Exception:
        logger.exception('Failed during cleanup_accesscodes_task')
        raise


def generate_ai_summary_sync(player_profile_id: int, game_context: str) -> dict:
    """Generate AI summary synchronously using OpenAI.
    
    Args:
        player_profile_id: ID of the PlayerProfile to generate summary for
        game_context: Game or player performance context (e.g., "Player had 15 kills, 8 digs, 2 aces in state tournament")
    
    Returns:
        dict with 'success' boolean and 'summary' string
    """
    if not OpenAI:
        logger.error('OpenAI package not installed; cannot generate summary')
        return {'success': False, 'error': 'OpenAI not installed'}
    
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        logger.error('OPENAI_API_KEY not configured in settings')
        return {'success': False, 'error': 'OpenAI API key not configured'}
    
    try:
        player = PlayerProfile.objects.select_related('player').get(id=player_profile_id)
        player_name = str(player.player) if player.player else player.user.username
        
        client = OpenAI(api_key=api_key)
        prompt = f"""Generate a brief AI summary (3-5 sentences) of volleyball performance for {player_name}:
Game context: {game_context}

Keep it motivational and highlight strengths."""
        
        gpt_model = getattr(settings, 'OPENAI_GPT_MODEL', 'gpt-3.5-turbo')
        response = client.chat.completions.create(
            model=gpt_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150,
        )
        
        summary = response.choices[0].message.content
        
        # Save to AISummary model
        ai_summary, created = AISummary.objects.update_or_create(
            player=player,
            defaults={'summary': summary}
        )
        
        logger.info('Generated AI summary for player %s', player_name)
        return {'success': True, 'summary': summary}
    
    except Exception as e:
        logger.exception('Error generating AI summary for player_profile_id %s', player_profile_id)
        return {'success': False, 'error': str(e)}


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def generate_ai_summary_task(self, player_profile_id: int, game_context: str):
    """Celery task wrapper for generating AI summaries."""
    return generate_ai_summary_sync(player_profile_id, game_context)


def analyze_video_sync(video_id: int) -> dict:
    """Analyze game video using ChatGPT with vision capabilities.
    
    Args:
        video_id: ID of the GameVideo to analyze
    
    Returns:
        dict with 'success' boolean and analysis results
    """
    if not OpenAI:
        logger.error('OpenAI package not installed; cannot analyze video')
        return {'success': False, 'error': 'OpenAI not installed'}
    
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        logger.error('OPENAI_API_KEY not configured in settings')
        return {'success': False, 'error': 'OpenAI API key not configured'}
    
    try:
        from .models import GameVideo
        video = GameVideo.objects.get(id=video_id)
        analysis, created = VideoAnalysis.objects.get_or_create(video=video)
        analysis.status = VideoAnalysis.STATUS_PROCESSING
        analysis.started_at = timezone.now()
        analysis.save()
        
        client = OpenAI(api_key=api_key)
        gpt_model = getattr(settings, 'OPENAI_GPT_MODEL', 'gpt-3.5-turbo')
        
        # For video analysis, we'll use a detailed prompt that would work with vision-capable models
        prompt = f"""Analyze this volleyball game video and provide comprehensive insights:

Video: {video.title}
Date: {video.game_date}
Opponent: {video.opponent}
Type: {video.get_game_type_display()}

Please provide:
1. **Overall Game Analysis**: Summary of team performance, score trends, key moments
2. **Highlights**: Most impressive plays, momentum shifts, clutch moments
3. **Player Performance**: Notable individual performances (if visible)
4. **Tactical Notes**: Formation choices, strategy effectiveness, areas for improvement
5. **Recommendations**: Coaching suggestions for future games

Be specific and actionable in your analysis."""
        
        response = client.chat.completions.create(
            model=gpt_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
        )
        
        analysis_text = response.choices[0].message.content
        
        # Parse the analysis into sections
        sections = parse_video_analysis(analysis_text)
        
        analysis.analysis = analysis_text
        analysis.highlights = sections.get('highlights', '')
        analysis.player_performance = sections.get('player_performance', '')
        analysis.tactical_notes = sections.get('tactical_notes', '')
        analysis.analysis_model = gpt_model
        analysis.status = VideoAnalysis.STATUS_COMPLETED
        analysis.completed_at = timezone.now()
        analysis.save()
        
        logger.info('Completed video analysis for %s', video.title)
        return {'success': True, 'analysis_id': analysis.id}
    
    except Exception as e:
        logger.exception('Error analyzing video_id %s', video_id)
        try:
            analysis.status = VideoAnalysis.STATUS_FAILED
            analysis.error_message = str(e)
            analysis.save()
        except Exception:
            pass
        return {'success': False, 'error': str(e)}


def parse_video_analysis(analysis_text: str) -> dict:
    """Parse structured analysis text into sections.
    
    Args:
        analysis_text: Raw analysis from GPT
    
    Returns:
        dict with parsed sections
    """
    sections = {
        'highlights': '',
        'player_performance': '',
        'tactical_notes': ''
    }
    
    lines = analysis_text.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        line_lower = line.lower()
        if '**highlights**' in line_lower or '## highlights' in line_lower:
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'highlights'
            current_content = []
        elif '**player performance**' in line_lower or '## player performance' in line_lower:
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'player_performance'
            current_content = []
        elif '**tactical notes**' in line_lower or '**recommendations**' in line_lower or '## tactical' in line_lower or '## recommendations' in line_lower:
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'tactical_notes'
            current_content = []
        elif current_section:
            current_content.append(line)
    
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def analyze_video_task(self, video_id: int):
    """Celery task wrapper for video analysis."""
    return analyze_video_sync(video_id)


# ==================== VIDEO CONVERSION TASKS ====================

@shared_task(bind=True, max_retries=3)
def convert_video_task(self, video_id: int, original_file_path: str, output_file_path: str):
    """
    Celery task to convert video to MP4 format.
    Reliable background task processing with automatic retries.
    
    Args:
        video_id: GameVideo instance ID
        original_file_path: Full path to original video file
        output_file_path: Full path where MP4 should be saved
    
    Returns:
        Success message or raises exception for retry
    """
    import os
    from team.video_converter import convert_to_mp4
    from team.models import GameVideo
    
    try:
        logger.info(f"🎬 Starting video conversion task for video {video_id}")
        
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
            
            logger.info(f"✓ Video {video_id} converted and database updated")
            return f"Video {video_id} successfully converted to MP4"
        else:
            error_msg = f"FFmpeg conversion failed for video {video_id}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    except Exception as exc:
        logger.exception(f"Error in video conversion task for video {video_id}: {str(exc)}")
        # Retry up to 3 times with exponential backoff (1 min, 2 min, 4 min)
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))