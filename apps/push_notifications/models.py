from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL

class Device(models.Model):
    """Appareils enregistrés pour les notifications push"""
    DEVICE_TYPE_CHOICES = [
        ('web', 'Web'),
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('desktop', 'Desktop'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices', verbose_name='Utilisateur')
    device_id = models.CharField(max_length=255, verbose_name='ID de l\'appareil')
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES, verbose_name='Type d\'appareil')
    device_name = models.CharField(max_length=100, blank=True, verbose_name='Nom de l\'appareil')
    push_token = models.TextField(verbose_name='Token de notification push')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    last_seen = models.DateTimeField(auto_now=True, verbose_name='Dernière vue')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Appareil'
        verbose_name_plural = 'Appareils'
        unique_together = ('user', 'device_id')
        ordering = ['-last_seen']

    def __str__(self):
        return f"{self.user.username} - {self.device_name or self.device_id}"

class NotificationTemplate(models.Model):
    """Modèles de notifications"""
    NOTIFICATION_TYPE_CHOICES = [
        ('job_alert', 'Alerte d\'emploi'),
        ('application_update', 'Mise à jour de candidature'),
        ('message_received', 'Message reçu'),
        ('profile_reminder', 'Rappel de profil'),
        ('achievement', 'Réussite'),
        ('badge_earned', 'Badge obtenu'),
        ('level_up', 'Montée de niveau'),
        ('referral', 'Parrainage'),
        ('system', 'Système'),
        ('marketing', 'Marketing'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nom du modèle')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES, verbose_name='Type de notification')
    title = models.CharField(max_length=200, verbose_name='Titre')
    body = models.TextField(verbose_name='Corps du message')
    icon = models.CharField(max_length=100, blank=True, verbose_name='Icône')
    image_url = models.URLField(blank=True, verbose_name='URL de l\'image')
    action_url = models.URLField(blank=True, verbose_name='URL d\'action')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Modèle de notification'
        verbose_name_plural = 'Modèles de notifications'
        ordering = ['notification_type', 'name']

    def __str__(self):
        return self.name

class PushNotification(models.Model):
    """Notifications push envoyées"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('sent', 'Envoyée'),
        ('delivered', 'Livrée'),
        ('opened', 'Ouverte'),
        ('failed', 'Échouée'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_notifications', verbose_name='Utilisateur')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications', verbose_name='Appareil')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications', verbose_name='Modèle')
    
    # Contenu de la notification
    title = models.CharField(max_length=200, verbose_name='Titre')
    body = models.TextField(verbose_name='Corps du message')
    icon = models.CharField(max_length=100, blank=True, verbose_name='Icône')
    image_url = models.URLField(blank=True, verbose_name='URL de l\'image')
    action_url = models.URLField(blank=True, verbose_name='URL d\'action')
    
    # Statut et suivi
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Statut')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Envoyé le')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='Livré le')
    opened_at = models.DateTimeField(null=True, blank=True, verbose_name='Ouvert le')
    
    # Métadonnées
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Métadonnées')
    error_message = models.TextField(blank=True, verbose_name='Message d\'erreur')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Notification push'
        verbose_name_plural = 'Notifications push'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

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

    def mark_as_failed(self, error_message=''):
        self.status = 'failed'
        self.error_message = error_message
        self.save()

class NotificationPreference(models.Model):
    """Préférences de notifications de l'utilisateur"""
    FREQUENCY_CHOICES = [
        ('instant', 'Instantané'),
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('never', 'Jamais'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences', verbose_name='Utilisateur')
    
    # Préférences générales
    push_enabled = models.BooleanField(default=True, verbose_name='Notifications push activées')
    email_enabled = models.BooleanField(default=True, verbose_name='Notifications email activées')
    sms_enabled = models.BooleanField(default=False, verbose_name='Notifications SMS activées')
    
    # Préférences par type
    job_alerts = models.BooleanField(default=True, verbose_name='Alertes d\'emploi')
    application_updates = models.BooleanField(default=True, verbose_name='Mises à jour de candidature')
    messages = models.BooleanField(default=True, verbose_name='Messages')
    profile_reminders = models.BooleanField(default=True, verbose_name='Rappels de profil')
    achievements = models.BooleanField(default=True, verbose_name='Réussites')
    badges = models.BooleanField(default=True, verbose_name='Badges')
    level_ups = models.BooleanField(default=True, verbose_name='Montées de niveau')
    referrals = models.BooleanField(default=True, verbose_name='Parrainages')
    system_notifications = models.BooleanField(default=True, verbose_name='Notifications système')
    marketing = models.BooleanField(default=False, verbose_name='Marketing')
    
    # Fréquence
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='instant', verbose_name='Fréquence')
    quiet_hours_start = models.TimeField(null=True, blank=True, verbose_name='Début des heures silencieuses')
    quiet_hours_end = models.TimeField(null=True, blank=True, verbose_name='Fin des heures silencieuses')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Préférence de notification'
        verbose_name_plural = 'Préférences de notifications'

    def __str__(self):
        return f"Préférences de {self.user.username}"

class NotificationCampaign(models.Model):
    """Campagnes de notifications"""
    CAMPAIGN_TYPE_CHOICES = [
        ('broadcast', 'Diffusion générale'),
        ('targeted', 'Ciblée'),
        ('scheduled', 'Planifiée'),
        ('triggered', 'Déclenchée'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Nom de la campagne')
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPE_CHOICES, verbose_name='Type de campagne')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, related_name='campaigns', verbose_name='Modèle')
    
    # Ciblage
    target_users = models.ManyToManyField(User, blank=True, related_name='notification_campaigns', verbose_name='Utilisateurs ciblés')
    target_filters = models.JSONField(default=dict, blank=True, verbose_name='Filtres de ciblage')
    
    # Planification
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name='Planifié le')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Envoyé le')
    
    # Statut
    is_active = models.BooleanField(default=True, verbose_name='Active')
    is_sent = models.BooleanField(default=False, verbose_name='Envoyée')
    
    # Statistiques
    total_sent = models.PositiveIntegerField(default=0, verbose_name='Total envoyé')
    total_delivered = models.PositiveIntegerField(default=0, verbose_name='Total livré')
    total_opened = models.PositiveIntegerField(default=0, verbose_name='Total ouvert')
    total_failed = models.PositiveIntegerField(default=0, verbose_name='Total échoué')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Campagne de notification'
        verbose_name_plural = 'Campagnes de notifications'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class NotificationAnalytics(models.Model):
    """Analyses des notifications"""
    date = models.DateField(verbose_name='Date')
    total_sent = models.PositiveIntegerField(default=0, verbose_name='Total envoyé')
    total_delivered = models.PositiveIntegerField(default=0, verbose_name='Total livré')
    total_opened = models.PositiveIntegerField(default=0, verbose_name='Total ouvert')
    total_failed = models.PositiveIntegerField(default=0, verbose_name='Total échoué')
    
    # Taux de conversion
    delivery_rate = models.FloatField(default=0.0, verbose_name='Taux de livraison (%)')
    open_rate = models.FloatField(default=0.0, verbose_name='Taux d\'ouverture (%)')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Analyse de notification'
        verbose_name_plural = 'Analyses de notifications'
        unique_together = ['date']
        ordering = ['-date']

    def __str__(self):
        return f"Analyses du {self.date}"

class NotificationSubscription(models.Model):
    """Abonnements aux notifications"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_subscriptions', verbose_name='Utilisateur')
    subscription_type = models.CharField(max_length=50, verbose_name='Type d\'abonnement')
    subscription_data = models.JSONField(default=dict, blank=True, verbose_name='Données d\'abonnement')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='Abonné le')
    unsubscribed_at = models.DateTimeField(null=True, blank=True, verbose_name='Désabonné le')

    class Meta:
        verbose_name = 'Abonnement aux notifications'
        verbose_name_plural = 'Abonnements aux notifications'
        unique_together = ('user', 'subscription_type')
        ordering = ['-subscribed_at']

    def __str__(self):
        return f"{self.user.username} - {self.subscription_type}"

class NotificationQueue(models.Model):
    """File d'attente des notifications"""
    PRIORITY_CHOICES = [
        ('low', 'Faible'),
        ('normal', 'Normal'),
        ('high', 'Élevé'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='queued_notifications', verbose_name='Utilisateur')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, related_name='queued_notifications', verbose_name='Modèle')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name='Priorité')
    scheduled_at = models.DateTimeField(default=timezone.now, verbose_name='Planifié le')
    attempts = models.PositiveIntegerField(default=0, verbose_name='Tentatives')
    max_attempts = models.PositiveIntegerField(default=3, verbose_name='Tentatives max')
    is_processed = models.BooleanField(default=False, verbose_name='Traité')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='Traité le')
    error_message = models.TextField(blank=True, verbose_name='Message d\'erreur')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')

    class Meta:
        verbose_name = 'Notification en file d\'attente'
        verbose_name_plural = 'Notifications en file d\'attente'
        ordering = ['priority', 'scheduled_at']

    def __str__(self):
        return f"{self.user.username} - {self.template.name} ({self.priority})"