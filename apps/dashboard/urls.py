from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.admin_dashboard, name='admin_dashboard'),
    
    # Statistiques et rapports
    path('statistics/', views.statistics, name='statistics'),
    path('reports/', views.reports, name='reports'),
    
    # Gestion des candidats
    path('candidates/', views.candidates_management, name='candidates'),
    path('candidate/<int:candidate_id>/', views.candidate_profile_view, name='candidate_profile'),
    
    # Export de données
    path('export/', views.export_data, name='export_data'),
    
    # API AJAX
    path('api/stats/', views.ajax_dashboard_stats, name='ajax_stats'),
    path('api/notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
]
