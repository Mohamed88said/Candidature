from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Company, CompanyReview, ReviewHelpful, ReviewResponse,
    CompanySalary, CompanyInterview, CompanyBenefit, CompanyPhoto, CompanyFollow
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'industry', 'size', 'is_verified', 'is_active', 'created_at']
    list_filter = ['industry', 'size', 'is_verified', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'industry', 'headquarters']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'slug', 'description', 'website')
        }),
        ('Détails', {
            'fields': ('industry', 'size', 'founded_year', 'headquarters')
        }),
        ('Contact', {
            'fields': ('email', 'phone')
        }),
        ('Médias', {
            'fields': ('logo', 'cover_image')
        }),
        ('Statut', {
            'fields': ('is_verified', 'is_active')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(CompanyReview)
class CompanyReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'job_title', 'overall_rating', 'is_approved', 'created_at']
    list_filter = ['overall_rating', 'employment_status', 'is_approved', 'is_anonymous', 'created_at']
    search_fields = ['user__username', 'company__name', 'job_title', 'pros', 'cons']
    raw_id_fields = ['user', 'company']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'company', 'job_title', 'employment_status')
        }),
        ('Dates d\'emploi', {
            'fields': ('employment_start_date', 'employment_end_date', 'is_current_employee')
        }),
        ('Notes', {
            'fields': ('overall_rating', 'work_life_balance', 'salary_benefits', 'job_security', 'management', 'culture', 'career_opportunities')
        }),
        ('Contenu', {
            'fields': ('pros', 'cons', 'advice_to_management', 'would_recommend')
        }),
        ('Statut', {
            'fields': ('is_approved', 'is_anonymous')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'company')


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ['user', 'review', 'is_helpful', 'created_at']
    list_filter = ['is_helpful', 'created_at']
    search_fields = ['user__username', 'review__company__name']
    raw_id_fields = ['user', 'review']
    readonly_fields = ['created_at']


@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    list_display = ['review', 'company_representative', 'created_at']
    list_filter = ['created_at']
    search_fields = ['review__company__name', 'company_representative__username']
    raw_id_fields = ['review', 'company_representative']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CompanySalary)
class CompanySalaryAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'job_title', 'base_salary', 'currency', 'is_approved', 'created_at']
    list_filter = ['currency', 'employment_type', 'experience_level', 'is_approved', 'is_anonymous', 'created_at']
    search_fields = ['user__username', 'company__name', 'job_title', 'department']
    raw_id_fields = ['user', 'company']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'company', 'job_title', 'department', 'location')
        }),
        ('Rémunération', {
            'fields': ('base_salary', 'bonus', 'total_compensation', 'currency')
        }),
        ('Détails de l\'emploi', {
            'fields': ('employment_type', 'experience_level', 'years_at_company')
        }),
        ('Statut', {
            'fields': ('is_approved', 'is_anonymous')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(CompanyInterview)
class CompanyInterviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'job_title', 'difficulty', 'outcome', 'is_approved', 'created_at']
    list_filter = ['difficulty', 'outcome', 'is_approved', 'is_anonymous', 'created_at']
    search_fields = ['user__username', 'company__name', 'job_title', 'department']
    raw_id_fields = ['user', 'company']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'company', 'job_title', 'department')
        }),
        ('Détails de l\'entretien', {
            'fields': ('interview_date', 'interview_type', 'difficulty', 'duration')
        }),
        ('Contenu', {
            'fields': ('interview_questions', 'interview_process')
        }),
        ('Résultat', {
            'fields': ('outcome', 'offer_made', 'offer_amount')
        }),
        ('Avis', {
            'fields': ('overall_experience', 'pros', 'cons', 'advice')
        }),
        ('Statut', {
            'fields': ('is_approved', 'is_anonymous')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(CompanyBenefit)
class CompanyBenefitAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'category', 'is_available', 'created_at']
    list_filter = ['category', 'is_available', 'created_at']
    search_fields = ['name', 'company__name', 'description']
    raw_id_fields = ['company']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CompanyPhoto)
class CompanyPhotoAdmin(admin.ModelAdmin):
    list_display = ['company', 'user', 'caption', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['company__name', 'user__username', 'caption']
    raw_id_fields = ['company', 'user']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company', 'user')


@admin.register(CompanyFollow)
class CompanyFollowAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'company__name']
    raw_id_fields = ['user', 'company']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'company')