# This file makes Python treat the directory as a package

# Ceci garantira que l'app est toujours importée quand
# Django démarre pour que shared_task utilise cette app.
from .celery import app as celery_app

__all__ = ('celery_app',)