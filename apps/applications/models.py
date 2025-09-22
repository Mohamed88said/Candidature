from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from apps.accounts.models import CandidateProfile
from apps.jobs.models import Job

User = get_user_model()


class Application(models.Model):
    """Candidature à une offre d'emploi"""
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('reviewing', 'En cours d\'examen'),
        ('shortlisted', 'Présélectionné'),
        ('interview_scheduled', 'Entretien programmé'),
        ('interview_completed', 'Entretien terminé'),
        ('offer_made', 'Offre faite'),
        ('accepted', 'Accepté'),
        ('rejected', 'Rejeté'),
        ('withdrawn', 'Retiré'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('urgent', 'Urgente'),
    )

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    
    # Statut et priorité
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Lettre de motivation et documents
    cover_letter = models.TextField()
    resume_file = models.FileField(upload_to='applications/resumes/', blank=True, null=True)
    additional_documents = models.FileField(upload_to='applications/documents/', blank=True, null=True)
    
    # Informations supplémentaires
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    availability_date = models.DateField(blank=True, null=True)
    willing_to_relocate = models.BooleanField(default=False)
    
    # Questions personnalisées (JSON field pour flexibilité)
    custom_answers = models.JSONField(default=dict, blank=True)
    
    # Métadonnées
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Suivi RH
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Candidature'
        verbose_name_plural = 'Candidatures'
        unique_together = ['candidate', 'job']
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.candidate.user.full_name} - {self.job.title}"

    def get_absolute_url(self):
        return reverse('applications:application_detail', kwargs={'pk': self.pk})

    @property
    def days_since_applied(self):
        """Nombre de jours depuis la candidature"""
        return (timezone.now().date() - self.applied_at.date()).days

    def mark_as_reviewed(self, reviewer):
        """Marquer comme examiné"""
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save(update_fields=['reviewed_by', 'reviewed_at'])


class ApplicationRating(models.Model):
    """Évaluation d'une candidature"""
    RATING_CRITERIA = (
        ('experience', 'Expérience'),
        ('skills', 'Compétences'),
        ('education', 'Formation'),
        ('motivation', 'Motivation'),
        ('cultural_fit', 'Adéquation culturelle'),
        ('communication', 'Communication'),
        ('overall', 'Évaluation globale'),
    )

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='ratings')
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    criteria = models.CharField(max_length=20, choices=RATING_CRITERIA)
    score = models.PositiveIntegerField()  # Sur 5 ou 10
    max_score = models.PositiveIntegerField(default=5)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Évaluation'
        verbose_name_plural = 'Évaluations'
        unique_together = ['application', 'evaluator', 'criteria']

    def __str__(self):
        return f"{self.application} - {self.get_criteria_display()}: {self.score}/{self.max_score}"

    @property
    def score_percentage(self):
        """Score en pourcentage"""
        return (self.score / self.max_score) * 100


class ApplicationComment(models.Model):
    """Commentaires sur une candidature"""
    COMMENT_TYPES = (
        ('general', 'Général'),
        ('screening', 'Présélection'),
        ('interview', 'Entretien'),
        ('reference', 'Référence'),
        ('decision', 'Décision'),
    )

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='application_comments')
    comment_type = models.CharField(max_length=20, choices=COMMENT_TYPES, default='general')
    content = models.TextField()
    is_internal = models.BooleanField(default=True)  # Visible seulement par l'équipe RH
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'
        ordering = ['-created_at']

    def __str__(self):
        return f"Commentaire de {self.author.full_name} sur {self.application}"


class Interview(models.Model):
    """Entretien d'embauche"""
    INTERVIEW_TYPES = (
        ('phone', 'Téléphonique'),
        ('video', 'Visioconférence'),
        ('in_person', 'En personne'),
        ('technical', 'Technique'),
        ('panel', 'Panel'),
    )
    
    STATUS_CHOICES = (
        ('scheduled', 'Programmé'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
        ('rescheduled', 'Reprogrammé'),
    )

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Planification
    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    location = models.CharField(max_length=200, blank=True)  # Adresse ou lien de visio
    
    # Participants
    interviewers = models.ManyToManyField(User, related_name='conducted_interviews')
    
    # Notes et évaluation
    notes = models.TextField(blank=True)
    overall_rating = models.PositiveIntegerField(null=True, blank=True)  # Sur 5
    recommendation = models.CharField(max_length=20, choices=[
        ('hire', 'Recommande l\'embauche'),
        ('maybe', 'Mitigé'),
        ('no_hire', 'Ne recommande pas'),
    ], blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_interviews')

    class Meta:
        verbose_name = 'Entretien'
        verbose_name_plural = 'Entretiens'
        ordering = ['scheduled_date']

    def __str__(self):
        return f"Entretien {self.get_interview_type_display()} - {self.application}"

    @property
    def is_upcoming(self):
        """Vérifie si l'entretien est à venir"""
        return self.scheduled_date > timezone.now() and self.status == 'scheduled'

    @property
    def is_overdue(self):
        """Vérifie si l'entretien est en retard"""
        return self.scheduled_date < timezone.now() and self.status == 'scheduled'


class ApplicationStatusHistory(models.Model):
    """Historique des changements de statut d'une candidature"""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_history')
    previous_status = models.CharField(max_length=30, choices=Application.STATUS_CHOICES)
    new_status = models.CharField(max_length=30, choices=Application.STATUS_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status_changes')
    reason = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Historique de statut'
        verbose_name_plural = 'Historiques de statut'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.application} - {self.previous_status} → {self.new_status}"


class ApplicationDocument(models.Model):
    """Documents supplémentaires liés à une candidature"""
    DOCUMENT_TYPES = (
        ('resume', 'CV'),
        ('cover_letter', 'Lettre de motivation'),
        ('portfolio', 'Portfolio'),
        ('certificate', 'Certificat'),
        ('reference', 'Lettre de recommandation'),
        ('other', 'Autre'),
    )

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='applications/documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Document de candidature'
        verbose_name_plural = 'Documents de candidature'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} - {self.application}"

    @property
    def file_size_mb(self):
        """Taille du fichier en MB"""
        if self.file:
            return round(self.file.size / (1024 * 1024), 2)
        return 0
