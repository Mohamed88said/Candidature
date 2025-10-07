from django.urls import path
from . import views

app_name = 'push_notifications'

urlpatterns = [
    # Dashboard
    path('', views.notifications_dashboard, name='dashboard'),
    
    # Préférences
    path('preferences/', views.manage_preferences, name='manage_preferences'),
    
    # Appareils
    path('devices/', views.devices_list, name='devices_list'),
    path('devices/register/', views.register_device, name='register_device'),
    path('devices/<int:device_id>/unregister/', views.unregister_device, name='unregister_device'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Campagnes (Admin)
    path('campaigns/', views.campaigns_list, name='campaigns_list'),
    path('campaigns/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('campaigns/<int:campaign_id>/send/', views.send_campaign, name='send_campaign'),
    
    # Modèles (Admin)
    path('templates/', views.templates_list, name='templates_list'),
    path('templates/<int:template_id>/', views.template_detail, name='template_detail'),
    
    # Analyses (Admin)
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    
    # API
    path('api/register-device/', views.register_device_api, name='register_device_api'),
    path('api/unregister-device/', views.unregister_device_api, name='unregister_device_api'),
    path('api/send-notification/', views.send_notification_api, name='send_notification_api'),
    path('api/mark-read/', views.mark_notification_read_api, name='mark_notification_read_api'),
    path('api/preferences/', views.update_preferences_api, name='update_preferences_api'),
]

