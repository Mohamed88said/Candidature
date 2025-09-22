# Plateforme de Recrutement Django

## Description
Plateforme ultra-complÃ¨te de gestion de recrutement avec intelligence artificielle, permettant aux candidats de postuler Ã  des offres d'emploi et aux administratGNFs de gÃ©rer tout le processus de recrutement avec des outils avancÃ©s d'analyse, de suivi, et de personnalisation complÃ¨te.

## FonctionnalitÃ©s

### Pour les Candidats
- âœ… Inscription et authentification
- âœ… Profil ultra-dÃ©taillÃ© avec toutes les informations personnelles
- âœ… Gestion avancÃ©e des expÃ©riences professionnelles multiples
- âœ… Calcul intelligent des annÃ©es d'expÃ©rience (gÃ©nÃ©rale et spÃ©cialisÃ©e)
- âœ… DÃ©tection automatique de l'expÃ©rience pertinente par mots-clÃ©s
- âœ… Gestion du parcours scolaire et formations
- âœ… CompÃ©tences avancÃ©es avec niveaux et certifications
- âœ… Langues avec niveaux CECR
- âœ… RÃ©fÃ©rences professionnelles
- âœ… Portfolio et projets personnels
- âœ… Upload de CV et documents
- âœ… Candidature aux offres d'emploi
- âœ… Suivi des candidatures
- âœ… Notifications par email
- âœ… SystÃ¨me de matching intelligent
- âœ… Recommandations personnalisÃ©es
- âœ… Alertes emploi avancÃ©es

### Pour les AdministratGNFs
- âœ… Dashboard complet avec statistiques
- âœ… Gestion complÃ¨te du contenu du site (pages dynamiques)
- âœ… Personnalisation des coulGNFs et thÃ¨mes
- âœ… Configuration avancÃ©e des paramÃ¨tres
- âœ… Gestion des offres d'emploi
- âœ… Gestion des candidatures
- âœ… SystÃ¨me de notation des candidats
- âœ… Commentaires et feedback
- âœ… Export Excel des donnÃ©es
- âœ… Gestion des utilisatGNFs
- âœ… Rapports dÃ©taillÃ©s
- âœ… Analytics avancÃ©es avec graphiques
- âœ… SystÃ¨me de notifications
- âœ… Gestion des entretiens
- âœ… Historique complet des actions
- âœ… SystÃ¨me de scoring automatique

### Pages GÃ©nÃ©rales
- âœ… Page d'accueil dynamique et personnalisable
- âœ… Page de contact avec formulaire avancÃ©
- âœ… ÃGNF propos entiÃ¨rement configurable via admin
- âœ… Conditions d'utilisation Ã©ditables
- âœ… Politique de confidentialitÃ© configurable
- âœ… FAQ dynamique par catÃ©gories
- âœ… Blog intÃ©grÃ© avec systÃ¨me de tags
- âœ… Newsletter avec gestion des abonnements
- âœ… Plan du site automatique
- âœ… Recherche globale avancÃ©e

### FonctionnalitÃ©s AvancÃ©es
- âœ… SystÃ¨me de thÃ¨mes et personnalisation visuelle
- âœ… Calcul intelligent de l'expÃ©rience professionnelle
- âœ… Matching automatique candidat-offre
- âœ… SystÃ¨me de scoring des candidats
- âœ… Analytics en temps rÃ©el
- âœ… Notifications push et email
- âœ… SystÃ¨me de workflow de recrutement
- âœ… Gestion des entretiens avec calendrier
- âœ… Export de donnÃ©es avancÃ©
- âœ… API REST pour intÃ©grations
- âœ… SystÃ¨me de cache pour performance
- âœ… Logs d'activitÃ© dÃ©taillÃ©s
## Technologies UtilisÃ©es
- **Backend**: Django 4.2+
- **Base de donnÃ©es**: PostgreSQL (SQLite pour le dÃ©veloppement)
- **Frontend**: Bootstrap 5, JavaScript
- **Authentification**: Django Auth
- **Export**: openpyxl pour Excel
- **Email**: Django Email Backend
- **Media**: Django Media Files
- **Cache**: Redis
- **TÃ¢ches asynchrones**: Celery
- **API**: Django REST Framework
- **Graphiques**: Chart.js
- **Formulaires**: Django Crispy Forms
- **ContenGNFisation**: Docker

## Installation

### PrÃ©requis
- Python 3.8+
- pip
- virtualenv (recommandÃ©)
- PostgreSQL (pour la production)

### Ã‰tapes d'installation

1. **Cloner le projet**
```bash
git clone <votre-repo>
cd recruitment-platform
```

2. **CrÃ©er un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer les dÃ©pendances**
```bash
pip install -r requirements.txt
```

