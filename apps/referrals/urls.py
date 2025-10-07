from django.urls import path
from . import views

app_name = 'referrals'

urlpatterns = [
    # Dashboard et pages principales
    path('', views.referrals_dashboard, name='dashboard'),
    path('invite/', views.invite_friends, name='invite_friends'),
    path('bulk-invite/', views.bulk_invite, name='bulk_invite'),
    path('my-referrals/', views.my_referrals, name='my_referrals'),
    path('my-rewards/', views.my_rewards, name='my_rewards'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('settings/', views.referral_settings, name='referral_settings'),
    
    # Inscription avec code de recommandation
    path('signup/<str:referral_code>/', views.referral_signup, name='referral_signup'),
    
    # Actions
    path('claim-reward/<int:reward_id>/', views.claim_reward, name='claim_reward'),
    
    # Analytics (admin)
    path('analytics/', views.referral_analytics, name='analytics'),
    
    # API AJAX
    path('api/send-invitation/', views.send_invitation, name='send_invitation'),
    path('api/track-click/<int:invitation_id>/', views.track_invitation_click, name='track_invitation_click'),
    path('api/track-open/<int:invitation_id>/', views.track_invitation_open, name='track_invitation_open'),
]


