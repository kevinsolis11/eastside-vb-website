from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string


class Player(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    number = models.PositiveSmallIntegerField(null=True, blank=True)
    position = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["number", "last_name", "first_name"]

    def __str__(self) -> str:
        if self.number:
            return f"#{self.number} {self.first_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"


class AccessCode(models.Model):
    """Invite/access code that a coach can generate and give to players/managers.
    When a user signs up they must present an unused code which will
    be marked used after account creation.
    """
    ROLE_PLAYER = 'player'
    ROLE_MANAGER = 'manager'
    ROLE_CHOICES = [
        (ROLE_PLAYER, 'Player'),
        (ROLE_MANAGER, 'Manager'),
    ]

    code = models.CharField(max_length=32, unique=True, db_index=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_PLAYER)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    # optional: tie a code to a specific email address
    allowed_email = models.EmailField(null=True, blank=True, help_text="If set, only this email may use the code")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.code} ({self.role})"

    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def matches_email(self, email: str | None) -> bool:
        if not self.allowed_email:
            return True
        if not email:
            return False
        return self.allowed_email.lower() == email.lower()

    @staticmethod
    def generate(role: str = ROLE_PLAYER, length: int = 8) -> str:
        prefix = "PLR" if role == AccessCode.ROLE_PLAYER else "MGR"
        chars = string.ascii_uppercase + string.digits
        return f"{prefix}-" + ''.join(random.choices(chars, k=length))


class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    player = models.OneToOneField(Player, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.CharField(max_length=50, blank=True)
    height = models.CharField(max_length=10, blank=True)

    def __str__(self) -> str:
        return self.user.username


class PlayerStats(models.Model):
    player = models.OneToOneField(PlayerProfile, on_delete=models.CASCADE)
    kills = models.IntegerField(default=0)
    blocks = models.IntegerField(default=0)
    aces = models.IntegerField(default=0)
    digs = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Stats for {self.player}"


class GameVideo(models.Model):
    """Team game videos - coaches upload, players view.
    Access control: only team members can view.
    """
    GAME_TYPE_FULL = 'full'
    GAME_TYPE_HIGHLIGHT = 'highlight'
    GAME_TYPE_PRACTICE = 'practice'
    GAME_TYPE_CHOICES = [
        (GAME_TYPE_FULL, 'Full Game'),
        (GAME_TYPE_HIGHLIGHT, 'Highlights'),
        (GAME_TYPE_PRACTICE, 'Practice'),
    ]
    
    title = models.CharField(max_length=200, help_text="e.g., 'State Championship vs Lincoln High'")
    description = models.TextField(blank=True, help_text="Game summary, notes, or highlights")
    game_type = models.CharField(max_length=20, choices=GAME_TYPE_CHOICES, default=GAME_TYPE_FULL)
    game_date = models.DateField(null=True, blank=True, help_text="Date game was played")
    opponent = models.CharField(max_length=200, blank=True, help_text="Opponent team name")
    video = models.FileField(upload_to='videos/%Y/%m/', help_text="MP4, MOV, or MKV (max 2GB)")
    thumbnail = models.ImageField(upload_to='video_thumbnails/%Y/%m/', null=True, blank=True)
    duration_seconds = models.IntegerField(default=0, help_text="Video duration in seconds")
    file_size_mb = models.FloatField(default=0, help_text="File size in MB")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_videos', help_text="Coach who uploaded")
    is_featured = models.BooleanField(default=False, help_text="Show on home page")
    view_count = models.IntegerField(default=0)
    private = models.BooleanField(default=True, help_text="Only team members can view")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-game_date', '-uploaded_at']
        indexes = [models.Index(fields=['-game_date']), models.Index(fields=['-uploaded_at'])]

    def __str__(self) -> str:
        if self.game_date:
            return f"{self.title} ({self.game_date.strftime('%Y-%m-%d')})"
        return self.title
    
    def is_coach_uploaded(self, user: User) -> bool:
        """Check if user is the coach who uploaded this video."""
        return self.uploaded_by == user
    
    def can_view(self, user: User | None) -> bool:
        """Check if user can view this video (team members only)."""
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        # Check if user is part of the team (has PlayerProfile)
        return hasattr(user, 'playerprofile')


class AISummary(models.Model):
    player = models.OneToOneField(PlayerProfile, on_delete=models.CASCADE)
    summary = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"AI summary for {self.player}"


class VideoAnalysis(models.Model):
    """ChatGPT video analysis results for game videos."""
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]
    
    video = models.OneToOneField(GameVideo, on_delete=models.CASCADE, related_name='ai_analysis')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    analysis = models.TextField(blank=True, help_text="AI-generated video analysis")
    highlights = models.TextField(blank=True, help_text="Key highlights and moments")
    player_performance = models.TextField(blank=True, help_text="Individual player performance insights")
    tactical_notes = models.TextField(blank=True, help_text="Tactical analysis and suggestions")
    error_message = models.TextField(blank=True, help_text="Error details if analysis failed")
    analysis_model = models.CharField(max_length=50, default='gpt-5.1-codex-max', help_text="GPT model used for analysis")
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='video_analyses_requested')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Video Analyses"
    
    def __str__(self) -> str:
        return f"Analysis for {self.video.title} ({self.status})"


class Announcement(models.Model):
    """Announcements from coaches to the team."""
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_urgent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.title} by {self.coach.username}"

class VideoConversionLog(models.Model):
    """Track video conversion progress, status, and errors for debugging."""
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_SKIPPED = 'skipped'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Conversion'),
        (STATUS_PROCESSING, 'Converting...'),
        (STATUS_SUCCESS, 'Converted Successfully'),
        (STATUS_FAILED, 'Conversion Failed'),
        (STATUS_SKIPPED, 'Skipped (Already MP4)'),
    ]
    
    video = models.OneToOneField(GameVideo, on_delete=models.CASCADE, related_name='conversion_log')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    original_filename = models.CharField(max_length=255)
    original_format = models.CharField(max_length=10, blank=True)  # e.g. 'MOV', 'MKV'
    original_size_mb = models.FloatField(default=0, help_text="Original file size in MB")
    converted_size_mb = models.FloatField(default=0, help_text="Converted MP4 size in MB (if applicable)")
    celery_task_id = models.CharField(max_length=255, blank=True, null=True, help_text="Celery task UUID")
    error_message = models.TextField(blank=True, help_text="Error details if conversion failed")
    debug_log = models.TextField(blank=True, help_text="Detailed debug output from ffmpeg and system")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Video Conversion Log"
        verbose_name_plural = "Video Conversion Logs"
    
    def __str__(self) -> str:
        status_display = dict(self.STATUS_CHOICES).get(self.status, self.status)
        return f"{self.video.title} - {status_display}"
    
    def is_error(self) -> bool:
        return self.status == self.STATUS_FAILED
    
    def is_complete(self) -> bool:
        return self.status in [self.STATUS_SUCCESS, self.STATUS_FAILED, self.STATUS_SKIPPED]