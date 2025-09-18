from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardWidget(models.Model):
    """Widgets personnalisables du dashboard"""
    WIDGET_TYPES = (
        ('stats', 'Statistiques'),
        ('chart', 'Graphique'),
        ('recent_activity', 'Activité récente'),
        ('quick_actions', 'Actions rapides'),
        ('notifications', 'Notifications'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboard_widgets')
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    title = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)  # Configuration spécifique au widget
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Widget Dashboard'
        verbose_name_plural = 'Widgets Dashboard'
        ordering = ['position']

    def __str__(self):
        return f"{self.title} - {self.user.full_name}"


class SystemNotification(models.Model):
    """Notifications système"""
    NOTIFICATION_TYPES = (
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
        ('success', 'Succès'),
    )

    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    target_users = models.ManyToManyField(User, blank=True, related_name='system_notifications')
    is_global = models.BooleanField(default=False)  # Visible par tous les utilisateurs
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Notification Système'
        verbose_name_plural = 'Notifications Système'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class UserNotificationRead(models.Model):
    """Suivi des notifications lues par utilisateur"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey(SystemNotification, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'notification']