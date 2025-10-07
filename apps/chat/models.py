from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.jobs.models import Job
from apps.applications.models import Application
from cloudinary.models import CloudinaryField
import uuid

User = get_user_model()


class ChatRoom(models.Model):
    """Salle de chat entre un candidat et un recruteur"""
    ROOM_TYPES = (
        ('application', 'Candidature'),
        ('general', 'Général'),
        ('interview', 'Entretien'),
        ('follow_up', 'Suivi'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='application')
    
    # Participants
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_candidate')
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_recruiter')
    
    # Contexte
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_rooms')
    application = models.ForeignKey(Application, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_rooms')
    
    # Métadonnées
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    
    # Statistiques
    message_count = models.PositiveIntegerField(default=0)
    last_message_at = models.DateTimeField(null=True, blank=True)
    last_message_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_messages')
    
    # Notifications
    candidate_notifications = models.PositiveIntegerField(default=0)
    recruiter_notifications = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Salle de Chat'
        verbose_name_plural = 'Salles de Chat'
        unique_together = ['candidate', 'recruiter', 'job']
        ordering = ['-last_message_at', '-created_at']
    
    def __str__(self):
        return f"Chat: {self.candidate.full_name} ↔ {self.recruiter.full_name}"
    
    def get_display_title(self):
        """Retourne le titre d'affichage de la salle"""
        if self.title:
            return self.title
        elif self.job:
            return f"Candidature: {self.job.title}"
        else:
            return f"Chat avec {self.recruiter.full_name}"
    
    def get_other_participant(self, user):
        """Retourne l'autre participant de la conversation"""
        if user == self.candidate:
            return self.recruiter
        return self.candidate
    
    def mark_as_read(self, user):
        """Marque les messages comme lus pour un utilisateur"""
        if user == self.candidate:
            self.candidate_notifications = 0
        else:
            self.recruiter_notifications = 0
        self.save(update_fields=['candidate_notifications', 'recruiter_notifications'])
    
    def add_notification(self, user):
        """Ajoute une notification pour l'autre utilisateur"""
        if user == self.candidate:
            self.recruiter_notifications += 1
        else:
            self.candidate_notifications += 1
        self.save(update_fields=['candidate_notifications', 'recruiter_notifications'])


class Message(models.Model):
    """Message dans une salle de chat"""
    MESSAGE_TYPES = (
        ('text', 'Texte'),
        ('image', 'Image'),
        ('file', 'Fichier'),
        ('video', 'Vidéo'),
        ('audio', 'Audio'),
        ('system', 'Système'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    # Contenu
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    
    # Fichiers
    attachment = CloudinaryField(
        'raw',
        folder='recruitment/chat/attachments/',
        null=True,
        blank=True,
        resource_type='raw'
    )
    
    # Métadonnées
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    
    # Statut de lecture
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Réactions
    reactions = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message de {self.sender.full_name} dans {self.room}"
    
    def mark_as_read(self):
        """Marque le message comme lu"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def add_reaction(self, user, emoji):
        """Ajoute une réaction au message"""
        if emoji not in self.reactions:
            self.reactions[emoji] = []
        
        if user.id not in self.reactions[emoji]:
            self.reactions[emoji].append(user.id)
            self.save(update_fields=['reactions'])
    
    def remove_reaction(self, user, emoji):
        """Supprime une réaction du message"""
        if emoji in self.reactions and user.id in self.reactions[emoji]:
            self.reactions[emoji].remove(user.id)
            if not self.reactions[emoji]:
                del self.reactions[emoji]
            self.save(update_fields=['reactions'])
    
    def get_reaction_count(self, emoji):
        """Retourne le nombre de réactions pour un emoji"""
        return len(self.reactions.get(emoji, []))
    
    def has_user_reacted(self, user, emoji):
        """Vérifie si un utilisateur a réagi avec un emoji"""
        return user.id in self.reactions.get(emoji, [])


class ChatParticipant(models.Model):
    """Participant à une salle de chat avec des préférences"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_participations')
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='participants')
    
    # Préférences
    is_muted = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    last_read_at = models.DateTimeField(null=True, blank=True)
    
    # Statut
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Participant au Chat'
        verbose_name_plural = 'Participants au Chat'
        unique_together = ['user', 'room']
    
    def __str__(self):
        return f"{self.user.full_name} dans {self.room}"


class ChatNotification(models.Model):
    """Notification de chat"""
    NOTIFICATION_TYPES = (
        ('new_message', 'Nouveau message'),
        ('message_reaction', 'Réaction au message'),
        ('room_created', 'Nouvelle salle créée'),
        ('user_joined', 'Utilisateur rejoint'),
        ('user_left', 'Utilisateur parti'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_notifications')
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notification de Chat'
        verbose_name_plural = 'Notifications de Chat'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification pour {self.user.full_name}: {self.title}"
    
    def mark_as_read(self):
        """Marque la notification comme lue"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class ChatSettings(models.Model):
    """Paramètres de chat pour un utilisateur"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chat_settings')
    
    # Notifications
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    sound_notifications = models.BooleanField(default=True)
    
    # Apparence
    theme = models.CharField(max_length=20, choices=[
        ('light', 'Clair'),
        ('dark', 'Sombre'),
        ('auto', 'Automatique'),
    ], default='auto')
    
    font_size = models.CharField(max_length=20, choices=[
        ('small', 'Petit'),
        ('medium', 'Moyen'),
        ('large', 'Grand'),
    ], default='medium')
    
    # Comportement
    show_typing_indicator = models.BooleanField(default=True)
    show_read_receipts = models.BooleanField(default=True)
    auto_download_media = models.BooleanField(default=False)
    
    # Confidentialité
    show_online_status = models.BooleanField(default=True)
    allow_direct_messages = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Paramètres de Chat'
        verbose_name_plural = 'Paramètres de Chat'
    
    def __str__(self):
        return f"Paramètres chat de {self.user.full_name}"


class ChatBlock(models.Model):
    """Utilisateurs bloqués dans le chat"""
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_users')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Utilisateur Bloqué'
        verbose_name_plural = 'Utilisateurs Bloqués'
        unique_together = ['blocker', 'blocked']
    
    def __str__(self):
        return f"{self.blocker.full_name} a bloqué {self.blocked.full_name}"


class ChatReport(models.Model):
    """Signalement de contenu inapproprié"""
    REPORT_TYPES = (
        ('spam', 'Spam'),
        ('harassment', 'Harcèlement'),
        ('inappropriate_content', 'Contenu inapproprié'),
        ('fake_profile', 'Profil faux'),
        ('other', 'Autre'),
    )
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_reports_made')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_reports_received')
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='reports')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    description = models.TextField()
    
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_reports')
    resolution_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Signalement de Chat'
        verbose_name_plural = 'Signalements de Chat'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Signalement de {self.reported_user.full_name} par {self.reporter.full_name}"

