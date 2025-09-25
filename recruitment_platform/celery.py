import os
from celery import Celery

# DÉTECTION AUTOMATIQUE - Si en production, désactiver Celery
if os.environ.get('RENDER', '') or os.environ.get('CELERY_TASK_ALWAYS_EAGER', '').lower() == 'true':
    # Mode production - créer une app factice qui ne fait rien
    app = None
    
    # Décorateur factice pour les tâches
    class MockTask:
        def __call__(self, *args, **kwargs):
            return None
        def delay(self, *args, **kwargs):
            return None
    
    def mock_task(*args, **kwargs):
        def decorator(func):
            return MockTask()
        return decorator
    
    # Remplacer les décorateurs
    task = mock_task
else:
    # Mode développement normal
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_platform.settings')
    app = Celery('recruitment_platform')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()

    @app.task(bind=True, ignore_result=True)
    def debug_task(self):
        print(f'Request: {self.request!r}')