from django.apps import AppConfig

class JobsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.jobs'
    verbose_name = 'Offres d\'emploi'
    
    def ready(self):
        # Importer les signaux pour les emails automatiques
        import apps.jobs.signals