from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    ChatRoom, Message, ChatParticipant, ChatNotification, 
    ChatSettings, ChatBlock, ChatReport
)


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'room_type', 'candidate', 'recruiter', 
        'job_link', 'message_count', 'last_message_at', 'is_active'
    ]
    list_filter = ['room_type', 'is_active', 'created_at']
    search_fields = ['title', 'candidate__first_name', 'candidate__last_name', 
                    'recruiter__first_name', 'recruiter__last_name']
    readonly_fields = ['created_at', 'updated_at', 'message_count', 'last_message_at']
    raw_id_fields = ['candidate', 'recruiter', 'job', 'application']
    
    def job_link(self, obj):
        if obj.job:
            url = reverse('admin:jobs_job_change', args=[obj.job.id])
            return format_html('<a href="{}">{}</a>', url, obj.job.title)
        return '-'
    job_link.short_description = 'Offre d\'emploi'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'room_type', 'candidate', 'recruiter', 'is_active')
        }),
        ('Contexte', {
            'fields': ('job', 'application')
        }),
        ('Statistiques', {
            'fields': ('message_count', 'last_message_at', 'last_message_by'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'room_link', 'sender', 'message_type', 'content_preview', 
        'created_at', 'is_deleted'
    ]
    list_filter = ['message_type', 'is_deleted', 'created_at']
    search_fields = ['content', 'sender__first_name', 'sender__last_name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['room', 'sender', 'reply_to']
    
    def room_link(self, obj):
        url = reverse('admin:chat_chatroom_change', args=[obj.room.id])
        return format_html('<a href="{}">{}</a>', url, obj.room.title)
    room_link.short_description = 'Salle de chat'
    
    def content_preview(self, obj):
        content = obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return content
    content_preview.short_description = 'Contenu'
    
    fieldsets = (
        ('Message', {
            'fields': ('room', 'sender', 'content', 'message_type', 'reply_to')
        }),
        ('Médias', {
            'fields': ('attachment', 'attachment_type'),
            'classes': ('collapse',)
        }),
        ('Réactions', {
            'fields': ('reactions', 'reaction_count'),
            'classes': ('collapse',)
        }),
        ('Statut', {
            'fields': ('is_deleted', 'deleted_at', 'deleted_by')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ChatParticipant)
class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'room_link', 'joined_at']
    list_filter = ['joined_at']
    search_fields = ['user__first_name', 'user__last_name']
    readonly_fields = ['joined_at']
    raw_id_fields = ['user', 'room']
    
    def room_link(self, obj):
        url = reverse('admin:chat_chatroom_change', args=[obj.room.id])
        return format_html('<a href="{}">{}</a>', url, obj.room.title)
    room_link.short_description = 'Salle de chat'


@admin.register(ChatNotification)
class ChatNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'room_link', 'notification_type', 'title', 
        'is_read', 'created_at'
    ]
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'content', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'read_at']
    raw_id_fields = ['user', 'room', 'message']
    
    def room_link(self, obj):
        if obj.room:
            url = reverse('admin:chat_chatroom_change', args=[obj.room.id])
            return format_html('<a href="{}">{}</a>', url, obj.room.title)
        return '-'
    room_link.short_description = 'Salle de chat'


@admin.register(ChatSettings)
class ChatSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Notifications', {
            'fields': ('notifications_enabled', 'email_notifications', 'push_notifications')
        }),
        ('Interface', {
            'fields': ('sound_enabled', 'theme', 'messages_per_page')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ChatBlock)
class ChatBlockAdmin(admin.ModelAdmin):
    list_display = ['id', 'blocker', 'blocked', 'created_at']
    list_filter = ['created_at']
    search_fields = ['blocker__first_name', 'blocker__last_name', 
                    'blocked__first_name', 'blocked__last_name']
    readonly_fields = ['created_at']
    raw_id_fields = ['blocker', 'blocked']


@admin.register(ChatReport)
class ChatReportAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'reporter', 'reported_user', 'report_type', 'created_at'
    ]
    list_filter = ['report_type', 'created_at']
    search_fields = ['reporter__first_name', 'reporter__last_name', 
                    'reported_user__first_name', 'reported_user__last_name']
    readonly_fields = ['created_at']
    raw_id_fields = ['reporter', 'reported_user']
    
    fieldsets = (
        ('Signalement', {
            'fields': ('reporter', 'reported_user', 'report_type', 'description')
        }),
        ('Statut', {
            'fields': ('status', 'admin_notes')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_resolved', 'mark_as_invalid']
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='resolved')
        self.message_user(request, f'{queryset.count()} signalements marqués comme résolus.')
    mark_as_resolved.short_description = 'Marquer comme résolu'
    
    def mark_as_invalid(self, request, queryset):
        queryset.update(status='invalid')
        self.message_user(request, f'{queryset.count()} signalements marqués comme invalides.')
    mark_as_invalid.short_description = 'Marquer comme invalide'
