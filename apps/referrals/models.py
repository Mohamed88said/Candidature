from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
import json

User = get_user_model()


class ReferralProgram(models.Model):
    """Modèle pour le programme de recommandation"""
    name = models.CharField(max_length=200, verbose_name='Nom du programme')
    description = models.TextField(verbose_name='Description')
    
    # Configuration des récompenses
    referrer_reward = models.JSONField(default=dict, verbose_name='Récompense du parrain')  # {'type': 'points', 'amount': 100}
    referee_reward = models.JSONField(default=dict, verbose_name='Récompense du filleul')  # {'type': 'points', 'amount': 50}
    
    # Conditions d'éligibilité
    min_referrals_for_bonus = models.PositiveIntegerField(default=5, verbose_name='Minimum de parrainages pour bonus')
    bonus_reward = models.JSONField(default=dict, verbose_name='Récompense bonus')  # {'type': 'points', 'amount': 500}
    
    # Limites
    max_referrals_per_user = models.PositiveIntegerField(default=10, verbose_name='Maximum de parrainages par utilisateur')
    max_rewards_per_user = models.PositiveIntegerField(default=1000, verbose_name='Maximum de récompenses par utilisateur')
    
    # Statut
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    start_date = models.DateTimeField(verbose_name='Date de début')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='Date de fin')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Programme de recommandation'
        verbose_name_plural = 'Programmes de recommandation'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def is_currently_active(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


class ReferralCode(models.Model):
    """Modèle pour les codes de recommandation"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_codes', verbose_name='Utilisateur')
    program = models.ForeignKey(ReferralProgram, on_delete=models.CASCADE, related_name='referral_codes', verbose_name='Programme')
    
    # Code de recommandation
    code = models.CharField(max_length=50, unique=True, verbose_name='Code de recommandation')
    
    # Statistiques
    total_uses = models.PositiveIntegerField(default=0, verbose_name='Nombre total d\'utilisations')
    successful_referrals = models.PositiveIntegerField(default=0, verbose_name='Parrainages réussis')
    total_rewards_earned = models.PositiveIntegerField(default=0, verbose_name='Total des récompenses gagnées')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name='Dernière utilisation')
    
    class Meta:
        verbose_name = 'Code de recommandation'
        verbose_name_plural = 'Codes de recommandation'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.code}"
    
    def generate_code(self):
        """Générer un code de recommandation unique"""
        if not self.code:
            # Utiliser les initiales de l'utilisateur + un UUID court
            initials = ''.join([name[0].upper() for name in self.user.full_name.split()[:2]])
            unique_id = str(uuid.uuid4())[:8].upper()
            self.code = f"{initials}{unique_id}"
        return self.code
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.generate_code()
        super().save(*args, **kwargs)


class Referral(models.Model):
    """Modèle pour les recommandations"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('cancelled', 'Annulé'),
        ('expired', 'Expiré'),
    ]
    
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made', verbose_name='Parrain')
    referee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_received', verbose_name='Filleul')
    program = models.ForeignKey(ReferralProgram, on_delete=models.CASCADE, related_name='referrals', verbose_name='Programme')
    referral_code = models.ForeignKey(ReferralCode, on_delete=models.CASCADE, related_name='referrals', verbose_name='Code de recommandation')
    
    # Statut et suivi
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Statut')
    
    # Récompenses
    referrer_reward_given = models.BooleanField(default=False, verbose_name='Récompense parrain donnée')
    referee_reward_given = models.BooleanField(default=False, verbose_name='Récompense filleul donnée')
    referrer_reward_amount = models.PositiveIntegerField(default=0, verbose_name='Montant récompense parrain')
    referee_reward_amount = models.PositiveIntegerField(default=0, verbose_name='Montant récompense filleul')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Complété le')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Expire le')
    
    class Meta:
        verbose_name = 'Recommandation'
        verbose_name_plural = 'Recommandations'
        ordering = ['-created_at']
        unique_together = ['referrer', 'referee', 'program']
    
    def __str__(self):
        return f"{self.referrer.full_name} → {self.referee.full_name}"
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def can_be_completed(self):
        return self.status == 'pending' and not self.is_expired()
    
    def complete(self):
        """Marquer la recommandation comme complétée"""
        if self.can_be_completed():
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()
            
            # Mettre à jour les statistiques du code
            self.referral_code.successful_referrals += 1
            self.referral_code.last_used_at = timezone.now()
            self.referral_code.save()
            
            # Donner les récompenses
            self.give_rewards()
    
    def give_rewards(self):
        """Donner les récompenses aux utilisateurs"""
        # Récompense du parrain
        if not self.referrer_reward_given:
            self.referrer_reward_amount = self.program.referrer_reward.get('amount', 0)
            self.referrer_reward_given = True
        
        # Récompense du filleul
        if not self.referee_reward_given:
            self.referee_reward_amount = self.program.referee_reward.get('amount', 0)
            self.referee_reward_given = True
        
        self.save()


