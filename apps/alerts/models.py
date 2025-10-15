from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import json

User = get_user_model()


class AlertType(models.Model):
    """Type d'alerte (Nouvelle offre, Offre mise à jour, etc.)"""
    name = models.CharField(max_length=100, verbose_name='Nom')
    description = models.TextField(blank=True, verbose_name='Description')
    icon = models.CharField(max_length=50, default='fas fa-bell', verbose_name='Icône')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Couleur')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Type d\'alerte'
        verbose_name_plural = 'Types d\'alerte'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class AlertPreference(models.Model):
    """Préférences d'alertes d'un utilisateur"""
    FREQUENCY_CHOICES = [
        ('immediate', 'Immédiat'),
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('never', 'Jamais'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alert_preferences', verbose_name='Utilisateur')
    
    # Préférences générales
    email_alerts = models.BooleanField(default=True, verbose_name='Alertes par email')
    push_notifications = models.BooleanField(default=True, verbose_name='Notifications push')
    sms_alerts = models.BooleanField(default=False, verbose_name='Alertes SMS')
    
    # Fréquence des alertes
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='daily', verbose_name='Fréquence')
    max_alerts_per_day = models.PositiveIntegerField(default=5, verbose_name='Maximum d\'alertes par jour')
    
    # Préférences de contenu
    include_salary = models.BooleanField(default=True, verbose_name='Inclure les salaires')
    include_remote_jobs = models.BooleanField(default=True, verbose_name='Inclure les emplois à distance')
    include_part_time = models.BooleanField(default=False, verbose_name='Inclure les emplois à temps partiel')
    include_internships = models.BooleanField(default=False, verbose_name='Inclure les stages')
    
    # Filtres géographiques
    max_distance = models.PositiveIntegerField(default=50, help_text='Distance maximale en km', verbose_name='Distance maximale')
    preferred_locations = models.JSONField(default=list, verbose_name='Localisations préférées')
    
    # Filtres de salaire
    min_salary = models.PositiveIntegerField(null=True, blank=True, verbose_name='Salaire minimum')
    max_salary = models.PositiveIntegerField(null=True, blank=True, verbose_name='Salaire maximum')
    
    # Filtres d'expérience
    min_experience = models.PositiveIntegerField(default=0, verbose_name='Expérience minimum (années)')
    max_experience = models.PositiveIntegerField(null=True, blank=True, verbose_name='Expérience maximum (années)')
    
    # Types d'emploi préférés
    preferred_job_types = models.JSONField(default=list, verbose_name='Types d\'emploi préférés')
    preferred_industries = models.JSONField(default=list, verbose_name='Secteurs préférés')
    preferred_skills = models.JSONField(default=list, verbose_name='Compétences préférées')
    
    # Types d'alertes activés
    enabled_alert_types = models.ManyToManyField(AlertType, blank=True, verbose_name='Types d\'alertes activés')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Préférence d\'alerte'
        verbose_name_plural = 'Préférences d\'alertes'
    
    def __str__(self):
        return f"Préférences d'alertes - {self.user.full_name}"
    
    def clean(self):
        if self.min_salary and self.max_salary and self.min_salary > self.max_salary:
            raise ValidationError('Le salaire minimum ne peut pas être supérieur au salaire maximum.')
        
        if self.min_experience and self.max_experience and self.min_experience > self.max_experience:
            raise ValidationError('L\'expérience minimum ne peut pas être supérieure à l\'expérience maximum.')


class AlertNotification(models.Model):
    """Alerte pour une offre d'emploi spécifique"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('sent', 'Envoyée'),
        ('delivered', 'Livrée'),
        ('opened', 'Ouverte'),
        ('clicked', 'Cliquée'),
        ('failed', 'Échouée'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alert_notifications', verbose_name='Utilisateur')
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='alerts', verbose_name='Offre d\'emploi')
    alert_type = models.ForeignKey(AlertType, on_delete=models.CASCADE, related_name='alert_notifications', verbose_name='Type d\'alerte')
    
    # Contenu de l'alerte
    title = models.CharField(max_length=200, verbose_name='Titre')
    message = models.TextField(verbose_name='Message')
    match_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Score de correspondance')
    match_reasons = models.JSONField(default=list, verbose_name='Raisons de correspondance')
    
    # Statut et livraison
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Statut')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Envoyée le')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='Livrée le')
    opened_at = models.DateTimeField(null=True, blank=True, verbose_name='Ouverte le')
    clicked_at = models.DateTimeField(null=True, blank=True, verbose_name='Cliquée le')
    
    # Canaux de livraison
    email_sent = models.BooleanField(default=False, verbose_name='Email envoyé')
    push_sent = models.BooleanField(default=False, verbose_name='Push envoyé')
    sms_sent = models.BooleanField(default=False, verbose_name='SMS envoyé')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Notification d\'alerte'
        verbose_name_plural = 'Notifications d\'alertes'
        ordering = ['-created_at']
        unique_together = ['user', 'job', 'alert_type']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.job.title}"
    
    def mark_as_sent(self):
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_delivered(self):
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save()
    
    def mark_as_opened(self):
        self.status = 'opened'
        self.opened_at = timezone.now()
        self.save()
    
    def mark_as_clicked(self):
        self.status = 'clicked'
        self.clicked_at = timezone.now()
        self.save()


class AlertTemplate(models.Model):
    """Modèle d'alerte personnalisable"""
    name = models.CharField(max_length=100, verbose_name='Nom')
    alert_type = models.ForeignKey(AlertType, on_delete=models.CASCADE, related_name='templates', verbose_name='Type d\'alerte')
    
    # Contenu du template
    subject_template = models.CharField(max_length=200, verbose_name='Modèle de sujet')
    message_template = models.TextField(verbose_name='Modèle de message')
    html_template = models.TextField(blank=True, verbose_name='Modèle HTML')
    
    # Variables disponibles
    available_variables = models.JSONField(default=list, verbose_name='Variables disponibles')
    
    # Configuration
    is_active = models.BooleanField(default=True, verbose_name='Active')
    is_default = models.BooleanField(default=False, verbose_name='Par défaut')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Modèle d\'alerte'
        verbose_name_plural = 'Modèles d\'alerte'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class AlertCampaign(models.Model):
    """Campagne d'alertes groupées"""
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('scheduled', 'Programmée'),
        ('running', 'En cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Nom')
    description = models.TextField(blank=True, verbose_name='Description')
    alert_type = models.ForeignKey(AlertType, on_delete=models.CASCADE, related_name='campaigns', verbose_name='Type d\'alerte')
    
    # Ciblage
    target_users = models.ManyToManyField(User, blank=True, related_name='alert_campaigns', verbose_name='Utilisateurs ciblés')
    target_criteria = models.JSONField(default=dict, verbose_name='Critères de ciblage')
    
    # Contenu
    subject = models.CharField(max_length=200, verbose_name='Sujet')
    message = models.TextField(verbose_name='Message')
    html_content = models.TextField(blank=True, verbose_name='Contenu HTML')
    
    # Planification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Statut')
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name='Programmée pour')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Démarrée le')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Terminée le')
    
    # Statistiques
    total_recipients = models.PositiveIntegerField(default=0, verbose_name='Destinataires totaux')
    emails_sent = models.PositiveIntegerField(default=0, verbose_name='Emails envoyés')
    emails_delivered = models.PositiveIntegerField(default=0, verbose_name='Emails livrés')
    emails_opened = models.PositiveIntegerField(default=0, verbose_name='Emails ouverts')
    emails_clicked = models.PositiveIntegerField(default=0, verbose_name='Emails cliqués')
    
    # Métadonnées
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_campaigns', verbose_name='Créée par')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créée le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifiée le')
    
    class Meta:
        verbose_name = 'Campagne d\'alertes'
        verbose_name_plural = 'Campagnes d\'alertes'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class AlertAnalytics(models.Model):
    """Analytics des alertes"""
    date = models.DateField(verbose_name='Date')
    
    # Statistiques générales
    total_alerts_sent = models.PositiveIntegerField(default=0, verbose_name='Alertes envoyées totales')
    total_alerts_delivered = models.PositiveIntegerField(default=0, verbose_name='Alertes livrées totales')
    total_alerts_opened = models.PositiveIntegerField(default=0, verbose_name='Alertes ouvertes totales')
    total_alerts_clicked = models.PositiveIntegerField(default=0, verbose_name='Alertes cliquées totales')
    
    # Statistiques par type
    alerts_by_type = models.JSONField(default=dict, verbose_name='Alertes par type')
    
    # Statistiques par canal
    email_alerts_sent = models.PositiveIntegerField(default=0, verbose_name='Alertes email envoyées')
    push_alerts_sent = models.PositiveIntegerField(default=0, verbose_name='Alertes push envoyées')
    sms_alerts_sent = models.PositiveIntegerField(default=0, verbose_name='Alertes SMS envoyées')
    
    # Taux de conversion
    delivery_rate = models.FloatField(default=0, verbose_name='Taux de livraison (%)')
    open_rate = models.FloatField(default=0, verbose_name='Taux d\'ouverture (%)')
    click_rate = models.FloatField(default=0, verbose_name='Taux de clic (%)')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Analytics d\'alerte'
        verbose_name_plural = 'Analytics d\'alertes'
        unique_together = ['date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics - {self.date}"


class AlertSubscription(models.Model):
    """Abonnement à des alertes spécifiques"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alert_subscriptions', verbose_name='Utilisateur')
    alert_type = models.ForeignKey(AlertType, on_delete=models.CASCADE, related_name='subscriptions', verbose_name='Type d\'alerte')
    
    # Critères d'abonnement
    keywords = models.JSONField(default=list, verbose_name='Mots-clés')
    locations = models.JSONField(default=list, verbose_name='Localisations')
    job_types = models.JSONField(default=list, verbose_name='Types d\'emploi')
    industries = models.JSONField(default=list, verbose_name='Secteurs')
    salary_range = models.JSONField(default=dict, verbose_name='Fourchette de salaire')
    
    # Configuration
    is_active = models.BooleanField(default=True, verbose_name='Active')
    frequency = models.CharField(max_length=20, choices=AlertPreference.FREQUENCY_CHOICES, default='daily', verbose_name='Fréquence')
    
    # Statistiques
    total_alerts_received = models.PositiveIntegerField(default=0, verbose_name='Alertes reçues totales')
    last_alert_sent = models.DateTimeField(null=True, blank=True, verbose_name='Dernière alerte envoyée')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créée le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifiée le')
    
    class Meta:
        verbose_name = 'Abonnement d\'alerte'
        verbose_name_plural = 'Abonnements d\'alertes'
        unique_together = ['user', 'alert_type']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.alert_type.name}"