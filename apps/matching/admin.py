from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    MatchingAlgorithm, JobMatch, CandidatePreference, 
    MatchingHistory, SkillSimilarity, IndustrySimilarity
)


@admin.register(MatchingAlgorithm)
class MatchingAlgorithmAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'minimum_match_score', 'high_match_threshold', 'created_at']
    list_filter = ['is_active', 'use_ai_analysis', 'consider_soft_skills']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Poids des critères (%)', {
            'fields': (
                'experience_weight', 'skills_weight', 'location_weight',
                'salary_weight', 'education_weight', 'company_culture_weight'
            ),
            'description': 'La somme des poids ne doit pas dépasser 100%'
        }),
        ('Seuils de matching', {
            'fields': ('minimum_match_score', 'high_match_threshold')
        }),
        ('Configuration avancée', {
            'fields': ('use_ai_analysis', 'consider_soft_skills', 'location_radius_km')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')


@admin.register(JobMatch)
class JobMatchAdmin(admin.ModelAdmin):
    list_display = [
        'candidate_name', 'job_title', 'company_name', 'overall_score', 
        'match_level_display', 'candidate_interest', 'is_viewed_by_candidate', 'created_at'
    ]
    list_filter = [
        'overall_score', 'candidate_interest', 'is_viewed_by_candidate', 
        'is_viewed_by_recruiter', 'algorithm', 'created_at'
    ]
    search_fields = [
        'candidate__user__first_name', 'candidate__user__last_name', 
        'candidate__user__email', 'job__title', 'job__company'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'match_level_display', 'detailed_scores'
    ]
    raw_id_fields = ['candidate', 'job']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('candidate', 'job', 'algorithm', 'overall_score')
        }),
        ('Scores détaillés', {
            'fields': (
                'experience_score', 'skills_score', 'location_score',
                'salary_score', 'education_score', 'culture_score'
            ),
            'classes': ('collapse',)
        }),
        ('Analyse détaillée', {
            'fields': ('matching_skills', 'missing_skills', 'strengths', 'concerns', 'recommendations'),
            'classes': ('collapse',)
        }),
        ('Statut et intérêt', {
            'fields': (
                'is_viewed_by_candidate', 'is_viewed_by_recruiter', 
                'candidate_interest'
            )
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def candidate_name(self, obj):
        return obj.candidate.user.full_name
    candidate_name.short_description = 'Candidat'
    candidate_name.admin_order_field = 'candidate__user__first_name'
    
    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Poste'
    job_title.admin_order_field = 'job__title'
    
    def company_name(self, obj):
        return obj.job.company
    company_name.short_description = 'Entreprise'
    company_name.admin_order_field = 'job__company'
    
    def match_level_display(self, obj):
        level_colors = {
            'excellent': 'green',
            'très_bon': 'blue',
            'bon': 'orange',
            'correct': 'yellow',
            'faible': 'red'
        }
        color = level_colors.get(obj.match_level, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.match_level_display
        )
    match_level_display.short_description = 'Niveau'
    
    def detailed_scores(self, obj):
        scores = [
            f"Expérience: {obj.experience_score}%",
            f"Compétences: {obj.skills_score}%",
            f"Localisation: {obj.location_score}%",
            f"Salaire: {obj.salary_score}%",
            f"Éducation: {obj.education_score}%",
            f"Culture: {obj.culture_score}%"
        ]
        return mark_safe('<br>'.join(scores))
    detailed_scores.short_description = 'Scores détaillés'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'candidate__user', 'job', 'algorithm'
        ).order_by('-overall_score', '-created_at')


@admin.register(CandidatePreference)
class CandidatePreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'candidate_name', 'alert_frequency', 'min_match_score', 
        'willing_to_relocate', 'remote_work_preference', 'updated_at'
    ]
    list_filter = [
        'alert_frequency', 'willing_to_relocate', 'remote_work_preference',
        'only_high_matches', 'updated_at'
    ]
    search_fields = [
        'candidate__user__first_name', 'candidate__user__last_name', 
        'candidate__user__email'
    ]
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['candidate']
    
    fieldsets = (
        ('Candidat', {
            'fields': ('candidate',)
        }),
        ('Préférences de localisation', {
            'fields': (
                'preferred_locations', 'max_commute_time', 'willing_to_relocate',
                'remote_work_preference'
            )
        }),
        ('Préférences salariales', {
            'fields': ('min_salary', 'max_salary', 'salary_negotiable')
        }),
        ('Préférences d\'entreprise', {
            'fields': (
                'preferred_company_sizes', 'preferred_industries', 
                'preferred_company_cultures'
            )
        }),
        ('Préférences de poste', {
            'fields': (
                'preferred_job_types', 'preferred_experience_levels', 
                'career_goals'
            )
        }),
        ('Critères d\'exclusion', {
            'fields': ('excluded_companies', 'excluded_locations', 'excluded_industries'),
            'classes': ('collapse',)
        }),
        ('Configuration des alertes', {
            'fields': ('alert_frequency', 'min_match_score', 'only_high_matches')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def candidate_name(self, obj):
        return obj.candidate.user.full_name
    candidate_name.short_description = 'Candidat'
    candidate_name.admin_order_field = 'candidate__user__first_name'


@admin.register(MatchingHistory)
class MatchingHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'candidate_name', 'job_title', 'overall_score', 
        'candidate_action', 'recruiter_action', 'final_outcome', 'created_at'
    ]
    list_filter = [
        'candidate_action', 'recruiter_action', 'final_outcome',
        'algorithm_version', 'created_at'
    ]
    search_fields = [
        'candidate__user__first_name', 'candidate__user__last_name',
        'job__title', 'job__company'
    ]
    readonly_fields = ['created_at']
    raw_id_fields = ['candidate', 'job']
    
    def candidate_name(self, obj):
        return obj.candidate.user.full_name
    candidate_name.short_description = 'Candidat'
    
    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Poste'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'candidate__user', 'job'
        ).order_by('-created_at')


@admin.register(SkillSimilarity)
class SkillSimilarityAdmin(admin.ModelAdmin):
    list_display = ['skill1', 'skill2', 'similarity_score']
    list_filter = ['similarity_score']
    search_fields = ['skill1', 'skill2']
    ordering = ['-similarity_score']


@admin.register(IndustrySimilarity)
class IndustrySimilarityAdmin(admin.ModelAdmin):
    list_display = ['industry1', 'industry2', 'similarity_score']
    list_filter = ['similarity_score']
    search_fields = ['industry1', 'industry2']
    ordering = ['-similarity_score']


# Configuration de l'admin
admin.site.site_header = "Administration - Système de Matching"
admin.site.site_title = "Matching Admin"
admin.site.index_title = "Gestion du Système de Matching Intelligent"


