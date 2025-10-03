#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_platform.settings')
    
    # Démarrer le keep-alive au démarrage de l'application
    try:
        # Vérifier que nous ne sommes pas en mode test ou commande spécifique
        if len(sys.argv) > 1 and sys.argv[1] in ['runserver', 'gunicorn']:
            from django.conf import settings
            if getattr(settings, 'ENABLE_KEEP_ALIVE', True):
                from apps.core.keep_alive import start_keep_alive
                start_keep_alive()
                print("🚀 Service keep-alive démarré depuis manage.py")
    except Exception as e:
        print(f"⚠️ Impossible de démarrer le keep-alive: {e}")
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()