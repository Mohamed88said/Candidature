import os
from celery import Celery

# Définir le module de paramètres Django par défaut pour le programme 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_platform.settings')

app = Celery('recruitment_platform')

# Utiliser une chaîne ici signifie que le worker n'a pas besoin de sérialiser
# l'objet de configuration vers les processus enfants.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Charger les modules de tâches de toutes les applications Django enregistrées.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')




# Dans celery.py
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-daily-alerts': {
        'task': 'apps.core.tasks.task_send_daily_alerts',
        'schedule': crontab(hour=8, minute=0),  # Tous les jours à 8h
    },
}






os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_platform.settings')

app = Celery('recruitment_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Ajoutez cette configuration
app.conf.beat_schedule = {
    'send-daily-job-alerts': {
        'task': 'apps.core.management.commands.send_daily_alerts',
        'schedule': crontab(hour=8, minute=0),  # Tous les jours à 8h00
    },
    'send-weekly-newsletter': {
        'task': 'apps.core.tasks.send_weekly_newsletter',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Tous les lundis à 9h00
    },
}