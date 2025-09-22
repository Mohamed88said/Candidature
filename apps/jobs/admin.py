from django.contrib import admin
from django.utils.html import format_html
from .models import JobCategory, Job, JobSkill, SavedJob, JobAlert
from django.utils.text import slugify
import uuid


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
        'applications_count', 'views_count', 'created_at', 'slug_preview'
    )
    list_filter = (
        'status', 'job_type', 'experience_level', 'category', 
        'remote_work', 'featured', 'urgent', 'created_at'
    )
    search_fields = ('title', 'company', 'description', 'location', 'slug')
    readonly_fields = ('views_count', 'applications_count', 'created_at', 'updated_at', 'slug')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'company', 'category')
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
        ('SEO et Slug', {
            'fields': ('slug',),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('views_count', 'applications_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [JobSkillInline]
    
    def slug_preview(self, obj):
        return obj.slug[:30] + '...' if obj.slug and len(obj.slug) > 30 else obj.slug
    slug_preview.short_description = 'Slug'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle offre
            obj.created_by = request.user
        
        # Générer un slug si nécessaire
        if not obj.slug or (change and 'title' in form.changed_data):
            base_slug = slugify(obj.title)
            if not base_slug:
                base_slug = "offre-emploi"
            obj.slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        
        # Vérifier l'unicité du slug
        if Job.objects.filter(slug=obj.slug).exclude(id=obj.id).exists():
            obj.slug = f"{obj.slug}-{str(uuid.uuid4())[:4]}"
        
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
