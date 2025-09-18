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