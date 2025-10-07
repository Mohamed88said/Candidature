from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    # Dashboard et liste des alertes
    path('', views.alerts_dashboard, name='dashboard'),
    path('list/', views.alerts_list, name='alerts_list'),
    path('alert/<int:alert_id>/', views.alert_detail, name='alert_detail'),
    
    # Préférences et abonnements
    path('preferences/', views.alert_preferences, name='preferences'),
    path('subscriptions/', views.alert_subscriptions, name='subscriptions'),
    
    # Actions sur les alertes
    path('alert/<int:alert_id>/mark-read/', views.mark_alert_read, name='mark_alert_read'),
    path('alert/<int:alert_id>/mark-clicked/', views.mark_alert_clicked, name='mark_alert_clicked'),
    path('alert/<int:alert_id>/feedback/', views.submit_alert_feedback, name='submit_alert_feedback'),
    path('bulk-action/', views.bulk_alert_action, name='bulk_alert_action'),
    
    # Analytics (admin)
    path('analytics/', views.alert_analytics, name='analytics'),
]


