"""
Comprehensive tests for Eastside VB Website
Tests models, serializers, views, and API endpoints
"""

import pytest
import unittest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from datetime import timedelta

from team.models import (
    Player, AccessCode, PlayerProfile, PlayerStats, GameVideo, 
    AISummary, VideoAnalysis, Announcement
)
from team.forms import SignUpForm, GameVideoUploadForm, PlayerStatsForm, AISummaryForm
from team.serializers import (
    UserSerializer, PlayerSerializer, PlayerProfileSerializer,
    GameVideoSerializer, VideoAnalysisSerializer
)
from team.tasks import generate_ai_summary_sync, analyze_video_sync


class PlayerModelTests(TestCase):
    """Test Player model"""
    
    def setUp(self):
        self.player = Player.objects.create(
            first_name="John",
            last_name="Doe",
            number=12,
            position="Setter"
        )
    
    def test_player_creation(self):
        """Test player is created correctly"""
        self.assertEqual(self.player.first_name, "John")
        self.assertEqual(self.player.number, 12)
        self.assertEqual(str(self.player), "#12 John Doe")
    
    def test_player_ordering(self):
        """Test players are ordered by number"""
        player2 = Player.objects.create(first_name="Jane", last_name="Smith", number=1)
        players = Player.objects.all()
        self.assertEqual(players[0].number, 1)


class AccessCodeModelTests(TestCase):
    """Test AccessCode model"""
    
    def test_code_generation(self):
        """Test access code generation"""
        code = AccessCode.generate(role=AccessCode.ROLE_PLAYER)
        self.assertTrue(code.startswith("PLR-"))
    
    def test_code_expiry(self):
        """Test access code expiry"""
        future = timezone.now() + timedelta(days=1)
        code = AccessCode.objects.create(
            code="TEST-CODE",
            expires_at=future
        )
        self.assertFalse(code.is_expired())
    
    def test_code_email_matching(self):
        """Test access code email matching"""
        code = AccessCode.objects.create(
            code="TEST-CODE",
            allowed_email="test@example.com"
        )
        self.assertTrue(code.matches_email("test@example.com"))
        self.assertFalse(code.matches_email("other@example.com"))


class VideoAnalysisModelTests(TestCase):
    """Test VideoAnalysis model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="coach1", password="pass123")
        self.video = GameVideo.objects.create(
            title="Test Game",
            uploaded_by=self.user,
            video="test.mp4"
        )
    
    def test_analysis_creation(self):
        """Test video analysis creation"""
        analysis = VideoAnalysis.objects.create(
            video=self.video,
            status=VideoAnalysis.STATUS_PENDING,
            requested_by=self.user
        )
        self.assertEqual(analysis.status, VideoAnalysis.STATUS_PENDING)
    
    def test_analysis_status_choices(self):
        """Test all status choices"""
        for idx, (status, label) in enumerate(VideoAnalysis.STATUS_CHOICES):
            # Create a unique video for each analysis since video is OneToOneField
            video = GameVideo.objects.create(
                title=f"Test Game {idx}",
                uploaded_by=self.user,
                video=f"test{idx}.mp4"
            )
            analysis = VideoAnalysis.objects.create(
                video=video,
                status=status,
                requested_by=self.user
            )
            self.assertEqual(analysis.status, status)


class PlayerProfileSerializerTests(TestCase):
    """Test PlayerProfile serializer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="player1",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        self.player = Player.objects.create(
            first_name="John",
            last_name="Doe",
            number=12,
            position="Setter"
        )
        self.profile = PlayerProfile.objects.create(
            user=self.user,
            player=self.player,
            height="6'2\""
        )
    
    def test_profile_serializer(self):
        """Test PlayerProfile serializer"""
        serializer = PlayerProfileSerializer(self.profile)
        data = serializer.data
        self.assertEqual(data['user']['username'], "player1")  # type: ignore
        self.assertEqual(data['player']['number'], 12)  # type: ignore


