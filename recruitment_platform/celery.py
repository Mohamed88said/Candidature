import os
from celery import Celery
from celery.schedules import crontab

# Définir le module de paramètres Django par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_platform.settings')

app = Celery('recruitment_platform')

# Utiliser la configuration depuis les settings Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Charger automatiquement les tâches depuis toutes les applications enregistrées
app.autodiscover_tasks()

# Configuration des tâches planifiées (CORRIGÉ)
app.conf.beat_schedule = {
    'send-daily-job-alerts': {
        'task': 'apps.core.tasks.send_daily_alerts',  # Chemin corrigé
        'schedule': crontab(hour=8, minute=0),
    },
    'send-weekly-newsletter': {
        'task': 'apps.core.tasks.send_weekly_newsletter',  # Chemin corrigé
        'schedule': crontab(day_of_week=1, hour=9, minute=0),
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')