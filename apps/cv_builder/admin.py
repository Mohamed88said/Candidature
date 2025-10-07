from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    CV, CVTemplate, CVSection, CVShare, CVExport, 
    CVFeedback, CVBuilderSettings, CVAnalytics, CVTemplateCategory
)


@admin.register(CVTemplate)
class CVTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'preview_image_display', 'is_premium', 
        'is_active', 'cv_count', 'created_at'
    ]
    list_filter = ['category', 'is_premium', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'preview_image_display']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'description', 'category')
        }),
        ('Fichiers', {
            'fields': ('preview_image', 'preview_image_display', 'template_file', 'css_file')
        }),
        ('Configuration', {
            'fields': ('sections', 'layout_config', 'color_scheme')
        }),
        ('Options', {
            'fields': ('is_premium', 'is_active')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def preview_image_display(self, obj):
        if obj.preview_image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px;" />',
                obj.preview_image.url
            )
        return '-'
    preview_image_display.short_description = 'Aperçu'
    
    def cv_count(self, obj):
        return obj.cvs.count()
    cv_count.short_description = 'CVs créés'


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'template', 'status', 'is_public',
        'view_count', 'download_count', 'last_modified'
    ]
    list_filter = ['status', 'is_public', 'template', 'created_at', 'last_modified']
    search_fields = ['title', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at', 'last_modified', 'view_count', 'download_count']
    raw_id_fields = ['user', 'template']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'template', 'title', 'status', 'is_public')
        }),
        ('Contenu', {
            'fields': ('professional_summary', 'personal_info', 'experience', 
                      'education', 'skills', 'projects', 'languages', 
                      'certifications', 'references', 'additional_sections')
        }),
        ('Personnalisation', {
            'fields': ('custom_colors', 'custom_fonts', 'layout_settings')
        }),
        ('Statistiques', {
            'fields': ('view_count', 'download_count')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'last_modified'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CVSection)
class CVSectionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'cv', 'section_type', 'order', 'is_visible', 'created_at'
    ]
    list_filter = ['section_type', 'is_visible', 'created_at']
    search_fields = ['title', 'cv__title', 'cv__user__first_name', 'cv__user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['cv']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('cv', 'section_type', 'title', 'order', 'is_visible')
        }),
        ('Contenu', {
            'fields': ('content',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CVShare)
class CVShareAdmin(admin.ModelAdmin):
    list_display = [
        'cv', 'share_type', 'share_url', 'view_count', 'download_count',
        'expires_at', 'is_expired', 'created_at'
    ]
    list_filter = ['share_type', 'created_at', 'expires_at']
    search_fields = ['cv__title', 'cv__user__first_name', 'cv__user__last_name', 'share_url']
    readonly_fields = ['created_at', 'updated_at', 'share_url', 'is_expired']
    raw_id_fields = ['cv']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('cv', 'share_type', 'share_url')
        }),
        ('Sécurité', {
            'fields': ('password', 'expires_at')
        }),
        ('Statistiques', {
            'fields': ('view_count', 'download_count')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'is_expired'),
            'classes': ('collapse',)
        }),
    )
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expiré'


@admin.register(CVExport)
class CVExportAdmin(admin.ModelAdmin):
    list_display = [
        'cv', 'export_format', 'file_size_display', 'created_at'
    ]
    list_filter = ['export_format', 'created_at']
    search_fields = ['cv__title', 'cv__user__first_name', 'cv__user__last_name']
    readonly_fields = ['created_at']
    raw_id_fields = ['cv']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('cv', 'export_format', 'file_path', 'file_size')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def file_size_display(self, obj):
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} B"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return '-'
    file_size_display.short_description = 'Taille'


@admin.register(CVFeedback)
class CVFeedbackAdmin(admin.ModelAdmin):
    list_display = [
        'cv', 'reviewer', 'rating', 'is_public', 'created_at'
    ]
    list_filter = ['rating', 'is_public', 'created_at']
    search_fields = ['cv__title', 'reviewer__first_name', 'reviewer__last_name', 'comment']
    readonly_fields = ['created_at']
    raw_id_fields = ['cv', 'reviewer']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('cv', 'reviewer', 'rating', 'is_public')
        }),
        ('Commentaire', {
            'fields': ('comment',)
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CVBuilderSettings)
class CVBuilderSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'default_template', 'auto_save', 'default_export_format',
        'default_share_type', 'created_at'
    ]
    list_filter = ['auto_save', 'default_export_format', 'default_share_type', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'default_template']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Paramètres d\'interface', {
            'fields': ('default_template', 'auto_save', 'auto_save_interval')
        }),
        ('Paramètres d\'export', {
            'fields': ('default_export_format', 'include_contact_info', 'include_photo')
        }),
        ('Paramètres de partage', {
            'fields': ('default_share_type', 'share_expiry_days')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CVAnalytics)
class CVAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'cv', 'date', 'views', 'downloads', 'shares'
    ]
    list_filter = ['date', 'created_at']
    search_fields = ['cv__title', 'cv__user__first_name', 'cv__user__last_name']
    readonly_fields = ['created_at']
    raw_id_fields = ['cv']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('cv', 'date')
        }),
        ('Statistiques', {
            'fields': ('views', 'downloads', 'shares')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CVTemplateCategory)
class CVTemplateCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'color_display', 'is_active', 'template_count', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'color_display']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'description', 'icon')
        }),
        ('Apparence', {
            'fields': ('color', 'color_display')
        }),
        ('Options', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 2px 8px; border-radius: 4px; color: white;">{}</span>',
            obj.color, obj.color
        )
    color_display.short_description = 'Couleur'
    
    def template_count(self, obj):
        return CVTemplate.objects.filter(category=obj.name).count()
    template_count.short_description = 'Modèles'