class AISummaryFormTests(TestCase):
    """Test AI Summary form"""
    
    def test_form_valid(self):
        """Test form with valid data"""
        form = AISummaryForm(data={
            'game_context': '15 kills, 8 digs in state tournament'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_required(self):
        """Test form requires game context"""
        form = AISummaryForm(data={})
        self.assertFalse(form.is_valid())


class GameVideoModelTests(TestCase):
    """Test GameVideo model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="coach1", password="pass123")
        self.video = GameVideo.objects.create(
            title="State Championship",
            uploaded_by=self.user,
            opponent="Lincoln High",
            game_date="2025-12-20",
            video="test.mp4",
            private=True
        )
    
    def test_video_can_view_coach(self):
        """Test coach can view video"""
        self.user.is_staff = True
        self.assertTrue(self.video.can_view(self.user))
    
    def test_video_can_view_player(self):
        """Test player with profile can view private video"""
        player_user = User.objects.create_user(username="player1")
        PlayerProfile.objects.create(user=player_user)
        self.assertTrue(self.video.can_view(player_user))
    
    def test_video_cannot_view_unauthorized(self):
        """Test unauthorized user cannot view private video"""
        user = User.objects.create_user(username="outsider")
        self.assertFalse(self.video.can_view(user))


class AnnouncementModelTests(TestCase):
    """Test Announcement model"""
    
    def setUp(self):
        self.coach = User.objects.create_user(username="coach1", is_staff=True)
        self.announcement = Announcement.objects.create(
            coach=self.coach,
            title="Practice Cancelled",
            message="Tomorrow's practice is cancelled due to weather",
            is_urgent=True
        )
    
    def test_announcement_creation(self):
        """Test announcement is created"""
        self.assertEqual(self.announcement.title, "Practice Cancelled")
        self.assertTrue(self.announcement.is_urgent)
    
    def test_announcement_ordering(self):
        """Test announcements ordered by creation date"""
        ann2 = Announcement.objects.create(
            coach=self.coach,
            title="New Announcement",
            message="Test"
        )
        announcements = Announcement.objects.all()
        self.assertEqual(announcements[0].id, ann2.id)  # type: ignore


class APIAuthenticationTests(APITestCase):
    """Test API authentication"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.client = APIClient()
    
    @unittest.skip("API URLs not configured yet")
    def test_login(self):
        """Test user can login"""
        response = self.client.post(reverse('api:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)  # type: ignore
    
    @unittest.skip("API URLs not configured yet")
    def test_login_invalid(self):
        """Test login fails with wrong password"""
        response = self.client.post(reverse('api:login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 401)


class VideoAnalysisAPITests(APITestCase):
    """Test Video Analysis API endpoints"""
    
    def setUp(self):
        self.coach = User.objects.create_user(username="coach1", is_staff=True)
        self.client = APIClient()
        self.client.force_authenticate(user=self.coach)
        
        self.video = GameVideo.objects.create(
            title="Test Game",
            uploaded_by=self.coach,
            video="test.mp4"
        )
    
    @unittest.skip("API URLs not configured yet")
    def test_request_video_analysis(self):
        """Test requesting video analysis"""
        response = self.client.post(
            reverse('api:request_video_analysis', args=[self.video.id])  # type: ignore
        )
        # Should be 200 or pending status
        self.assertIn(response.status_code, [200, 201])
    
    @unittest.skip("API URLs not configured yet")
    def test_get_video_analysis_status(self):
        """Test getting video analysis status"""
        # Create analysis record
        analysis = VideoAnalysis.objects.create(
            video=self.video,
            status=VideoAnalysis.STATUS_PENDING,
            requested_by=self.coach
        )
        
        response = self.client.get(
            reverse('api:get_video_analysis', args=[self.video.id])  # type: ignore
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], VideoAnalysis.STATUS_PENDING)  # type: ignore


class FormValidationTests(TestCase):
    """Test form validation"""
    
    def test_signup_valid_code(self):
        """Test signup with valid code"""
        code = AccessCode.objects.create(code="PLR-TEST1234")
        form = SignUpForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'access_code': 'PLR-TEST1234'
        })
        self.assertTrue(form.is_valid())
    
    def test_signup_invalid_code(self):
        """Test signup with invalid code"""
        form = SignUpForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'access_code': 'INVALID'
        })
        self.assertFalse(form.is_valid())


class SettingsTests(TestCase):
    """Test Django settings configuration"""
    
    def test_gpt_model_configured(self):
        """Test GPT model is configured"""
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'OPENAI_GPT_MODEL'))
    
    def test_gpt_codex_max_setting(self):
        """Test GPT-5.1-Codex-Max setting exists"""
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'ENABLE_GPT_5_1_CODEX_MAX'))


if __name__ == '__main__':
    pytest.main([__file__])
