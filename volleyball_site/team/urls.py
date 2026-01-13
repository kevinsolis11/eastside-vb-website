from django.urls import path
from .views import (
    PlayerListView, PlayerDetailView, signup, coach_codes,
    video_upload, video_list, video_detail, video_edit, video_delete,
    player_stats_list, player_stats_edit, player_stats_view, player_dashboard, player_edit, player_delete,
    generate_ai_summary, announcement_list, announcement_create, announcement_edit, 
    announcement_delete, announcement_feed, request_video_analysis, video_analysis_detail,
    ai_chat_view, settings_view
)

app_name = "team"

urlpatterns = [
    # Dashboard
    path('dashboard/', player_dashboard, name='player_dashboard'),
    path('settings/', settings_view, name='settings'),
    
    # Players
    path("", PlayerListView.as_view(), name="player-list"),
    path("player/<int:pk>/", PlayerDetailView.as_view(), name="player-detail"),
    path('signup/', signup, name='signup'),
    path('coach/codes/', coach_codes, name='coach_codes'),
    
    # AI Chat Assistant
    path('ai-chat/', ai_chat_view, name='ai_chat'),
    
    # Video endpoints
    path('videos/', video_list, name='video_list'),
    path('videos/upload/', video_upload, name='video_upload'),
    path('videos/<int:pk>/', video_detail, name='video_detail'),
    path('videos/<int:pk>/edit/', video_edit, name='video_edit'),
    path('videos/<int:pk>/delete/', video_delete, name='video_delete'),
    
    # Player stats endpoints
    path('stats/', player_stats_list, name='player_stats_list'),
    path('stats/<int:player_id>/edit/', player_stats_edit, name='player_stats_edit'),
    path('stats/<int:player_id>/view/', player_stats_view, name='player_stats_view'),
    path('player/<int:player_id>/edit/', player_edit, name='player_edit'),
    path('player/<int:player_id>/delete/', player_delete, name='player_delete'),
    
    # AI summary endpoints
    path('player/<int:player_profile_id>/ai-summary/', generate_ai_summary, name='generate_ai_summary'),
    
    # Video analysis endpoints (ChatGPT 5)
    path('videos/<int:video_id>/analyze/', request_video_analysis, name='request_video_analysis'),
    path('videos/<int:video_id>/analysis/', video_analysis_detail, name='video_analysis_detail'),
    
    # Announcements
    path('announcements/', announcement_list, name='announcement_list'),
    path('announcements/create/', announcement_create, name='announcement_create'),
    path('announcements/<int:announcement_id>/edit/', announcement_edit, name='announcement_edit'),
    path('announcements/<int:announcement_id>/delete/', announcement_delete, name='announcement_delete'),
    path('feed/', announcement_feed, name='announcement_feed'),
]
