from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from apps.accounts.models import CandidateProfile
from apps.jobs.models import Job
from cloudinary.models import CloudinaryField

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
    
    # Fichiers avec Cloudinary
    resume_file = CloudinaryField(
        'raw',
        folder='recruitment/applications/resumes/',
        null=True,
        blank=True,
        resource_type='raw'
    )
    
    additional_documents = CloudinaryField(
        'raw',
        folder='recruitment/applications/documents/',
        null=True,
        blank=True,
        resource_type='raw'
    )
    
    # Vidéo de présentation
    presentation_video = CloudinaryField(
        'video',
        folder='recruitment/applications/videos/',
        null=True,
        blank=True,
        resource_type='video',
        transformation=[
            {'width': 1280, 'height': 720, 'crop': 'fill'},
            {'quality': 'auto'},
            {'format': 'mp4'}
        ]
    )
    video_duration = models.PositiveIntegerField(blank=True, null=True, help_text='Durée en secondes')
    video_transcript = models.TextField(blank=True, help_text='Transcription automatique de la vidéo')
    video_questions = models.JSONField(default=list, blank=True, help_text='Questions posées dans la vidéo')
    
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
    
    # Fichier avec Cloudinary
    file = CloudinaryField(
        'raw',
        folder='recruitment/applications/additional_docs/',
        resource_type='raw'
    )
    
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


class VideoQuestion(models.Model):
    """Questions personnalisées pour les vidéos de candidature"""
    QUESTION_TYPES = (
        ('introduction', 'Présentation personnelle'),
        ('motivation', 'Motivation pour le poste'),
        ('experience', 'Expérience pertinente'),
        ('skills', 'Compétences techniques'),
        ('challenge', 'Défi professionnel'),
        ('goals', 'Objectifs de carrière'),
        ('custom', 'Question personnalisée'),
    )
    
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='video_questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    question_text = models.TextField()
    is_required = models.BooleanField(default=True)
    time_limit = models.PositiveIntegerField(default=120, help_text='Temps limite en secondes')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Question vidéo'
        verbose_name_plural = 'Questions vidéo'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.get_question_type_display()} - {self.job.title}"


class VideoApplication(models.Model):
    """Candidature vidéo spécialisée"""
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='video_application')
    
    # Vidéo principale
    main_video = CloudinaryField(
        'video',
        folder='recruitment/applications/main_videos/',
        resource_type='video',
        transformation=[
            {'width': 1280, 'height': 720, 'crop': 'fill'},
            {'quality': 'auto'},
            {'format': 'mp4'}
        ]
    )
    
    # Réponses aux questions
    question_responses = models.JSONField(default=list, help_text='Réponses aux questions vidéo')
    
    # Métadonnées vidéo
    total_duration = models.PositiveIntegerField(help_text='Durée totale en secondes')
    video_quality = models.CharField(max_length=20, choices=[
        ('low', 'Basse'),
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
        ('ultra', 'Ultra'),
    ], default='medium')
    
    # Transcription et analyse
    transcript = models.TextField(blank=True)
    keywords_extracted = models.JSONField(default=list, blank=True)
    sentiment_analysis = models.JSONField(default=dict, blank=True)
    
    # Statut de traitement
    is_processed = models.BooleanField(default=False)
    processing_status = models.CharField(max_length=20, choices=[
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échec'),
    ], default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Candidature vidéo'
        verbose_name_plural = 'Candidatures vidéo'
    
    def __str__(self):
        return f"Vidéo - {self.application.candidate.user.full_name} - {self.application.job.title}"
    
    @property
    def duration_formatted(self):
        """Durée formatée (mm:ss)"""
        minutes = self.total_duration // 60
        seconds = self.total_duration % 60
        return f"{minutes:02d}:{seconds:02d}"