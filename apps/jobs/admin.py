from django.contrib import admin
from django.utils.html import format_html
from .models import JobCategory, Job, JobSkill, SavedJob, JobAlert


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'jobs_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {}

    def jobs_count(self, obj):
        return obj.jobs.count()
    jobs_count.short_description = 'Nombre d\'offres'


class JobSkillInline(admin.TabularInline):
    model = JobSkill
    extra = 1


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'company', 'category', 'job_type', 'status', 
        'applications_count', 'views_count', 'created_at'
    )
    list_filter = (
        'status', 'job_type', 'experience_level', 'category', 
        'remote_work', 'featured', 'urgent', 'created_at'
    )
    search_fields = ('title', 'company', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'applications_count', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'company', 'category', 'slug')
        }),
        ('Type et niveau', {
            'fields': ('job_type', 'experience_level')
        }),
        ('Localisation', {
            'fields': ('location', 'remote_work')
        }),
        ('Description', {
            'fields': ('description', 'requirements', 'responsibilities', 'benefits')
        }),
        ('Salaire', {
            'fields': ('salary_min', 'salary_max', 'salary_currency', 'salary_period')
        }),
        ('Statut et options', {
            'fields': ('status', 'featured', 'urgent')
        }),
        ('Dates', {
            'fields': ('application_deadline', 'start_date')
        }),
        ('Gestion', {
            'fields': ('created_by',)
        }),
        ('Statistiques', {
            'fields': ('views_count', 'applications_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [JobSkillInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle offre
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'created_by')


@admin.register(JobSkill)
class JobSkillAdmin(admin.ModelAdmin):
    list_display = ('job', 'skill_name', 'level', 'years_required')
    list_filter = ('level', 'years_required')
    search_fields = ('job__title', 'skill_name')


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__first_name', 'user__last_name', 'job__title')
    date_hierarchy = 'saved_at'


@admin.register(JobAlert)
class JobAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'job_type', 'is_active', 'email_frequency', 'created_at')
    list_filter = ('is_active', 'job_type', 'experience_level', 'email_frequency', 'created_at')
    search_fields = ('title', 'user__first_name', 'user__last_name', 'keywords')
    readonly_fields = ('created_at', 'last_sent')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'title', 'is_active')
        }),
        ('Critères de recherche', {
            'fields': ('keywords', 'location', 'category', 'job_type', 'experience_level', 'salary_min', 'remote_work')
        }),
        ('Notifications', {
            'fields': ('email_frequency', 'last_sent')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )