from django.apps import AppConfig


class AlertsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.alerts'
    verbose_name = 'Alertes personnalisées'
    
    def ready(self):
        """Initialiser les signaux quand l'application est prête"""
        import apps.alerts.signals