from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Dashboard et liste des conversations
    path('', views.chat_dashboard, name='dashboard'),
    path('rooms/', views.chat_rooms_list, name='rooms_list'),
    path('room/<int:room_id>/', views.chat_room_detail, name='room_detail'),
    
    # Création et gestion des conversations
    path('create/', views.create_chat_room, name='create_room'),
    path('start/<int:user_id>/', views.start_chat_with_user, name='start_chat'),
    path('start-from-application/<int:application_id>/', views.start_chat_from_application, name='start_from_application'),
    
    # Messages
    path('room/<int:room_id>/send/', views.send_message, name='send_message'),
    path('message/<int:message_id>/reaction/add/', views.add_reaction, name='add_reaction'),
    path('message/<int:message_id>/reaction/remove/', views.remove_reaction, name='remove_reaction'),
    
    # Paramètres et gestion
    path('settings/', views.chat_settings, name='settings'),
    path('notifications/', views.chat_notifications, name='notifications'),
    
    # Signalement et blocage
    path('report/<int:user_id>/', views.report_user, name='report_user'),
    path('block/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
    
    # Analytics (admin)
    path('analytics/', views.chat_analytics, name='analytics'),
]

