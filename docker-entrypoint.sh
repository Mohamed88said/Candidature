#!/bin/bash

# Script de démarrage Docker pour la plateforme de recrutement

set -e

# Attendre que la base de données soit prête
echo "Attente de la base de données..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Base de données prête!"

# Exécuter les migrations
echo "Exécution des migrations..."
python manage.py migrate --noinput

# Créer un superutilisateur si les variables d'environnement sont définies
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Création du superutilisateur..."
    python manage.py createsuperuser --noinput || true
fi

# Collecter les fichiers statiques
echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Charger les données initiales si elles existent
if [ -f "fixtures/initial_data.json" ]; then
    echo "Chargement des données initiales..."
    python manage.py loaddata fixtures/initial_data.json
fi

# Démarrer le serveur
echo "Démarrage du serveur Django..."
if [ "$DEBUG" = "True" ]; then
    python manage.py runserver 0.0.0.0:8000
else
    gunicorn recruitment_platform.wsgi:application --bind 0.0.0.0:8000 --workers 3
fi