4. **Configuration de la base de donnÃ©es**
```bash
# Copier le fichier de configuration
cp .env.example .env
# Ã‰diter .env avec vos paramÃ¨tres
```

5. **Migrations de base de donnÃ©es**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **CrÃ©er un superutilisatGNF**
```bash
python manage.py createsuperuser
```

7. **Collecter les fichiers statiques**
```bash
python manage.py collectstatic
```

8. **Lancer le servGNF de dÃ©veloppement**
```bash
python manage.py runserver
```

Le site sera accessible sur `http://127.0.0.1:8000/`

## Structure du Projet

```
recruitment_platform/
â”œâ”GNFâ”GNF manage.py
â”œâ”GNFâ”GNF requirements.txt
â”œâ”GNFâ”GNF .env.example
â”œâ”GNFâ”GNF README.md
â”œâ”GNFâ”GNF recruitment_platform/
â”‚   â”œâ”GNFâ”GNF __init__.py
â”‚   â”œâ”GNFâ”GNF settings.py
â”‚   â”œâ”GNFâ”GNF urls.py
â”‚   â”œâ”GNFâ”GNF wsgi.py
â”‚   â””â”GNFâ”GNF asgi.py
â”œâ”GNFâ”GNF apps/
â”‚   â”œâ”GNFâ”GNF __init__.py
â”‚   â”œâ”GNFâ”GNF accounts/
â”‚   â”‚   â”œâ”GNFâ”GNF __init__.py
â”‚   â”‚   â”œâ”GNFâ”GNF admin.py
â”‚   â”‚   â”œâ”GNFâ”GNF apps.py
â”‚   â”‚   â”œâ”GNFâ”GNF models.py
â”‚   â”‚   â”œâ”GNFâ”GNF views.py
â”‚   â”‚   â”œâ”GNFâ”GNF urls.py
â”‚   â”‚   â”œâ”GNFâ”GNF forms.py
â”‚   â”‚   â”œâ”GNFâ”GNF signals.py
â”‚   â”‚   â””â”GNFâ”GNF migrations/
â”‚   â”œâ”GNFâ”GNF jobs/
â”‚   â”‚   â”œâ”GNFâ”GNF __init__.py
â”‚   â”‚   â”œâ”GNFâ”GNF admin.py
â”‚   â”‚   â”œâ”GNFâ”GNF apps.py
â”‚   â”‚   â”œâ”GNFâ”GNF models.py
â”‚   â”‚   â”œâ”GNFâ”GNF views.py
â”‚   â”‚   â”œâ”GNFâ”GNF urls.py
â”‚   â”‚   â”œâ”GNFâ”GNF forms.py
â”‚   â”‚   â””â”GNFâ”GNF migrations/
â”‚   â”œâ”GNFâ”GNF applications/
â”‚   â”‚   â”œâ”GNFâ”GNF __init__.py
â”‚   â”‚   â”œâ”GNFâ”GNF admin.py
â”‚   â”‚   â”œâ”GNFâ”GNF apps.py
â”‚   â”‚   â”œâ”GNFâ”GNF models.py
â”‚   â”‚   â”œâ”GNFâ”GNF views.py
â”‚   â”‚   â”œâ”GNFâ”GNF urls.py
â”‚   â”‚   â”œâ”GNFâ”GNF forms.py
â”‚   â”‚   â””â”GNFâ”GNF migrations/
â”‚   â”œâ”GNFâ”GNF dashboard/
â”‚   â”‚   â”œâ”GNFâ”GNF __init__.py
â”‚   â”‚   â”œâ”GNFâ”GNF admin.py
â”‚   â”‚   â”œâ”GNFâ”GNF apps.py
â”‚   â”‚   â”œâ”GNFâ”GNF models.py
â”‚   â”‚   â”œâ”GNFâ”GNF views.py
â”‚   â”‚   â”œâ”GNFâ”GNF urls.py
â”‚   â”‚   â”œâ”GNFâ”GNF utils.py
â”‚   â”‚   â””â”GNFâ”GNF migrations/
â”‚   â””â”GNFâ”GNF core/
â”‚       â”œâ”GNFâ”GNF __init__.py
â”‚       â”œâ”GNFâ”GNF admin.py
â”‚       â”œâ”GNFâ”GNF apps.py
â”‚       â”œâ”GNFâ”GNF models.py
â”‚       â”œâ”GNFâ”GNF views.py
â”‚       â”œâ”GNFâ”GNF urls.py
â”‚       â”œâ”GNFâ”GNF forms.py
â”‚       â””â”GNFâ”GNF migrations/
â”œâ”GNFâ”GNF templates/
â”‚   â”œâ”GNFâ”GNF base.html
â”‚   â”œâ”GNFâ”GNF home.html
â”‚   â”œâ”GNFâ”GNF accounts/
â”‚   â”‚   â”œâ”GNFâ”GNF login.html
â”‚   â”‚   â”œâ”GNFâ”GNF register.html
â”‚   â”‚   â”œâ”GNFâ”GNF profile.html
â”‚   â”‚   â”œâ”GNFâ”GNF profile_edit.html
â”‚   â”‚   â””â”GNFâ”GNF dashboard.html
â”‚   â”œâ”GNFâ”GNF jobs/
â”‚   â”‚   â”œâ”GNFâ”GNF job_list.html
â”‚   â”‚   â”œâ”GNFâ”GNF job_detail.html
â”‚   â”‚   â”œâ”GNFâ”GNF job_create.html
â”‚   â”‚   â””â”GNFâ”GNF job_edit.html
â”‚   â”œâ”GNFâ”GNF applications/
â”‚   â”‚   â”œâ”GNFâ”GNF application_form.html
â”‚   â”‚   â”œâ”GNFâ”GNF application_list.html
â”‚   â”‚   â””â”GNFâ”GNF application_detail.html
â”‚   â”œâ”GNFâ”GNF dashboard/
â”‚   â”‚   â”œâ”GNFâ”GNF admin_dashboard.html
â”‚   â”‚   â”œâ”GNFâ”GNF statistics.html
â”‚   â”‚   â”œâ”GNFâ”GNF candidates.html
â”‚   â”‚   â””â”GNFâ”GNF reports.html
â”‚   â””â”GNFâ”GNF core/
â”‚       â”œâ”GNFâ”GNF contact.html
â”‚       â”œâ”GNFâ”GNF about.html
â”‚       â”œâ”GNFâ”GNF terms.html
â”‚       â””â”GNFâ”GNF privacy.html
â”œâ”GNFâ”GNF static/
â”‚   â”œâ”GNFâ”GNF css/
â”‚   â”‚   â”œâ”GNFâ”GNF bootstrap.min.css
â”‚   â”‚   â””â”GNFâ”GNF custom.css
â”‚   â”œâ”GNFâ”GNF js/
â”‚   â”‚   â”œâ”GNFâ”GNF bootstrap.min.js
â”‚   â”‚   â””â”GNFâ”GNF custom.js
â”‚   â””â”GNFâ”GNF images/
â”œâ”GNFâ”GNF media/
â”‚   â”œâ”GNFâ”GNF cvs/
â”‚   â”œâ”GNFâ”GNF documents/
â”‚   â””â”GNFâ”GNF profile_pictures/
â””â”GNFâ”GNF utils/
    â”œâ”GNFâ”GNF __init__.py
    â”œâ”GNFâ”GNF decorators.py
    â”œâ”GNFâ”GNF helpers.py
    â””â”GNFâ”GNF export.py
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

### Base de donnÃ©es PostgreSQL (Production)
```
DATABASE_URL=postgresql://username:password@localhost:5432/recruitment_db
```

## Utilisation

### AccÃ¨s Admin
- URL: `/admin/`
- CrÃ©er un superutilisatGNF avec `python manage.py createsuperuser`

### Candidats
1. S'inscrire sur `/accounts/register/`
2. ComplÃ©ter le profil
3. Postuler aux offres disponibles

### AdministratGNFs
1. Se connecter via `/admin/` ou `/dashboard/`
2. GÃ©rer les offres d'emploi
3. Consulter les candidatures
4. Exporter les donnÃ©es

## API Endpoints

### Authentification
- `POST /accounts/register/` - Inscription
- `POST /accounts/login/` - Connexion
- `POST /accounts/logout/` - DÃ©connexion

### Profils
- `GET /accounts/profile/` - Voir profil
- `PUT /accounts/profile/edit/` - Modifier profil

### Offres d'emploi
- `GET /jobs/` - Liste des offres
- `GET /jobs/<id>/` - DÃ©tail d'une offre
- `POST /jobs/create/` - CrÃ©er offre (admin)

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

# Tests spÃ©cifiques
python manage.py test apps.accounts
python manage.py test apps.jobs
```

## DÃ©ploiement

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
2. CrÃ©er une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit (`git commit -am 'Ajouter nouvelle fonctionnalitÃ©'`)
4. Push (`git push origin feature/nouvelle-fonctionnalite`)
5. CrÃ©er une Pull Request

## Support

Pour toute question ou problÃ¨me :
- CrÃ©er une issue sur GitHub
- Email: support@recruitment-platform.com

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de dÃ©tails.

## Changelog

### Version 1.0.0
- SystÃ¨me d'authentification complet
- Gestion des profils candidats
- SystÃ¨me de candidatures
- Dashboard administratGNF
- Export Excel
- SystÃ¨me de notation et commentaires
