from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from unittest.mock import patch, MagicMock
from team.models import PlayerProfile, Player, AISummary
from team.tasks import generate_ai_summary_sync


class AISummaryTaskTestCase(TestCase):
    """Test AI summary generation with mocked OpenAI."""
    
    def setUp(self):
        """Create test user and player profile."""
        self.user = User.objects.create_user(username='testplayer', email='player@test.com', password='testpass')
        self.player = Player.objects.create(first_name='John', last_name='Doe', number=5)
        self.player_profile = PlayerProfile.objects.create(user=self.user, player=self.player)
    
    @patch('team.tasks.OpenAI')
    def test_generate_ai_summary_sync_success(self, mock_openai_class):
        """Test successful AI summary generation with mocked OpenAI."""
        # Mock OpenAI client and response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Great performance with 15 kills and strong defensive plays."
        mock_client.chat.completions.create.return_value = mock_response
        
        # Set API key for the test
        with patch.object(settings, 'OPENAI_API_KEY', 'test-key'):
            result = generate_ai_summary_sync(self.player_profile.pk, "15 kills, 8 digs in final game")
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertIn('Great performance', result['summary'])
        
        # Verify AISummary was created/updated
        ai_summary = AISummary.objects.get(player=self.player_profile)
        self.assertIn('Great performance', ai_summary.summary)
    
    def test_generate_ai_summary_no_api_key(self):
        """Test AI summary generation fails gracefully without API key."""
        with patch.object(settings, 'OPENAI_API_KEY', None):
            result = generate_ai_summary_sync(self.player_profile.pk, "test context")
        
        self.assertFalse(result['success'])
        self.assertIn('API key not configured', result.get('error', ''))
    
    @patch('team.tasks.OpenAI')
    def test_generate_ai_summary_openai_error(self, mock_openai_class):
        """Test AI summary generation handles OpenAI API errors."""
        mock_openai_class.side_effect = Exception("API Error: Rate limit exceeded")
        
        with patch.object(settings, 'OPENAI_API_KEY', 'test-key'):
            result = generate_ai_summary_sync(self.player_profile.pk, "test context")
        
        self.assertFalse(result['success'])
        self.assertIn('Error', result.get('error', ''))
