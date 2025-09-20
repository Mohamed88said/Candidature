from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Liste et recherche
    path('', views.job_list, name='job_list'),
    path('categories/', views.job_categories, name='job_categories'),
    path('category/<int:category_id>/', views.jobs_by_category, name='jobs_by_category'),
    
    # Favoris
    path('save/<int:job_id>/', views.toggle_save_job, name='toggle_save_job'),
    path('saved/', views.saved_jobs, name='saved_jobs'),
    
    # Alertes emploi - DOIT ÊTRE AVANT le pattern <slug:slug>/
    path('alerts/', views.job_alerts, name='job_alerts'),
    path('alerts/create/', views.create_job_alert, name='create_job_alert'),
    path('alerts/<int:alert_id>/edit/', views.edit_job_alert, name='edit_job_alert'),
    path('alerts/<int:alert_id>/delete/', views.delete_job_alert, name='delete_job_alert'),
    path('alerts/<int:alert_id>/toggle/', views.toggle_job_alert, name='toggle_job_alert'),
    
    # Détail et gestion des offres - DOIT ÊTRE APRÈS tous les autres patterns
    path('create/', views.create_job, name='create_job'),
    path('<slug:slug>/edit/', views.edit_job, name='edit_job'),
    path('<slug:slug>/', views.job_detail, name='job_detail'),
]