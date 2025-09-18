# Plateforme de Recrutement Django

## Description
Plateforme ultra-complète de gestion de recrutement avec intelligence artificielle, permettant aux candidats de postuler à des offres d'emploi et aux administrateurs de gérer tout le processus de recrutement avec des outils avancés d'analyse, de suivi, et de personnalisation complète.

## Fonctionnalités

### Pour les Candidats
- ✅ Inscription et authentification
- ✅ Profil ultra-détaillé avec toutes les informations personnelles
- ✅ Gestion avancée des expériences professionnelles multiples
- ✅ Calcul intelligent des années d'expérience (générale et spécialisée)
- ✅ Détection automatique de l'expérience pertinente par mots-clés
- ✅ Gestion du parcours scolaire et formations
- ✅ Compétences avancées avec niveaux et certifications
- ✅ Langues avec niveaux CECR
- ✅ Références professionnelles
- ✅ Portfolio et projets personnels
- ✅ Upload de CV et documents
- ✅ Candidature aux offres d'emploi
- ✅ Suivi des candidatures
- ✅ Notifications par email
- ✅ Système de matching intelligent
- ✅ Recommandations personnalisées
- ✅ Alertes emploi avancées

### Pour les Administrateurs
- ✅ Dashboard complet avec statistiques
- ✅ Gestion complète du contenu du site (pages dynamiques)
- ✅ Personnalisation des couleurs et thèmes
- ✅ Configuration avancée des paramètres
- ✅ Gestion des offres d'emploi
- ✅ Gestion des candidatures
- ✅ Système de notation des candidats
- ✅ Commentaires et feedback
- ✅ Export Excel des données
- ✅ Gestion des utilisateurs
- ✅ Rapports détaillés
- ✅ Analytics avancées avec graphiques
- ✅ Système de notifications
- ✅ Gestion des entretiens
- ✅ Historique complet des actions
- ✅ Système de scoring automatique

### Pages Générales
- ✅ Page d'accueil dynamique et personnalisable
- ✅ Page de contact avec formulaire avancé
- ✅ À propos entièrement configurable via admin
- ✅ Conditions d'utilisation éditables
- ✅ Politique de confidentialité configurable
- ✅ FAQ dynamique par catégories
- ✅ Blog intégré avec système de tags
- ✅ Newsletter avec gestion des abonnements
- ✅ Plan du site automatique
- ✅ Recherche globale avancée

### Fonctionnalités Avancées
- ✅ Système de thèmes et personnalisation visuelle
- ✅ Calcul intelligent de l'expérience professionnelle
- ✅ Matching automatique candidat-offre
- ✅ Système de scoring des candidats
- ✅ Analytics en temps réel
- ✅ Notifications push et email
- ✅ Système de workflow de recrutement
- ✅ Gestion des entretiens avec calendrier
- ✅ Export de données avancé
- ✅ API REST pour intégrations
- ✅ Système de cache pour performance
- ✅ Logs d'activité détaillés
## Technologies Utilisées
- **Backend**: Django 4.2+
- **Base de données**: PostgreSQL (SQLite pour le développement)
- **Frontend**: Bootstrap 5, JavaScript
- **Authentification**: Django Auth
- **Export**: openpyxl pour Excel
- **Email**: Django Email Backend
- **Media**: Django Media Files
- **Cache**: Redis
- **Tâches asynchrones**: Celery
- **API**: Django REST Framework
- **Graphiques**: Chart.js
- **Formulaires**: Django Crispy Forms
- **Conteneurisation**: Docker

## Installation

### Prérequis
- Python 3.8+
- pip
- virtualenv (recommandé)
- PostgreSQL (pour la production)

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone <votre-repo>
cd recruitment-platform
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration de la base de données**
```bash
# Copier le fichier de configuration
cp .env.example .env
# Éditer .env avec vos paramètres
```

5. **Migrations de base de données**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

7. **Collecter les fichiers statiques**
```bash
python manage.py collectstatic
```

8. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

Le site sera accessible sur `http://127.0.0.1:8000/`

## Structure du Projet

```
recruitment_platform/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── recruitment_platform/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── __init__.py
│   ├── accounts/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── signals.py
│   │   └── migrations/
│   ├── jobs/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── migrations/
│   ├── applications/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── migrations/
│   ├── dashboard/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── utils.py
│   │   └── migrations/
│   └── core/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       ├── forms.py
│       └── migrations/
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   ├── profile_edit.html
│   │   └── dashboard.html
│   ├── jobs/
│   │   ├── job_list.html
│   │   ├── job_detail.html
│   │   ├── job_create.html
│   │   └── job_edit.html
│   ├── applications/
│   │   ├── application_form.html
│   │   ├── application_list.html
│   │   └── application_detail.html
│   ├── dashboard/
│   │   ├── admin_dashboard.html
│   │   ├── statistics.html
│   │   ├── candidates.html
│   │   └── reports.html
│   └── core/
│       ├── contact.html
│       ├── about.html
│       ├── terms.html
│       └── privacy.html
├── static/
│   ├── css/
│   │   ├── bootstrap.min.css
│   │   └── custom.css
│   ├── js/
│   │   ├── bootstrap.min.js
│   │   └── custom.js
│   └── images/
├── media/
│   ├── cvs/
│   ├── documents/
│   └── profile_pictures/
└── utils/
    ├── __init__.py
    ├── decorators.py
    ├── helpers.py
    └── export.py
```

## Configuration

### Variables d'environnement (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

### Base de données PostgreSQL (Production)
```
DATABASE_URL=postgresql://username:password@localhost:5432/recruitment_db
```

## Utilisation

### Accès Admin
- URL: `/admin/`
- Créer un superutilisateur avec `python manage.py createsuperuser`

### Candidats
1. S'inscrire sur `/accounts/register/`
2. Compléter le profil
3. Postuler aux offres disponibles

### Administrateurs
1. Se connecter via `/admin/` ou `/dashboard/`
2. Gérer les offres d'emploi
3. Consulter les candidatures
4. Exporter les données

## API Endpoints

### Authentification
- `POST /accounts/register/` - Inscription
- `POST /accounts/login/` - Connexion
- `POST /accounts/logout/` - Déconnexion

### Profils
- `GET /accounts/profile/` - Voir profil
- `PUT /accounts/profile/edit/` - Modifier profil

### Offres d'emploi
- `GET /jobs/` - Liste des offres
- `GET /jobs/<id>/` - Détail d'une offre
- `POST /jobs/create/` - Créer offre (admin)

### Candidatures
- `POST /applications/apply/<job_id>/` - Postuler
- `GET /applications/` - Mes candidatures

### Dashboard
- `GET /dashboard/` - Dashboard admin
- `GET /dashboard/export/` - Export Excel

## Tests

```bash
# Lancer tous les tests
python manage.py test

# Tests spécifiques
python manage.py test apps.accounts
python manage.py test apps.jobs
```

## Déploiement

### Heroku
1. Installer Heroku CLI
2. `heroku create your-app-name`
3. `git push heroku main`
4. `heroku run python manage.py migrate`
5. `heroku run python manage.py createsuperuser`

### Docker
```bash
docker build -t recruitment-platform .
docker run -p 8000:8000 recruitment-platform
```

## Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Push (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## Support

Pour toute question ou problème :
- Créer une issue sur GitHub
- Email: support@recruitment-platform.com

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Changelog

### Version 1.0.0
- Système d'authentification complet
- Gestion des profils candidats
- Système de candidatures
- Dashboard administrateur
- Export Excel
- Système de notation et commentaires