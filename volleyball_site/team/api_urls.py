from django.urls import path
from . import api_views

app_name = 'api'

urlpatterns = [
    # Auth
    path('login/', api_views.login, name='login'),
    path('logout/', api_views.logout, name='logout'),
    
    # Player data
    path('player/profile/', api_views.get_player_profile, name='player_profile'),
    path('player/stats/', api_views.get_player_stats, name='player_stats'),
    path('player/summary/', api_views.get_ai_summary, name='ai_summary'),
    
    # Team data
    path('announcements/', api_views.get_announcements, name='announcements'),
    path('videos/', api_views.get_game_videos, name='videos'),
    
    # Video analysis (ChatGPT 5 analyzer)
    path('videos/<int:video_id>/analyze/', api_views.request_video_analysis, name='request_video_analysis'),
    path('videos/<int:video_id>/analysis/', api_views.get_video_analysis, name='get_video_analysis'),
    
    # AI Chat Assistant
    path('ai-chat/', api_views.ai_chat, name='ai_chat'),
]