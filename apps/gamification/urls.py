from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    # Dashboard
    path('', views.gamification_dashboard, name='dashboard'),
    
    # Badges
    path('badges/', views.badges_list, name='badges_list'),
    path('badges/<int:badge_id>/', views.badge_detail, name='badge_detail'),
    
    # Réussites
    path('achievements/', views.achievements_list, name='achievements_list'),
    path('achievements/<int:achievement_id>/', views.achievement_detail, name='achievement_detail'),
    
    # Classements
    path('leaderboards/', views.leaderboards_list, name='leaderboards_list'),
    path('leaderboards/<int:leaderboard_id>/', views.leaderboard_detail, name='leaderboard_detail'),
    
    # Récompenses
    path('rewards/', views.rewards_list, name='rewards_list'),
    path('rewards/<int:reward_id>/claim/', views.claim_reward, name='claim_reward'),
    path('my-rewards/', views.my_rewards, name='my_rewards'),
    
    # Événements
    path('events/', views.events_list, name='events_list'),
    
    # API
    path('api/stats/', views.user_stats_api, name='user_stats_api'),
    path('api/trigger-action/', views.trigger_action_api, name='trigger_action_api'),
]


