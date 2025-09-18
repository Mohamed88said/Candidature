# Dockerfile pour la plateforme de recrutement Django

FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE recruitment_platform.settings

# Répertoire de travail
WORKDIR /app

# Dépendances système
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        libjpeg-dev \
        libpng-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        tcl8.6-dev \
        tk8.6-dev \
        python3-tk \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . /app/

# Créer les répertoires nécessaires
RUN mkdir -p /app/staticfiles /app/media

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput

# Exposer le port
EXPOSE 8000

# Script de démarrage
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Commande par défaut
CMD ["/app/docker-entrypoint.sh"]