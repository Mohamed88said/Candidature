"""
Django settings for recruitment_platform project.
"""

from pathlib import Path
from decouple import config, Csv
import os
import dj_database_url
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,.onrender.com', cast=Csv())

# =============================================================================
# CONFIGURATION KEEP-ALIVE ANTI-HIBERNATION
# =============================================================================

# URL de l'application pour le keep-alive interne
RENDER_EXTERNAL_URL = config('RENDER_EXTERNAL_URL', default='https://recruitment-platform-vnjb.onrender.com')

# Activation du keep-alive interne (désactiver en développement si besoin)
ENABLE_KEEP_ALIVE = config('ENABLE_KEEP_ALIVE', default=not DEBUG, cast=bool)

# Intervalle des pings en secondes (5 minutes = 300 secondes)
KEEP_ALIVE_INTERVAL = config('KEEP_ALIVE_INTERVAL', default=240, cast=int)  # 4 minutes

# =============================================================================
# FIN CONFIGURATION KEEP-ALIVE
# =============================================================================

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'django_filters',
    'corsheaders',
    'django_celery_beat',
    'cloudinary',
    'cloudinary_storage',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.jobs',
    'apps.applications',
    'apps.dashboard',
    'apps.core',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'recruitment_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'apps.core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'recruitment_platform.wsgi.application'

# Database - Configuration optimisée pour Render.com
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3'),
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}

# Configuration optimisée pour PostgreSQL sur Render
if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',
        'connect_timeout': 10,
    }
    DATABASES['default']['CONN_MAX_AGE'] = 300  # 5 minutes

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Créer les dossiers statics s'ils n'existent pas
os.makedirs(BASE_DIR / 'static' / 'css', exist_ok=True)
os.makedirs(BASE_DIR / 'static' / 'js', exist_ok=True)
os.makedirs(BASE_DIR / 'static' / 'images', exist_ok=True)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =============================================================================
# CONFIGURATION CLOUDINARY AVEC FALLBACK
# =============================================================================

# Cloudinary Configuration for Media Files
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}

# Vérification si Cloudinary est configuré
CLOUDINARY_ACTIVE = all([
    CLOUDINARY_STORAGE['CLOUD_NAME'],
    CLOUDINARY_STORAGE['API_KEY'], 
    CLOUDINARY_STORAGE['API_SECRET']
])

if CLOUDINARY_ACTIVE:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    # Configuration Cloudinary supplémentaire
    import cloudinary
    cloudinary.config(
        cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
        api_key=CLOUDINARY_STORAGE['API_KEY'],
        api_secret=CLOUDINARY_STORAGE['API_SECRET']
    )
else:
    # Fallback vers le stockage local si Cloudinary n'est pas configuré
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    print("⚠️ Cloudinary non configuré - utilisation du stockage local")

# Media URL configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
os.makedirs(MEDIA_ROOT, exist_ok=True)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Login/Logout URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='')

# Support Email et Site Name pour les templates
SUPPORT_EMAIL = config('SUPPORT_EMAIL', default='')
SITE_NAME = config('SITE_NAME', default='Plateforme de Recrutement')
SITE_URL = config('SITE_URL', default='http://localhost:8000')

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# Security Settings (Production)
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "https://*.onrender.com",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS = True

# Messages Framework
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# =============================================================================
# CELERY CONFIGURATION - SOLUTION OPTIMISÉE
# =============================================================================

# Configuration Celery intelligente
REDIS_URL = config('REDIS_URL', default='')

if REDIS_URL and not REDIS_URL.startswith(('redis://localhost', 'redis://127.0.0.1')):
    # Mode production avec Redis externe
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TASK_ALWAYS_EAGER = False
else:
    # Mode développement/synchrone
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# =============================================================================
# FIN CONFIGURATION CELERY
# =============================================================================

# Configuration de la langue française
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Configuration des formats de date français
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i'
SHORT_DATE_FORMAT = 'd/m/Y'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'

# Formules de politesse françaises pour les emails
EMAIL_SUBJECT_PREFIX = '[Plateforme Recrutement] '

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO' if DEBUG else 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Test configuration
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]

# =============================================================================
# DÉMARRAGE AUTOMATIQUE DU KEEP-ALIVE
# =============================================================================

# Démarrer le keep-alive automatiquement
if ENABLE_KEEP_ALIVE and not any('test' in arg for arg in sys.argv):
    try:
        from apps.core.keep_alive import start_keep_alive
        start_keep_alive()
        print("🔄 Système keep-alive activé")
    except Exception as e:
        print(f"⚠️ Impossible de démarrer le keep-alive: {e}")

# Debug information
if DEBUG:
    print("=" * 50)
    print("DEBUG MODE ACTIVATED")
    print(f"Database: {DATABASES['default']['ENGINE']}")
    print(f"Redis URL: {REDIS_URL}")
    print(f"Celery Mode: {'SYNCHRONE' if CELERY_TASK_ALWAYS_EAGER else 'ASYNCHRONE'}")
    print(f"Cloudinary: {'ACTIVE' if CLOUDINARY_ACTIVE else 'INACTIVE'}")
    print(f"Keep-alive: {'ACTIVE' if ENABLE_KEEP_ALIVE else 'INACTIVE'}")
    print("=" * 50)