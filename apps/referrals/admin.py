from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    ReferralProgram, ReferralCode, Referral, ReferralReward,
    ReferralInvitation, ReferralLeaderboard, ReferralAnalytics
)


@admin.register(ReferralProgram)
class ReferralProgramAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'is_active', 'start_date', 'end_date',
        'referral_count', 'total_rewards_given', 'created_at'
    ]
    list_filter = ['is_active', 'start_date', 'end_date', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'description')
        }),
        ('Configuration des récompenses', {
            'fields': ('referrer_reward', 'referee_reward', 'bonus_reward')
        }),
        ('Conditions', {
            'fields': ('min_referrals_for_bonus', 'max_referrals_per_user', 'max_rewards_per_user')
        }),
        ('Statut et dates', {
            'fields': ('is_active', 'start_date', 'end_date')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def referral_count(self, obj):
        return obj.referrals.count()
    referral_count.short_description = 'Recommandations'
    
    def total_rewards_given(self, obj):
        return ReferralReward.objects.filter(referral__program=obj).count()
    total_rewards_given.short_description = 'Récompenses données'


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'program', 'code', 'total_uses', 'successful_referrals',
        'total_rewards_earned', 'created_at', 'last_used_at'
    ]
    list_filter = ['program', 'created_at', 'last_used_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'code']
    readonly_fields = ['created_at', 'total_uses', 'successful_referrals', 'total_rewards_earned']
    raw_id_fields = ['user', 'program']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'program', 'code')
        }),
        ('Statistiques', {
            'fields': ('total_uses', 'successful_referrals', 'total_rewards_earned', 'last_used_at')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = [
        'referrer', 'referee', 'program', 'status', 'referrer_reward_given',
        'referee_reward_given', 'created_at', 'completed_at'
    ]
    list_filter = ['status', 'program', 'referrer_reward_given', 'referee_reward_given', 'created_at']
    search_fields = [
        'referrer__first_name', 'referrer__last_name', 'referrer__email',
        'referee__first_name', 'referee__last_name', 'referee__email'
    ]
    readonly_fields = ['created_at', 'completed_at']
    raw_id_fields = ['referrer', 'referee', 'program', 'referral_code']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('referrer', 'referee', 'program', 'referral_code')
        }),
        ('Statut', {
            'fields': ('status',)
        }),
        ('Récompenses', {
            'fields': ('referrer_reward_given', 'referee_reward_given', 
                      'referrer_reward_amount', 'referee_reward_amount')
        }),
        ('Dates', {
            'fields': ('created_at', 'completed_at', 'expires_at')
        }),
    )
    
    actions = ['mark_as_completed', 'give_rewards']
    
    def mark_as_completed(self, request, queryset):
        for referral in queryset:
            referral.complete()
        self.message_user(request, f"{queryset.count()} recommandations marquées comme complétées.")
    mark_as_completed.short_description = "Marquer comme complétées"
    
    def give_rewards(self, request, queryset):
        for referral in queryset:
            referral.give_rewards()
        self.message_user(request, f"Récompenses données pour {queryset.count()} recommandations.")
    give_rewards.short_description = "Donner les récompenses"


@admin.register(ReferralReward)
class ReferralRewardAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'referral', 'reward_type', 'amount', 'is_claimed',
        'claimed_at', 'created_at'
    ]
    list_filter = ['reward_type', 'is_claimed', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'referral']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'referral')
        }),
        ('Détails de la récompense', {
            'fields': ('reward_type', 'amount', 'description')
        }),
        ('Statut', {
            'fields': ('is_claimed', 'claimed_at')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_claimed']
    
    def mark_as_claimed(self, request, queryset):
        for reward in queryset:
            reward.claim()
        self.message_user(request, f"{queryset.count()} récompenses marquées comme réclamées.")
    mark_as_claimed.short_description = "Marquer comme réclamées"


@admin.register(ReferralInvitation)
class ReferralInvitationAdmin(admin.ModelAdmin):
    list_display = [
        'referrer', 'email', 'name', 'status', 'sent_at',
        'opened_at', 'clicked_at', 'registered_at', 'is_expired'
    ]
    list_filter = ['status', 'sent_at', 'opened_at', 'clicked_at', 'registered_at']
    search_fields = [
        'referrer__first_name', 'referrer__last_name', 'referrer__email',
        'email', 'name'
    ]
    readonly_fields = ['sent_at', 'opened_at', 'clicked_at', 'registered_at', 'is_expired']
    raw_id_fields = ['referrer', 'referral_code']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('referrer', 'referral_code', 'email', 'name')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Statut et suivi', {
            'fields': ('status', 'sent_at', 'opened_at', 'clicked_at', 'registered_at')
        }),
        ('Expiration', {
            'fields': ('expires_at', 'is_expired')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expirée'


@admin.register(ReferralLeaderboard)
class ReferralLeaderboardAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'program', 'rank', 'total_referrals', 'successful_referrals',
        'total_rewards', 'period_start', 'period_end'
    ]
    list_filter = ['program', 'rank', 'period_start', 'period_end']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'program']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'program')
        }),
        ('Statistiques', {
            'fields': ('total_referrals', 'successful_referrals', 'total_rewards')
        }),
        ('Position', {
            'fields': ('rank',)
        }),
        ('Période', {
            'fields': ('period_start', 'period_end')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReferralAnalytics)
class ReferralAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'program', 'date', 'total_invitations_sent', 'total_invitations_opened',
        'total_invitations_clicked', 'total_registrations', 'total_rewards_given'
    ]
    list_filter = ['program', 'date', 'created_at']
    search_fields = ['program__name']
    readonly_fields = ['created_at']
    raw_id_fields = ['program']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('program', 'date')
        }),
        ('Statistiques d\'invitations', {
            'fields': ('total_invitations_sent', 'total_invitations_opened', 
                      'total_invitations_clicked', 'total_registrations')
        }),
        ('Récompenses', {
            'fields': ('total_rewards_given',)
        }),
        ('Taux de conversion', {
            'fields': ('open_rate', 'click_rate', 'registration_rate')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )