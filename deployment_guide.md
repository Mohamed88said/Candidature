# Guide de Déploiement - Plateforme de Recrutement Django

## Prérequis

### ServGNF
- Ubuntu 20.04+ ou CentOS 8+
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Nginx
- SSL Certificate (Let's Encrypt recommandé)

### Services externes
- Compte email SMTP (Gmail, SendGrid, etc.)
- Stockage de fichiers (AWS S3 optionnel)

## Installation sur ServGNF de Production

### 1. Préparation du servGNF

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib redis-server nginx supervisor git

# Installation de Node.js (pour les assets)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 2. Configuration PostgreSQL

```bash
# Connexion à PostgreSQL
sudo -u postgres psql

# Création de la base de données et utilisatGNF
CREATE DATABASE recruitment_db;
CREATE USER recruitment_user WITH PASSWORD 'votre_mot_de_passe_securise';
ALTER ROLE recruitment_user SET client_encoding TO 'utf8';
ALTER ROLE recruitment_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE recruitment_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE recruitment_db TO recruitment_user;
\q
```

### 3. Déploiement de l'application

```bash
# Création de l'utilisatGNF système
sudo adduser --system --group --home /opt/recruitment recruitment

# Clonage du projet
sudo -u recruitment git clone https://github.com/votre-repo/recruitment-platform.git /opt/recruitment/app
cd /opt/recruitment/app

# Création de l'environnement virtuel
sudo -u recruitment python3 -m venv /opt/recruitment/venv
sudo -u recruitment /opt/recruitment/venv/bin/pip install -r requirements.txt

# Configuration des variables d'environnement
sudo -u recruitment cp .env.example .env
sudo -u recruitment nano .env
```

### 4. Configuration .env de production

```bash
DEBUG=False
SECRET_KEY=votre_cle_secrete_tres_longue_et_aleatoire
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com

# Base de données
DATABASE_URL=postgresql://recruitment_user:votre_mot_de_passe@localhost:5432/recruitment_db

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@votre-domaine.com

# Redis
REDIS_URL=redis://localhost:6379/0

# Sécurité
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True

# Fichiers statiques et media
STATIC_URL=/static/
MEDIA_URL=/media/
```

### 5. Initialisation de l'application

```bash
# Migrations de base de données
sudo -u recruitment /opt/recruitment/venv/bin/python manage.py migrate

# Création du superutilisatGNF
sudo -u recruitment /opt/recruitment/venv/bin/python manage.py createsuperuser

# Collecte des fichiers statiques
sudo -u recruitment /opt/recruitment/venv/bin/python manage.py collectstatic --noinput

# Chargement des données initiales
sudo -u recruitment /opt/recruitment/venv/bin/python manage.py loaddata fixtures/initial_data.json

# Permissions des fichiers
sudo chown -R recruitment:recruitment /opt/recruitment/
sudo chmod -R 755 /opt/recruitment/app/media/
sudo chmod -R 755 /opt/recruitment/app/staticfiles/
```

### 6. Configuration Gunicorn

```bash
# Création du fichier de configuration Gunicorn
sudo nano /opt/recruitment/gunicorn.conf.py
```

```python
# /opt/recruitment/gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
user = "recruitment"
group = "recruitment"
tmp_upload_dir = None
errorlog = "/opt/recruitment/logs/gunicorn_error.log"
accesslog = "/opt/recruitment/logs/gunicorn_access.log"
loglevel = "info"
```

### 7. Configuration Supervisor

```bash
# Création des répertoires de logs
sudo mkdir -p /opt/recruitment/logs
sudo chown recruitment:recruitment /opt/recruitment/logs

# Configuration Supervisor pour Django
sudo nano /etc/supervisor/conf.d/recruitment-django.conf
```

```ini
[program:recruitment-django]
command=/opt/recruitment/venv/bin/gunicorn recruitment_platform.wsgi:application -c /opt/recruitment/gunicorn.conf.py
directory=/opt/recruitment/app
user=recruitment
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/recruitment/logs/django.log
environment=PATH="/opt/recruitment/venv/bin"
```

```bash
# Configuration Supervisor pour Celery Worker
sudo nano /etc/supervisor/conf.d/recruitment-celery.conf
```

```ini
[program:recruitment-celery]
command=/opt/recruitment/venv/bin/celery -A recruitment_platform worker -l info
directory=/opt/recruitment/app
user=recruitment
numprocs=1
stdout_logfile=/opt/recruitment/logs/celery.log
stderr_logfile=/opt/recruitment/logs/celery.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
killasgroup=true
priority=998
environment=PATH="/opt/recruitment/venv/bin"
```

```bash
# Configuration Supervisor pour Celery Beat
sudo nano /etc/supervisor/conf.d/recruitment-celery-beat.conf
```

```ini
[program:recruitment-celery-beat]
command=/opt/recruitment/venv/bin/celery -A recruitment_platform beat -l info
directory=/opt/recruitment/app
user=recruitment
numprocs=1
stdout_logfile=/opt/recruitment/logs/celery-beat.log
stderr_logfile=/opt/recruitment/logs/celery-beat.log
autostart=true
autorestart=true
startsecs=10
priority=999
environment=PATH="/opt/recruitment/venv/bin"
```

### 8. Configuration Nginx

```bash
sudo nano /etc/nginx/sites-available/recruitment
```

```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name votre-domaine.com www.votre-domaine.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/votre-domaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/votre-domaine.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;

    # Client Max Body Size
    client_max_body_size 10M;

    # Static Files
    location /static/ {
        alias /opt/recruitment/app/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media Files
    location /media/ {
        alias /opt/recruitment/app/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Django Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 9. Activation des services

```bash
# Activation du site Nginx
sudo ln -s /etc/nginx/sites-available/recruitment /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Démarrage des services Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all

# Vérification du statut
sudo supervisorctl status
```

### 10. Configuration SSL avec Let's Encrypt

```bash
# Installation Certbot
sudo apt install certbot python3-certbot-nginx

# Obtention du certificat SSL
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com

# Test de renouvellement automatique
sudo certbot renew --dry-run
```

## Maintenance et Monitoring

### Scripts de sauvegarde

```bash
# Création du script de sauvegarde
sudo nano /opt/recruitment/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/recruitment/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Création du répertoire de sauvegarde
mkdir -p $BACKUP_DIR

# Sauvegarde de la base de données
pg_dump -h localhost -U recruitment_user recruitment_db > $BACKUP_DIR/db_$DATE.sql

# Sauvegarde des fichiers media
tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C /opt/recruitment/app media/

# Nettoyage des anciennes sauvegardes (garde 7 jours)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Sauvegarde terminée: $DATE"
```

```bash
# Rendre le script exécutable
sudo chmod +x /opt/recruitment/backup.sh

# Ajouter au crontab pour exécution quotidienne
sudo crontab -e
# Ajouter: 0 2 * * * /opt/recruitment/backup.sh
```

### Monitoring des logs

```bash
# Surveillance des logs en temps réel
sudo tail -f /opt/recruitment/logs/django.log
sudo tail -f /opt/recruitment/logs/celery.log
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Mise à jour de l'application

```bash
# Script de mise à jour
sudo nano /opt/recruitment/update.sh
```

```bash
#!/bin/bash
cd /opt/recruitment/app

# Sauvegarde avant mise à jour
/opt/recruitment/backup.sh

# Mise à jour du code
sudo -u recruitment git pull origin main

# Installation des nouvelles dépendances
sudo -u recruitment /opt/recruitment/venv/bin/pip install -r requirements.txt

# Migrations de base de données
sudo -u recruitment /opt/recruitment/venv/bin/python manage.py migrate

# Collecte des fichiers statiques
sudo -u recruitment /opt/recruitment/venv/bin/python manage.py collectstatic --noinput

# Redémarrage des services
sudo supervisorctl restart all
sudo systemctl reload nginx

echo "Mise à jour terminée"
```

## Optimisations de Performance

### Configuration Redis pour le cache

```python
# Dans settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### Configuration de la base de données

```sql
-- Optimisations PostgreSQL
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
SELECT pg_reload_conf();
```

## Sécurité

### Firewall

```bash
# Configuration UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Fail2Ban

```bash
# Installation
sudo apt install fail2ban

# Configuration
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/*error.log
findtime = 600
bantime = 7200
maxretry = 10
```

## Troubleshooting

### Problèmes courants

1. **ErrGNF 502 Bad Gateway**
   - Vérifier que Gunicorn fonctionne: `sudo supervisorctl status`
   - Vérifier les logs: `sudo tail -f /opt/recruitment/logs/django.log`

2. **Fichiers statiques non chargés**
   - Vérifier la configuration Nginx
   - Relancer `collectstatic`

3. **ErrGNFs de base de données**
   - Vérifier la connexion PostgreSQL
   - Vérifier les permissions utilisatGNF

4. **Problèmes de performance**
   - Activer le cache Redis
   - Optimiser les requêtes de base de données
   - Configurer la compression Nginx

### Commandes utiles

```bash
# Redémarrage complet
sudo supervisorctl restart all
sudo systemctl restart nginx
sudo systemctl restart postgresql
sudo systemctl restart redis

# Vérification des services
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis
sudo supervisorctl status

# Logs
sudo journalctl -u nginx -f
sudo tail -f /opt/recruitment/logs/django.log
```

Ce guide couvre tous les aspects essentiels du déploiement en production. Adaptez les configurations selon vos besoins spécifiques et votre infrastructure.
