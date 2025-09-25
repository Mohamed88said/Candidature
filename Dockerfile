FROM python:3.11-slim

# Variables d'environnement - CELERY DÉSACTIVÉ
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE recruitment_platform.settings
ENV CELERY_TASK_ALWAYS_EAGER True
ENV CELERY_BROKER_URL memory://

# Répertoire de travail
WORKDIR /app

# Dépendances système MINIMALES
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Copier les requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p staticfiles media

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput

# Exposer le port
EXPOSE 10000

# Script de démarrage SIMPLIFIÉ - SEULEMENT GUNICORN
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "1", "--timeout", "120", "--preload", "recruitment_platform.wsgi:application"]