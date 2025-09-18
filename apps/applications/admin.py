from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Application, ApplicationRating, ApplicationComment, 
    Interview, ApplicationStatusHistory, ApplicationDocument
)


class ApplicationRatingInline(admin.TabularInline):
    model = ApplicationRating
    extra = 0
    readonly_fields = ('created_at',)


class ApplicationCommentInline(admin.TabularInline):
    model = ApplicationComment
    extra = 1
    readonly_fields = ('created_at', 'updated_at')


class InterviewInline(admin.TabularInline):
    model = Interview
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


class ApplicationStatusHistoryInline(admin.TabularInline):
    model = ApplicationStatusHistory
    extra = 0
    readonly_fields = ('changed_at',)


class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 0
    readonly_fields = ('uploaded_at', 'file_size_mb')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'candidate_name', 'job_title', 'status', 'priority', 
        'applied_at', 'days_since_applied', 'reviewed_status'
    )
    list_filter = (
        'status', 'priority', 'applied_at', 'job__category', 
        'willing_to_relocate', 'reviewed_by'
    )
    search_fields = (
        'candidate__user__first_name', 'candidate__user__last_name',
        'candidate__user__email', 'job__title', 'job__company'
    )
    readonly_fields = ('applied_at', 'updated_at', 'days_since_applied')
    date_hierarchy = 'applied_at'
    
    fieldsets = (
        ('Candidature', {
            'fields': ('candidate', 'job', 'status', 'priority')
        }),
        ('Documents et motivation', {
            'fields': ('cover_letter', 'resume_file', 'additional_documents')
        }),
        ('Informations supplémentaires', {
            'fields': ('expected_salary', 'availability_date', 'willing_to_relocate', 'custom_answers')
        }),
        ('Suivi RH', {
            'fields': ('reviewed_by', 'reviewed_at')
        }),
        ('Métadonnées', {
            'fields': ('applied_at', 'updated_at', 'days_since_applied'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [
        ApplicationRatingInline, ApplicationCommentInline, 
        InterviewInline, ApplicationStatusHistoryInline, ApplicationDocumentInline
    ]
    
    def candidate_name(self, obj):
        return obj.candidate.user.full_name
    candidate_name.short_description = 'Candidat'
    candidate_name.admin_order_field = 'candidate__user__last_name'
    
    def job_title(self, obj):
        return f"{obj.job.title} - {obj.job.company}"
    job_title.short_description = 'Offre d\'emploi'
    job_title.admin_order_field = 'job__title'
    
    def reviewed_status(self, obj):
        if obj.reviewed_by:
            return format_html(
                '<span style="color: green;">✓ Examiné par {}</span>',
                obj.reviewed_by.full_name
            )
        return format_html('<span style="color: orange;">En attente d\'examen</span>')
    reviewed_status.short_description = 'Statut d\'examen'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'candidate__user', 'job', 'reviewed_by'
        )


@admin.register(ApplicationRating)
class ApplicationRatingAdmin(admin.ModelAdmin):
    list_display = ('application', 'evaluator', 'criteria', 'score', 'max_score', 'score_percentage', 'created_at')
    list_filter = ('criteria', 'score', 'max_score', 'created_at')
    search_fields = (
        'application__candidate__user__first_name',
        'application__candidate__user__last_name',
        'application__job__title'
    )
    readonly_fields = ('created_at', 'score_percentage')


@admin.register(ApplicationComment)
class ApplicationCommentAdmin(admin.ModelAdmin):
    list_display = ('application', 'author', 'comment_type', 'is_internal', 'created_at')
    list_filter = ('comment_type', 'is_internal', 'created_at')
    search_fields = (
        'application__candidate__user__first_name',
        'application__candidate__user__last_name',
        'content'
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = (
        'application', 'interview_type', 'status', 'scheduled_date', 
        'duration_minutes', 'overall_rating', 'recommendation'
    )
    list_filter = ('interview_type', 'status', 'scheduled_date', 'recommendation')
    search_fields = (
        'application__candidate__user__first_name',
        'application__candidate__user__last_name',
        'application__job__title'
    )
    readonly_fields = ('created_at', 'updated_at', 'is_upcoming', 'is_overdue')
    date_hierarchy = 'scheduled_date'
    filter_horizontal = ('interviewers',)
    
    fieldsets = (
        ('Entretien', {
            'fields': ('application', 'interview_type', 'status')
        }),
        ('Planification', {
            'fields': ('scheduled_date', 'duration_minutes', 'location', 'interviewers')
        }),
        ('Évaluation', {
            'fields': ('notes', 'overall_rating', 'recommendation')
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at', 'is_upcoming', 'is_overdue'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('application', 'previous_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('previous_status', 'new_status', 'changed_at')
    search_fields = (
        'application__candidate__user__first_name',
        'application__candidate__user__last_name',
        'reason'
    )
    readonly_fields = ('changed_at',)
    date_hierarchy = 'changed_at'


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'application', 'document_type', 'uploaded_by', 'file_size_mb', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = (
        'title', 'application__candidate__user__first_name',
        'application__candidate__user__last_name'
    )
    readonly_fields = ('uploaded_at', 'file_size_mb')