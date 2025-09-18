from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User, CandidateProfile, Education, Experience, 
    Skill, Language, Certification, Reference
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('user_type', 'phone', 'is_email_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('email', 'first_name', 'last_name', 'user_type')
        }),
    )


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1


class LanguageInline(admin.TabularInline):
    model = Language
    extra = 1


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 1


class ReferenceInline(admin.TabularInline):
    model = Reference
    extra = 1


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'current_position', 'years_of_experience', 
        'profile_completion', 'is_active', 'updated_at'
    )
    list_filter = ('is_active', 'gender', 'marital_status', 'willing_to_relocate', 'preferred_work_type')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'current_position', 'current_company')
    readonly_fields = ('profile_completion', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Informations personnelles', {
            'fields': (
                'profile_picture', 'date_of_birth', 'gender', 'marital_status', 'nationality'
            )
        }),
        ('Adresse', {
            'fields': ('address', 'city', 'postal_code', 'country')
        }),
        ('Contact', {
            'fields': ('mobile_phone', 'linkedin_url', 'website_url')
        }),
        ('Informations professionnelles', {
            'fields': (
                'current_position', 'current_company', 'years_of_experience',
                'expected_salary', 'availability_date'
            )
        }),
        ('Documents', {
            'fields': ('cv_file', 'cover_letter')
        }),
        ('Préférences', {
            'fields': ('willing_to_relocate', 'preferred_work_type')
        }),
        ('Métadonnées', {
            'fields': ('profile_completion', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [EducationInline, ExperienceInline, SkillInline, LanguageInline, CertificationInline, ReferenceInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'degree', 'institution', 'degree_level', 'start_date', 'end_date', 'is_current')
    list_filter = ('degree_level', 'is_current', 'start_date')
    search_fields = ('candidate__user__first_name', 'candidate__user__last_name', 'institution', 'degree')
    date_hierarchy = 'start_date'


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'position', 'company', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current', 'start_date')
    search_fields = ('candidate__user__first_name', 'candidate__user__last_name', 'company', 'position')
    date_hierarchy = 'start_date'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'name', 'level', 'category', 'years_of_experience')
    list_filter = ('level', 'category')
    search_fields = ('candidate__user__first_name', 'candidate__user__last_name', 'name')


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'language', 'proficiency')
    list_filter = ('proficiency',)
    search_fields = ('candidate__user__first_name', 'candidate__user__last_name', 'language')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'name', 'issuing_organization', 'issue_date', 'expiration_date')
    list_filter = ('issue_date', 'expiration_date')
    search_fields = ('candidate__user__first_name', 'candidate__user__last_name', 'name', 'issuing_organization')
    date_hierarchy = 'issue_date'


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'name', 'position', 'company', 'email')
    search_fields = ('candidate__user__first_name', 'candidate__user__last_name', 'name', 'company')