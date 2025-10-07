from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    Badge, Level, Achievement, Reward, UserReward, Leaderboard
)

class RewardClaimForm(forms.Form):
    """Formulaire pour réclamer une récompense"""
    confirm = forms.BooleanField(
        required=True,
        label="Je confirme que je veux réclamer cette récompense",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        self.reward = kwargs.pop('reward', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.reward and self.user:
            # Vérifier si l'utilisateur a déjà réclamé cette récompense
            if UserReward.objects.filter(user=self.user, reward=self.reward).exists():
                self.add_error('confirm', 'Vous avez déjà réclamé cette récompense.')
            
            # Vérifier si l'utilisateur a assez de points
            user_level = self.user.level
            if user_level and user_level.total_points < self.reward.cost:
                self.add_error('confirm', f'Vous n\'avez pas assez de points. Coût: {self.reward.cost}, Vos points: {user_level.total_points}')

class BadgeForm(forms.ModelForm):
    """Formulaire pour créer/modifier un badge"""
    class Meta:
        model = Badge
        fields = [
            'name', 'description', 'icon', 'color', 'badge_type',
            'points', 'rarity', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fas fa-star'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'badge_type': forms.Select(attrs={'class': 'form-select'}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'rarity': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_points(self):
        points = self.cleaned_data.get('points')
        if points < 0:
            raise ValidationError('Les points doivent être positifs.')
        return points

class LevelForm(forms.ModelForm):
    """Formulaire pour créer/modifier un niveau"""
    class Meta:
        model = Level
        fields = [
            'name', 'level_number', 'required_points', 'description',
            'icon', 'color', 'benefits', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'level_number': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'required_points': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fas fa-trophy'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '["profile_boost", "priority_support"]'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_level_number(self):
        level_number = self.cleaned_data.get('level_number')
        if level_number < 1:
            raise ValidationError('Le numéro de niveau doit être supérieur à 0.')
        
        # Vérifier l'unicité
        if self.instance.pk:
            if Level.objects.filter(level_number=level_number).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Ce numéro de niveau existe déjà.')
        else:
            if Level.objects.filter(level_number=level_number).exists():
                raise ValidationError('Ce numéro de niveau existe déjà.')
        
        return level_number
    
    def clean_required_points(self):
        required_points = self.cleaned_data.get('required_points')
        if required_points < 0:
            raise ValidationError('Les points requis doivent être positifs.')
        return required_points

class AchievementForm(forms.ModelForm):
    """Formulaire pour créer/modifier une réussite"""
    class Meta:
        model = Achievement
        fields = [
            'name', 'description', 'achievement_type', 'condition',
            'points', 'badge', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'achievement_type': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '{"type": "count", "value": 10, "target": "job_applications"}'}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'badge': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_points(self):
        points = self.cleaned_data.get('points')
        if points < 0:
            raise ValidationError('Les points doivent être positifs.')
        return points
    
    def clean_condition(self):
        condition = self.cleaned_data.get('condition')
        if condition:
            try:
                import json
                json.loads(condition)
            except json.JSONDecodeError:
                raise ValidationError('Le format de la condition n\'est pas valide JSON.')
        return condition

class RewardForm(forms.ModelForm):
    """Formulaire pour créer/modifier une récompense"""
    class Meta:
        model = Reward
        fields = [
            'name', 'description', 'reward_type', 'value',
            'cost', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reward_type': forms.Select(attrs={'class': 'form-select'}),
            'value': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '{"points": 100} ou {"discount_percent": 20}'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_cost(self):
        cost = self.cleaned_data.get('cost')
        if cost < 0:
            raise ValidationError('Le coût doit être positif.')
        return cost
    
    def clean_value(self):
        value = self.cleaned_data.get('value')
        if value:
            try:
                import json
                json.loads(value)
            except json.JSONDecodeError:
                raise ValidationError('Le format de la valeur n\'est pas valide JSON.')
        return value

class LeaderboardForm(forms.ModelForm):
    """Formulaire pour créer/modifier un classement"""
    class Meta:
        model = Leaderboard
        fields = [
            'name', 'leaderboard_type', 'period', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'leaderboard_type': forms.Select(attrs={'class': 'form-select'}),
            'period': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class GamificationSettingsForm(forms.Form):
    """Formulaire pour les paramètres de gamification"""
    show_notifications = forms.BooleanField(
        required=False,
        label="Afficher les notifications de gamification",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    show_leaderboards = forms.BooleanField(
        required=False,
        label="Afficher les classements",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    show_achievements = forms.BooleanField(
        required=False,
        label="Afficher les réussites",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    show_badges = forms.BooleanField(
        required=False,
        label="Afficher les badges",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    show_rewards = forms.BooleanField(
        required=False,
        label="Afficher les récompenses",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Charger les préférences existantes
            try:
                preferences = self.user.gamification_preferences
                self.fields['show_notifications'].initial = preferences.show_notifications
                self.fields['show_leaderboards'].initial = preferences.show_leaderboards
                self.fields['show_achievements'].initial = preferences.show_achievements
                self.fields['show_badges'].initial = preferences.show_badges
                self.fields['show_rewards'].initial = preferences.show_rewards
            except:
                pass

class BadgeSearchForm(forms.Form):
    """Formulaire de recherche de badges"""
    search_query = forms.CharField(
        max_length=255,
        required=False,
        label='Rechercher',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du badge...'})
    )
    
    badge_type = forms.ChoiceField(
        choices=[('', 'Tous les types')] + Badge.BADGE_TYPE_CHOICES,
        required=False,
        label='Type de badge',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    rarity = forms.ChoiceField(
        choices=[('', 'Toutes les raretés')] + Badge._meta.get_field('rarity').choices,
        required=False,
        label='Rareté',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    earned_only = forms.BooleanField(
        required=False,
        label='Badges obtenus uniquement',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class AchievementSearchForm(forms.Form):
    """Formulaire de recherche de réussites"""
    search_query = forms.CharField(
        max_length=255,
        required=False,
        label='Rechercher',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la réussite...'})
    )
    
    achievement_type = forms.ChoiceField(
        choices=[('', 'Tous les types')] + Achievement.ACHIEVEMENT_TYPE_CHOICES,
        required=False,
        label='Type de réussite',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    completed_only = forms.BooleanField(
        required=False,
        label='Réussites terminées uniquement',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    in_progress_only = forms.BooleanField(
        required=False,
        label='Réussites en cours uniquement',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class LeaderboardSearchForm(forms.Form):
    """Formulaire de recherche de classements"""
    leaderboard_type = forms.ChoiceField(
        choices=[('', 'Tous les types')] + Leaderboard.LEADERBOARD_TYPE_CHOICES,
        required=False,
        label='Type de classement',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    period = forms.ChoiceField(
        choices=[('', 'Toutes les périodes')] + Leaderboard.PERIOD_CHOICES,
        required=False,
        label='Période',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class RewardSearchForm(forms.Form):
    """Formulaire de recherche de récompenses"""
    search_query = forms.CharField(
        max_length=255,
        required=False,
        label='Rechercher',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la récompense...'})
    )
    
    reward_type = forms.ChoiceField(
        choices=[('', 'Tous les types')] + Reward.REWARD_TYPE_CHOICES,
        required=False,
        label='Type de récompense',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    max_cost = forms.IntegerField(
        required=False,
        label='Coût maximum',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    
    available_only = forms.BooleanField(
        required=False,
        label='Récompenses disponibles uniquement',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    claimed_only = forms.BooleanField(
        required=False,
        label='Récompenses réclamées uniquement',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
