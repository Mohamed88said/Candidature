from django.urls import path
from . import views

app_name = 'matching'

urlpatterns = [
    # Dashboard et vues principales
    path('', views.matching_dashboard, name='dashboard'),
    path('matches/', views.job_matches, name='job_matches'),
    path('match/<int:match_id>/', views.match_detail, name='match_detail'),
    path('match/<int:match_id>/interest/', views.update_match_interest, name='update_match_interest'),
    
    # Préférences
    path('preferences/', views.matching_preferences, name='preferences'),
    
    # Actions
    path('generate-matches/', views.generate_new_matches, name='generate_matches'),
    
    # Analytics (admin)
    path('analytics/', views.matching_analytics, name='analytics'),
    
    # API AJAX
    path('api/match/<int:match_id>/interest/', views.ajax_match_interest, name='ajax_match_interest'),
    
    # Vues recruteur
    path('recruiter/job/<int:job_id>/matches/', views.recruiter_matches, name='recruiter_matches'),
]


