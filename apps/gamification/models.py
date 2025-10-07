from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL

class Badge(models.Model):
    """Modèle pour les badges de gamification"""
    BADGE_TYPE_CHOICES = [
        ('profile_completion', 'Complétion de profil'),
        ('job_application', 'Candidature'),
        ('cv_creation', 'Création de CV'),
        ('skill_verification', 'Vérification de compétences'),
        ('referral', 'Parrainage'),
        ('achievement', 'Réussite'),
        ('streak', 'Série'),
        ('social', 'Social'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nom du badge')
    description = models.TextField(verbose_name='Description')
    icon = models.CharField(max_length=50, help_text='Icône FontAwesome', verbose_name='Icône')
    color = models.CharField(max_length=7, default='#007bff', help_text='Couleur hexadécimale', verbose_name='Couleur')
    badge_type = models.CharField(max_length=30, choices=BADGE_TYPE_CHOICES, verbose_name='Type de badge')
    points = models.PositiveIntegerField(default=10, verbose_name='Points attribués')
    rarity = models.CharField(max_length=20, choices=[
        ('common', 'Commun'),
        ('uncommon', 'Peu commun'),
        ('rare', 'Rare'),
        ('epic', 'Épique'),
        ('legendary', 'Légendaire'),
    ], default='common', verbose_name='Rareté')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Badge'
        verbose_name_plural = 'Badges'
        ordering = ['badge_type', 'points']

    def __str__(self):
        return self.name

class UserBadge(models.Model):
    """Association entre utilisateur et badge"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges', verbose_name='Utilisateur')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='users', verbose_name='Badge')
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name='Obtenu le')
    is_featured = models.BooleanField(default=False, verbose_name='Mis en avant')

    class Meta:
        verbose_name = 'Badge utilisateur'
        verbose_name_plural = 'Badges utilisateurs'
        unique_together = ('user', 'badge')
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"

class Level(models.Model):
    """Niveaux de gamification"""
    name = models.CharField(max_length=50, verbose_name='Nom du niveau')
    level_number = models.PositiveIntegerField(unique=True, verbose_name='Numéro de niveau')
    required_points = models.PositiveIntegerField(verbose_name='Points requis')
    description = models.TextField(blank=True, verbose_name='Description')
    icon = models.CharField(max_length=50, help_text='Icône FontAwesome', verbose_name='Icône')
    color = models.CharField(max_length=7, default='#28a745', verbose_name='Couleur')
    benefits = models.JSONField(default=list, blank=True, verbose_name='Avantages')  # ex: ['profile_boost', 'priority_support']
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')

    class Meta:
        verbose_name = 'Niveau'
        verbose_name_plural = 'Niveaux'
        ordering = ['level_number']

    def __str__(self):
        return f"Niveau {self.level_number}: {self.name}"

class UserLevel(models.Model):
    """Niveau actuel de l'utilisateur"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='level', verbose_name='Utilisateur')
    current_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='users', verbose_name='Niveau actuel')
    total_points = models.PositiveIntegerField(default=0, verbose_name='Points totaux')
    points_to_next_level = models.PositiveIntegerField(default=0, verbose_name='Points jusqu\'au niveau suivant')
    level_progress = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Progression (%)')
    last_level_up = models.DateTimeField(null=True, blank=True, verbose_name='Dernière montée de niveau')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Niveau utilisateur'
        verbose_name_plural = 'Niveaux utilisateurs'

    def __str__(self):
        return f"{self.user.username} - Niveau {self.current_level.level_number}"

    def calculate_progress(self):
        """Calcule la progression vers le niveau suivant"""
        next_level = Level.objects.filter(level_number__gt=self.current_level.level_number).order_by('level_number').first()
        if next_level:
            points_needed = next_level.required_points - self.current_level.required_points
            points_earned = self.total_points - self.current_level.required_points
            self.level_progress = min(100, (points_earned / points_needed) * 100) if points_needed > 0 else 100
            self.points_to_next_level = max(0, next_level.required_points - self.total_points)
        else:
            self.level_progress = 100
            self.points_to_next_level = 0

class Achievement(models.Model):
    """Réussites spécifiques"""
    ACHIEVEMENT_TYPE_CHOICES = [
        ('profile_completion', 'Complétion de profil'),
        ('job_application', 'Candidature'),
        ('cv_creation', 'Création de CV'),
        ('skill_verification', 'Vérification de compétences'),
        ('referral', 'Parrainage'),
        ('streak', 'Série'),
        ('social', 'Social'),
        ('custom', 'Personnalisé'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nom de la réussite')
    description = models.TextField(verbose_name='Description')
    achievement_type = models.CharField(max_length=30, choices=ACHIEVEMENT_TYPE_CHOICES, verbose_name='Type de réussite')
    condition = models.JSONField(verbose_name='Condition')  # ex: {'type': 'count', 'value': 10, 'target': 'job_applications'}
    points = models.PositiveIntegerField(default=50, verbose_name='Points attribués')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, null=True, blank=True, related_name='achievements', verbose_name='Badge associé')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Réussite'
        verbose_name_plural = 'Réussites'
        ordering = ['achievement_type', 'points']

    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    """Réussites de l'utilisateur"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements', verbose_name='Utilisateur')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='users', verbose_name='Réussite')
    progress = models.PositiveIntegerField(default=0, verbose_name='Progression')
    is_completed = models.BooleanField(default=False, verbose_name='Terminé')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Terminé le')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Réussite utilisateur'
        verbose_name_plural = 'Réussites utilisateurs'
        unique_together = ('user', 'achievement')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"

class Streak(models.Model):
    """Séries d'activité"""
    STREAK_TYPE_CHOICES = [
        ('daily_login', 'Connexion quotidienne'),
        ('job_application', 'Candidature quotidienne'),
        ('profile_update', 'Mise à jour de profil'),
        ('skill_learning', 'Apprentissage de compétences'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streaks', verbose_name='Utilisateur')
    streak_type = models.CharField(max_length=30, choices=STREAK_TYPE_CHOICES, verbose_name='Type de série')
    current_streak = models.PositiveIntegerField(default=0, verbose_name='Série actuelle')
    longest_streak = models.PositiveIntegerField(default=0, verbose_name='Plus longue série')
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name='Dernière activité')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Série'
        verbose_name_plural = 'Séries'
        unique_together = ('user', 'streak_type')
        ordering = ['-current_streak']

    def __str__(self):
        return f"{self.user.username} - {self.get_streak_type_display()} ({self.current_streak} jours)"

class Leaderboard(models.Model):
    """Classements"""
    LEADERBOARD_TYPE_CHOICES = [
        ('points', 'Points totaux'),
        ('badges', 'Nombre de badges'),
        ('applications', 'Candidatures'),
        ('profile_completion', 'Complétion de profil'),
        ('streak', 'Série'),
    ]
    
    PERIOD_CHOICES = [
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('all_time', 'Tout temps'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nom du classement')
    leaderboard_type = models.CharField(max_length=30, choices=LEADERBOARD_TYPE_CHOICES, verbose_name='Type de classement')
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, verbose_name='Période')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Classement'
        verbose_name_plural = 'Classements'
        unique_together = ('leaderboard_type', 'period')
        ordering = ['leaderboard_type', 'period']

    def __str__(self):
        return f"{self.name} ({self.get_period_display()})"

class LeaderboardEntry(models.Model):
    """Entrées du classement"""
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE, related_name='entries', verbose_name='Classement')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries', verbose_name='Utilisateur')
    rank = models.PositiveIntegerField(verbose_name='Rang')
    score = models.PositiveIntegerField(verbose_name='Score')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Entrée de classement'
        verbose_name_plural = 'Entrées de classement'
        unique_together = ('leaderboard', 'user')
        ordering = ['rank']

    def __str__(self):
        return f"#{self.rank} {self.user.username} - {self.score} points"

class Reward(models.Model):
    """Récompenses"""
    REWARD_TYPE_CHOICES = [
        ('points', 'Points'),
        ('badge', 'Badge'),
        ('discount', 'Remise'),
        ('premium_feature', 'Fonctionnalité premium'),
        ('custom', 'Personnalisé'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nom de la récompense')
    description = models.TextField(verbose_name='Description')
    reward_type = models.CharField(max_length=30, choices=REWARD_TYPE_CHOICES, verbose_name='Type de récompense')
    value = models.JSONField(verbose_name='Valeur')  # ex: {'points': 100} ou {'discount_percent': 20}
    cost = models.PositiveIntegerField(default=0, verbose_name='Coût en points')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Récompense'
        verbose_name_plural = 'Récompenses'
        ordering = ['cost']

    def __str__(self):
        return self.name

class UserReward(models.Model):
    """Récompenses de l'utilisateur"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards', verbose_name='Utilisateur')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, related_name='users', verbose_name='Récompense')
    claimed_at = models.DateTimeField(auto_now_add=True, verbose_name='Réclamé le')
    is_used = models.BooleanField(default=False, verbose_name='Utilisé')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='Utilisé le')

    class Meta:
        verbose_name = 'Récompense utilisateur'
        verbose_name_plural = 'Récompenses utilisateurs'
        ordering = ['-claimed_at']

    def __str__(self):
        return f"{self.user.username} - {self.reward.name}"

class GamificationEvent(models.Model):
    """Événements de gamification"""
    EVENT_TYPE_CHOICES = [
        ('badge_earned', 'Badge obtenu'),
        ('level_up', 'Montée de niveau'),
        ('achievement_completed', 'Réussite terminée'),
        ('streak_milestone', 'Étape de série'),
        ('leaderboard_rank', 'Rang dans le classement'),
        ('reward_claimed', 'Récompense réclamée'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gamification_events', verbose_name='Utilisateur')
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES, verbose_name='Type d\'événement')
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(verbose_name='Description')
    points_earned = models.PositiveIntegerField(default=0, verbose_name='Points gagnés')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Métadonnées')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')

    class Meta:
        verbose_name = 'Événement de gamification'
        verbose_name_plural = 'Événements de gamification'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"