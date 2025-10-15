from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    AlertPreference, AlertType, AlertNotification, AlertTemplate, 
    AlertCampaign, AlertAnalytics, AlertSubscription
)


@admin.register(AlertType)
class AlertTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'icon', 'color_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Couleur'


@admin.register(AlertPreference)
class AlertPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'email_alerts', 'push_notifications', 'sms_alerts', 
        'frequency', 'max_alerts_per_day', 'updated_at'
    ]
    list_filter = ['email_alerts', 'push_notifications', 'sms_alerts', 'frequency', 'updated_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Préférences de notification', {
            'fields': ('email_alerts', 'push_notifications', 'sms_alerts', 'frequency', 'max_alerts_per_day')
        }),
        ('Filtres de contenu', {
            'fields': ('include_salary', 'include_remote_jobs', 'include_part_time', 'include_internships')
        }),
        ('Filtres géographiques', {
            'fields': ('max_distance', 'preferred_locations')
        }),
        ('Filtres de salaire', {
            'fields': ('min_salary', 'max_salary')
        }),
        ('Filtres d\'expérience', {
            'fields': ('min_experience', 'max_experience')
        }),
        ('Préférences', {
            'fields': ('preferred_job_types', 'preferred_industries', 'preferred_skills', 'enabled_alert_types')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AlertNotification)
class AlertNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'job', 'alert_type', 'match_score', 'status', 
        'email_sent', 'push_sent', 'sms_sent', 'created_at'
    ]
    list_filter = ['status', 'alert_type', 'email_sent', 'push_sent', 'sms_sent', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'job__title', 'title']
    readonly_fields = ['created_at', 'updated_at', 'sent_at', 'delivered_at', 'opened_at', 'clicked_at']
    raw_id_fields = ['user', 'job', 'alert_type']
    
    fieldsets = (
        ('Alerte', {
            'fields': ('user', 'job', 'alert_type', 'title', 'message')
        }),
        ('Correspondance', {
            'fields': ('match_score', 'match_reasons')
        }),
        ('Statut', {
            'fields': ('status',)
        }),
        ('Livraison', {
            'fields': ('email_sent', 'push_sent', 'sms_sent')
        }),
        ('Horodatage', {
            'fields': ('sent_at', 'delivered_at', 'opened_at', 'clicked_at'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_sent', 'mark_as_delivered', 'mark_as_opened', 'mark_as_clicked']
    
    def mark_as_sent(self, request, queryset):
        for alert in queryset:
            alert.mark_as_sent()
        self.message_user(request, f'{queryset.count()} alertes marquées comme envoyées.')
    mark_as_sent.short_description = 'Marquer comme envoyées'
    
    def mark_as_delivered(self, request, queryset):
        for alert in queryset:
            alert.mark_as_delivered()
        self.message_user(request, f'{queryset.count()} alertes marquées comme livrées.')
    mark_as_delivered.short_description = 'Marquer comme livrées'
    
    def mark_as_opened(self, request, queryset):
        for alert in queryset:
            alert.mark_as_opened()
        self.message_user(request, f'{queryset.count()} alertes marquées comme ouvertes.')
    mark_as_opened.short_description = 'Marquer comme ouvertes'
    
    def mark_as_clicked(self, request, queryset):
        for alert in queryset:
            alert.mark_as_clicked()
        self.message_user(request, f'{queryset.count()} alertes marquées comme cliquées.')
    mark_as_clicked.short_description = 'Marquer comme cliquées'


@admin.register(AlertTemplate)
class AlertTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'alert_type', 'is_active', 'is_default', 'created_at']
    list_filter = ['alert_type', 'is_active', 'is_default', 'created_at']
    search_fields = ['name', 'subject_template', 'message_template']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['alert_type']
    
    fieldsets = (
        ('Template', {
            'fields': ('name', 'alert_type', 'is_active', 'is_default')
        }),
        ('Contenu', {
            'fields': ('subject_template', 'message_template', 'html_template')
        }),
        ('Configuration', {
            'fields': ('available_variables',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AlertCampaign)
class AlertCampaignAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'alert_type', 'status', 'scheduled_at', 
        'total_recipients', 'emails_sent', 'created_by', 'created_at'
    ]
    list_filter = ['status', 'alert_type', 'scheduled_at', 'created_at']
    search_fields = ['name', 'description', 'created_by__first_name', 'created_by__last_name']
    readonly_fields = ['created_at', 'updated_at', 'started_at', 'completed_at']
    raw_id_fields = ['created_by', 'alert_type']
    
    fieldsets = (
        ('Campagne', {
            'fields': ('name', 'description', 'alert_type', 'status')
        }),
        ('Ciblage', {
            'fields': ('target_users', 'target_criteria')
        }),
        ('Contenu', {
            'fields': ('subject', 'message', 'html_content')
        }),
        ('Planification', {
            'fields': ('scheduled_at', 'started_at', 'completed_at')
        }),
        ('Statistiques', {
            'fields': ('total_recipients', 'emails_sent', 'emails_delivered', 'emails_opened', 'emails_clicked'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['start_campaign', 'stop_campaign']
    
    def start_campaign(self, request, queryset):
        for campaign in queryset:
            if campaign.status == 'scheduled':
                campaign.status = 'running'
                campaign.started_at = timezone.now()
                campaign.save()
        self.message_user(request, f'{queryset.count()} campagnes démarrées.')
    start_campaign.short_description = 'Démarrer les campagnes'
    
    def stop_campaign(self, request, queryset):
        for campaign in queryset:
            if campaign.status == 'running':
                campaign.status = 'completed'
                campaign.completed_at = timezone.now()
                campaign.save()
        self.message_user(request, f'{queryset.count()} campagnes arrêtées.')
    stop_campaign.short_description = 'Arrêter les campagnes'


@admin.register(AlertAnalytics)
class AlertAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'total_alerts_sent', 'total_alerts_delivered', 
        'total_alerts_opened', 'total_alerts_clicked', 'delivery_rate', 'open_rate', 'click_rate'
    ]
    list_filter = ['date']
    search_fields = ['date']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Analytics', {
            'fields': ('date',)
        }),
        ('Statistiques générales', {
            'fields': ('total_alerts_sent', 'total_alerts_delivered', 'total_alerts_opened', 'total_alerts_clicked')
        }),
        ('Statistiques par type', {
            'fields': ('alerts_by_type',)
        }),
        ('Statistiques par canal', {
            'fields': ('email_alerts_sent', 'push_alerts_sent', 'sms_alerts_sent')
        }),
        ('Taux de conversion', {
            'fields': ('delivery_rate', 'open_rate', 'click_rate')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(AlertSubscription)
class AlertSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'alert_type', 'frequency', 'is_active', 
        'total_alerts_received', 'last_alert_sent', 'created_at'
    ]
    list_filter = ['alert_type', 'frequency', 'is_active', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'keywords', 'locations']
    readonly_fields = ['created_at', 'updated_at', 'total_alerts_received', 'last_alert_sent']
    raw_id_fields = ['user', 'alert_type']
    
    fieldsets = (
        ('Abonnement', {
            'fields': ('user', 'alert_type', 'frequency', 'is_active')
        }),
        ('Critères', {
            'fields': ('keywords', 'locations', 'job_types', 'industries', 'salary_range')
        }),
        ('Statistiques', {
            'fields': ('total_alerts_received', 'last_alert_sent')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )