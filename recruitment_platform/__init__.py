# recruitment_platform/__init__.py
import os

# Charger Celery seulement si on est PAS en mode production
if not os.environ.get('RENDER', '') and os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'False').lower() != 'true':
    try:
        from .celery import app as celery_app
        __all__ = ('celery_app',)
    except ImportError:
        # Si Celery n'est pas disponible, continuer sans
        __all__ = ()
else:
    # En production, ne pas charger Celery
    __all__ = ()