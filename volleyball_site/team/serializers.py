from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Player, PlayerProfile, PlayerStats, GameVideo, AISummary, Announcement, VideoAnalysis

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'first_name', 'last_name', 'number', 'position']

class PlayerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStats
        fields = ['id', 'kills', 'blocks', 'aces', 'digs', 'updated_at']

class PlayerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    player = PlayerSerializer(read_only=True)
    stats = serializers.SerializerMethodField()
    
    class Meta:
        model = PlayerProfile
        fields = ['id', 'user', 'player', 'position', 'height', 'stats']
    
    def get_stats(self, obj):
        try:
            return PlayerStatsSerializer(obj.playerstats).data
        except PlayerStats.DoesNotExist:
            return None

class AISummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = AISummary
        fields = ['id', 'summary', 'generated_at']

class GameVideoSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = GameVideo
        fields = ['id', 'title', 'description', 'game_type', 'game_date', 'opponent', 
                  'thumbnail', 'duration_seconds', 'view_count', 'uploaded_by_name', 'uploaded_at']

class AnnouncementSerializer(serializers.ModelSerializer):
    coach_name = serializers.CharField(source='coach.get_full_name', read_only=True)
    
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'message', 'is_urgent', 'coach_name', 'created_at', 'updated_at']
        ordering = ['-created_at']

class VideoAnalysisSerializer(serializers.ModelSerializer):
    video_title = serializers.CharField(source='video.title', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    
    class Meta:
        model = VideoAnalysis
        fields = ['id', 'video', 'video_title', 'status', 'analysis', 'highlights', 
                  'player_performance', 'tactical_notes', 'analysis_model', 
                  'requested_by_name', 'created_at', 'started_at', 'completed_at', 'error_message']