class ReferralReward(models.Model):
    """Modèle pour les récompenses de recommandation"""
    REWARD_TYPE_CHOICES = [
        ('points', 'Points'),
        ('credits', 'Crédits'),
        ('discount', 'Remise'),
        ('premium_access', 'Accès premium'),
        ('badge', 'Badge'),
        ('cash', 'Argent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_rewards', verbose_name='Utilisateur')
    referral = models.ForeignKey(Referral, on_delete=models.CASCADE, related_name='rewards', verbose_name='Recommandation')
    
    # Détails de la récompense
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPE_CHOICES, verbose_name='Type de récompense')
    amount = models.PositiveIntegerField(verbose_name='Montant')
    description = models.TextField(verbose_name='Description')
    
    # Statut
    is_claimed = models.BooleanField(default=False, verbose_name='Réclamée')
    claimed_at = models.DateTimeField(null=True, blank=True, verbose_name='Réclamée le')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Récompense de recommandation'
        verbose_name_plural = 'Récompenses de recommandation'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.get_reward_type_display()} ({self.amount})"
    
    def claim(self):
        """Réclamer la récompense"""
        if not self.is_claimed:
            self.is_claimed = True
            self.claimed_at = timezone.now()
            self.save()


class ReferralInvitation(models.Model):
    """Modèle pour les invitations de recommandation"""
    STATUS_CHOICES = [
        ('sent', 'Envoyée'),
        ('opened', 'Ouverte'),
        ('clicked', 'Cliquée'),
        ('registered', 'Inscrite'),
        ('expired', 'Expirée'),
    ]
    
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_invitations', verbose_name='Parrain')
    referral_code = models.ForeignKey(ReferralCode, on_delete=models.CASCADE, related_name='invitations', verbose_name='Code de recommandation')
    
    # Détails de l'invitation
    email = models.EmailField(verbose_name='Email invité')
    name = models.CharField(max_length=200, blank=True, verbose_name='Nom de l\'invité')
    message = models.TextField(blank=True, verbose_name='Message personnalisé')
    
    # Suivi
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent', verbose_name='Statut')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='Envoyée le')
    opened_at = models.DateTimeField(null=True, blank=True, verbose_name='Ouverte le')
    clicked_at = models.DateTimeField(null=True, blank=True, verbose_name='Cliquée le')
    registered_at = models.DateTimeField(null=True, blank=True, verbose_name='Inscrite le')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Expire le')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Invitation de recommandation'
        verbose_name_plural = 'Invitations de recommandation'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invitation de {self.referrer.full_name} à {self.email}"
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def mark_as_opened(self):
        if self.status == 'sent':
            self.status = 'opened'
            self.opened_at = timezone.now()
            self.save()
    
    def mark_as_clicked(self):
        if self.status in ['sent', 'opened']:
            self.status = 'clicked'
            self.clicked_at = timezone.now()
            self.save()
    
    def mark_as_registered(self):
        if self.status in ['sent', 'opened', 'clicked']:
            self.status = 'registered'
            self.registered_at = timezone.now()
            self.save()


class ReferralLeaderboard(models.Model):
    """Modèle pour le classement des recommandations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_leaderboard', verbose_name='Utilisateur')
    program = models.ForeignKey(ReferralProgram, on_delete=models.CASCADE, related_name='leaderboard', verbose_name='Programme')
    
    # Statistiques
    total_referrals = models.PositiveIntegerField(default=0, verbose_name='Total des recommandations')
    successful_referrals = models.PositiveIntegerField(default=0, verbose_name='Recommandations réussies')
    total_rewards = models.PositiveIntegerField(default=0, verbose_name='Total des récompenses')
    
    # Position
    rank = models.PositiveIntegerField(default=0, verbose_name='Rang')
    
    # Période
    period_start = models.DateTimeField(verbose_name='Début de période')
    period_end = models.DateTimeField(verbose_name='Fin de période')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Classement de recommandation'
        verbose_name_plural = 'Classements de recommandation'
        ordering = ['rank', '-total_referrals']
        unique_together = ['user', 'program', 'period_start', 'period_end']
    
    def __str__(self):
        return f"{self.user.full_name} - Rang {self.rank}"


class ReferralAnalytics(models.Model):
    """Modèle pour les analytics des recommandations"""
    program = models.ForeignKey(ReferralProgram, on_delete=models.CASCADE, related_name='analytics', verbose_name='Programme')
    date = models.DateField(verbose_name='Date')
    
    # Statistiques
    total_invitations_sent = models.PositiveIntegerField(default=0, verbose_name='Total invitations envoyées')
    total_invitations_opened = models.PositiveIntegerField(default=0, verbose_name='Total invitations ouvertes')
    total_invitations_clicked = models.PositiveIntegerField(default=0, verbose_name='Total invitations cliquées')
    total_registrations = models.PositiveIntegerField(default=0, verbose_name='Total inscriptions')
    total_rewards_given = models.PositiveIntegerField(default=0, verbose_name='Total récompenses données')
    
    # Taux de conversion
    open_rate = models.FloatField(default=0, verbose_name='Taux d\'ouverture')
    click_rate = models.FloatField(default=0, verbose_name='Taux de clic')
    registration_rate = models.FloatField(default=0, verbose_name='Taux d\'inscription')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Analytics de recommandation'
        verbose_name_plural = 'Analytics de recommandation'
        unique_together = ['program', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics {self.program.name} - {self.date}"