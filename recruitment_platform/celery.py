import os
from celery import Celery

# Définir le module de paramètres Django par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_platform.settings')

app = Celery('recruitment_platform')

# Utiliser la configuration depuis les settings Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Charger automatiquement les tâches depuis toutes les applications enregistrées
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# # À ajouter plus tard 
# app.conf.beat_schedule = {
#     'send-daily-job-alerts': {
#         'task': 'apps.core.tasks.send_daily_alerts',
#         'schedule': crontab(hour=8, minute=0),
#     },
#     'send-weekly-newsletter': {
#         'task': 'apps.core.tasks.send_weekly_newsletter', 
#         'schedule': crontab(day_of_week=1, hour=9, minute=0),
#     },
# }