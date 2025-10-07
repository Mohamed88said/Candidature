from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.accounts.models import CandidateProfile
from apps.jobs.models import Job
from apps.applications.models import Application
import json

User = get_user_model()


class MatchingAlgorithm(models.Model):
    """Configuration de l'algorithme de matching"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Poids des critères (0-100)
    experience_weight = models.PositiveIntegerField(default=25)
    skills_weight = models.PositiveIntegerField(default=30)
    location_weight = models.PositiveIntegerField(default=15)
    salary_weight = models.PositiveIntegerField(default=10)
    education_weight = models.PositiveIntegerField(default=10)
    company_culture_weight = models.PositiveIntegerField(default=10)
    
    # Seuils de matching
    minimum_match_score = models.PositiveIntegerField(default=60)
    high_match_threshold = models.PositiveIntegerField(default=80)
    
    # Configuration avancée
    use_ai_analysis = models.BooleanField(default=True)
    consider_soft_skills = models.BooleanField(default=True)
    location_radius_km = models.PositiveIntegerField(default=50)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Algorithme de Matching'
        verbose_name_plural = 'Algorithmes de Matching'
    
    def __str__(self):
        return self.name


class JobMatch(models.Model):
    """Résultat de matching entre un candidat et une offre"""
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='job_matches')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='candidate_matches')
    algorithm = models.ForeignKey(MatchingAlgorithm, on_delete=models.CASCADE)
    
    # Score de matching (0-100)
    overall_score = models.PositiveIntegerField()
    
    # Scores détaillés
    experience_score = models.PositiveIntegerField()
    skills_score = models.PositiveIntegerField()
    location_score = models.PositiveIntegerField()
    salary_score = models.PositiveIntegerField()
    education_score = models.PositiveIntegerField()
    culture_score = models.PositiveIntegerField()
    
    # Analyse détaillée
    matching_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    strengths = models.JSONField(default=list)
    concerns = models.JSONField(default=list)
    recommendations = models.TextField(blank=True)
    
    # Statut
    is_viewed_by_candidate = models.BooleanField(default=False)
    is_viewed_by_recruiter = models.BooleanField(default=False)
    candidate_interest = models.CharField(max_length=20, choices=[
        ('not_interested', 'Pas intéressé'),
        ('interested', 'Intéressé'),
        ('very_interested', 'Très intéressé'),
        ('applied', 'A postulé'),
    ], blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Match Emploi'
        verbose_name_plural = 'Matches Emploi'
        unique_together = ['candidate', 'job', 'algorithm']
        ordering = ['-overall_score', '-created_at']
    
    def __str__(self):
        return f"{self.candidate.user.full_name} ↔ {self.job.title} ({self.overall_score}%)"
    
    @property
    def match_level(self):
        """Niveau de matching basé sur le score"""
        if self.overall_score >= 90:
            return 'excellent'
        elif self.overall_score >= 80:
            return 'très_bon'
        elif self.overall_score >= 70:
            return 'bon'
        elif self.overall_score >= 60:
            return 'correct'
        else:
            return 'faible'
    
    @property
    def match_level_display(self):
        """Affichage du niveau de matching"""
        levels = {
            'excellent': 'Excellent Match',
            'très_bon': 'Très Bon Match',
            'bon': 'Bon Match',
            'correct': 'Match Correct',
            'faible': 'Match Faible'
        }
        return levels.get(self.match_level, 'Inconnu')


class CandidatePreference(models.Model):
    """Préférences du candidat pour le matching"""
    candidate = models.OneToOneField(CandidateProfile, on_delete=models.CASCADE, related_name='matching_preferences')
    
    # Préférences de localisation
    preferred_locations = models.JSONField(default=list, help_text="Liste des villes/régions préférées")
    max_commute_time = models.PositiveIntegerField(default=60, help_text="Temps de trajet max en minutes")
    willing_to_relocate = models.BooleanField(default=False)
    remote_work_preference = models.CharField(max_length=20, choices=[
        ('office_only', 'Bureau uniquement'),
        ('remote_only', 'Télétravail uniquement'),
        ('hybrid', 'Hybride'),
        ('flexible', 'Flexible'),
    ], default='flexible')
    
    # Préférences salariales
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_negotiable = models.BooleanField(default=True)
    
    # Préférences d'entreprise
    preferred_company_sizes = models.JSONField(default=list)
    preferred_industries = models.JSONField(default=list)
    preferred_company_cultures = models.JSONField(default=list)
    
    # Préférences de poste
    preferred_job_types = models.JSONField(default=list)
    preferred_experience_levels = models.JSONField(default=list)
    career_goals = models.TextField(blank=True)
    
    # Critères d'exclusion
    excluded_companies = models.JSONField(default=list)
    excluded_locations = models.JSONField(default=list)
    excluded_industries = models.JSONField(default=list)
    
    # Fréquence des alertes
    alert_frequency = models.CharField(max_length=20, choices=[
        ('immediate', 'Immédiat'),
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
    ], default='daily')
    
    # Seuils de matching
    min_match_score = models.PositiveIntegerField(default=70)
    only_high_matches = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Préférence de Matching'
        verbose_name_plural = 'Préférences de Matching'
    
    def __str__(self):
        return f"Préférences de {self.candidate.user.full_name}"


class MatchingHistory(models.Model):
    """Historique des matchings pour analytics"""
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='matching_history')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='matching_history')
    algorithm_version = models.CharField(max_length=50)
    
    # Scores
    overall_score = models.PositiveIntegerField()
    experience_score = models.PositiveIntegerField()
    skills_score = models.PositiveIntegerField()
    location_score = models.PositiveIntegerField()
    salary_score = models.PositiveIntegerField()
    education_score = models.PositiveIntegerField()
    culture_score = models.PositiveIntegerField()
    
    # Actions
    candidate_action = models.CharField(max_length=20, choices=[
        ('viewed', 'Vu'),
        ('interested', 'Intéressé'),
        ('applied', 'A postulé'),
        ('ignored', 'Ignoré'),
        ('saved', 'Sauvegardé'),
    ], blank=True)
    
    recruiter_action = models.CharField(max_length=20, choices=[
        ('viewed', 'Vu'),
        ('contacted', 'Contacté'),
        ('interviewed', 'Entretien'),
        ('hired', 'Embauché'),
        ('rejected', 'Rejeté'),
    ], blank=True)
    
    # Résultat final
    final_outcome = models.CharField(max_length=20, choices=[
        ('hired', 'Embauché'),
        ('rejected', 'Rejeté'),
        ('withdrawn', 'Retiré'),
        ('pending', 'En cours'),
    ], blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Historique de Matching'
        verbose_name_plural = 'Historiques de Matching'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.candidate.user.full_name} - {self.job.title} ({self.overall_score}%)"


class SkillSimilarity(models.Model):
    """Matrice de similarité entre compétences"""
    skill1 = models.CharField(max_length=100)
    skill2 = models.CharField(max_length=100)
    similarity_score = models.FloatField(help_text="Score de similarité entre 0 et 1")
    
    class Meta:
        verbose_name = 'Similarité de Compétence'
        verbose_name_plural = 'Similarités de Compétences'
        unique_together = ['skill1', 'skill2']
    
    def __str__(self):
        return f"{self.skill1} ↔ {self.skill2} ({self.similarity_score:.2f})"


class IndustrySimilarity(models.Model):
    """Matrice de similarité entre industries"""
    industry1 = models.CharField(max_length=100)
    industry2 = models.CharField(max_length=100)
    similarity_score = models.FloatField(help_text="Score de similarité entre 0 et 1")
    
    class Meta:
        verbose_name = 'Similarité d\'Industrie'
        verbose_name_plural = 'Similarités d\'Industries'
        unique_together = ['industry1', 'industry2']
    
    def __str__(self):
        return f"{self.industry1} ↔ {self.industry2} ({self.similarity_score:.2f})"

