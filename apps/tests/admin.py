from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Test, TestCategory, JobTest, TestAttempt, TestResult, 
    TestCertificate, TestAnalytics
)


@admin.register(TestCategory)
class TestCategoryAdmin(admin.ModelAdmin):
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


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'difficulty', 'status', 'total_questions', 
        'passing_score', 'total_attempts', 'average_score', 'created_by', 'created_at'
    ]
    list_filter = ['category', 'difficulty', 'status', 'created_at']
    search_fields = ['title', 'description', 'created_by__first_name', 'created_by__last_name']
    readonly_fields = ['created_at', 'updated_at', 'total_questions', 'total_points', 'total_attempts', 'average_score', 'completion_rate']
    raw_id_fields = ['created_by']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'description', 'category', 'difficulty', 'status')
        }),
        ('Configuration', {
            'fields': ('time_limit', 'max_attempts', 'passing_score')
        }),
        ('Questions', {
            'fields': ('questions',),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('total_questions', 'total_points', 'total_attempts', 'average_score', 'completion_rate'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Nouveau test
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(JobTest)
class JobTestAdmin(admin.ModelAdmin):
    list_display = ['job', 'test', 'is_required', 'order', 'created_at']
    list_filter = ['is_required', 'created_at']
    search_fields = ['job__title', 'test__title']
    readonly_fields = ['created_at']
    raw_id_fields = ['job', 'test']


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = [
        'candidate', 'test', 'status', 'score', 'percentage', 'passed', 
        'started_at', 'completed_at', 'time_spent'
    ]
    list_filter = ['status', 'passed', 'started_at', 'test__category']
    search_fields = ['candidate__first_name', 'candidate__last_name', 'test__title']
    readonly_fields = ['started_at', 'completed_at', 'time_spent', 'score', 'percentage', 'passed']
    raw_id_fields = ['candidate', 'test', 'job']
    
    fieldsets = (
        ('Tentative', {
            'fields': ('candidate', 'test', 'job', 'status')
        }),
        ('Progression', {
            'fields': ('current_question', 'answers')
        }),
        ('Résultats', {
            'fields': ('score', 'percentage', 'passed')
        }),
        ('Temps', {
            'fields': ('started_at', 'completed_at', 'time_spent')
        }),
        ('Métadonnées', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_abandoned']
    
    def mark_as_completed(self, request, queryset):
        for attempt in queryset:
            if attempt.status == 'in_progress':
                attempt.status = 'completed'
                attempt.completed_at = timezone.now()
                attempt.save()
        self.message_user(request, f'{queryset.count()} tentatives marquées comme terminées.')
    mark_as_completed.short_description = 'Marquer comme terminé'
    
    def mark_as_abandoned(self, request, queryset):
        for attempt in queryset:
            if attempt.status == 'in_progress':
                attempt.status = 'abandoned'
                attempt.save()
        self.message_user(request, f'{queryset.count()} tentatives marquées comme abandonnées.')
    mark_as_abandoned.short_description = 'Marquer comme abandonné'


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'correct_answers', 'incorrect_answers', 'skipped_questions', 'created_at']
    list_filter = ['created_at']
    search_fields = ['attempt__candidate__first_name', 'attempt__candidate__last_name', 'attempt__test__title']
    readonly_fields = ['created_at']
    raw_id_fields = ['attempt']
    
    fieldsets = (
        ('Résultat', {
            'fields': ('attempt',)
        }),
        ('Statistiques', {
            'fields': ('correct_answers', 'incorrect_answers', 'skipped_questions')
        }),
        ('Analyse', {
            'fields': ('question_results', 'strengths', 'weaknesses', 'recommendations'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(TestCertificate)
class TestCertificateAdmin(admin.ModelAdmin):
    list_display = [
        'certificate_number', 'attempt', 'issued_at', 'expires_at', 'is_valid'
    ]
    list_filter = ['is_valid', 'issued_at', 'expires_at']
    search_fields = ['certificate_number', 'attempt__candidate__first_name', 'attempt__candidate__last_name']
    readonly_fields = ['certificate_number', 'issued_at']
    raw_id_fields = ['attempt']
    
    fieldsets = (
        ('Certificat', {
            'fields': ('attempt', 'certificate_number', 'certificate_file')
        }),
        ('Validité', {
            'fields': ('issued_at', 'expires_at', 'is_valid')
        }),
    )
    
    actions = ['invalidate_certificates', 'extend_certificates']
    
    def invalidate_certificates(self, request, queryset):
        queryset.update(is_valid=False)
        self.message_user(request, f'{queryset.count()} certificats invalidés.')
    invalidate_certificates.short_description = 'Invalider les certificats'
    
    def extend_certificates(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        
        for certificate in queryset:
            certificate.expires_at = timezone.now() + timedelta(days=365)
            certificate.save()
        self.message_user(request, f'{queryset.count()} certificats étendus d\'un an.')
    extend_certificates.short_description = 'Étendre les certificats d\'un an'


@admin.register(TestAnalytics)
class TestAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'test', 'date', 'total_attempts', 'completed_attempts', 
        'passed_attempts', 'average_score', 'average_time'
    ]
    list_filter = ['date', 'test__category']
    search_fields = ['test__title']
    readonly_fields = ['created_at']
    raw_id_fields = ['test']
    
    fieldsets = (
        ('Analytics', {
            'fields': ('test', 'date')
        }),
        ('Statistiques', {
            'fields': ('total_attempts', 'completed_attempts', 'passed_attempts', 'average_score', 'average_time')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )