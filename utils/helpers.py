import os
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.files.storage import default_storage
from PIL import Image
import logging

logger = logging.getLogger(__name__)


def send_notification_email(to_email, subject, template_name, context):
    """Envoie un email de notification"""
    try:
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Erreur envoi email à {to_email}: {str(e)}")
        return False


def generate_unique_filename(filename):
    """Génère un nom de fichier unique"""
    ext = filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return unique_filename


def resize_image(image_path, max_width=800, max_height=600):
    """Redimensionne une image"""
    try:
        with Image.open(image_path) as img:
            # Convertir en RGB si nécessaire
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Calculer les nouvelles dimensions
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Sauvegarder
            img.save(image_path, optimize=True, quality=85)
            return True
    except Exception as e:
        logger.error(f"Erreur redimensionnement image {image_path}: {str(e)}")
        return False


def validate_file_type(file, allowed_types):
    """Valide le type de fichier"""
    if not file:
        return True
    
    file_extension = file.name.split('.')[-1].lower()
    return file_extension in allowed_types


def calculate_file_size_mb(file):
    """Calcule la taille d'un fichier en MB"""
    if not file:
        return 0
    return round(file.size / (1024 * 1024), 2)


def clean_filename(filename):
    """Nettoie un nom de fichier"""
    import re
    # Supprimer les caractères spéciaux
    filename = re.sub(r'[^\w\s-.]', '', filename)
    # Remplacer les espaces par des underscores
    filename = re.sub(r'[-\s]+', '_', filename)
    return filename


def get_client_ip(request):
    """Récupère l'IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def format_phone_number(phone):
    """Formate un numéro de téléphone"""
    if not phone:
        return ""
    
    # Supprimer tous les caractères non numériques
    digits = ''.join(filter(str.isdigit, phone))
    
    # Formater selon la longueur
    if len(digits) == 10:
        return f"{digits[:2]} {digits[2:4]} {digits[4:6]} {digits[6:8]} {digits[8:]}"
    elif len(digits) == 9:
        return f"0{digits[0]} {digits[1:3]} {digits[3:5]} {digits[5:7]} {digits[7:]}"
    else:
        return phone


def truncate_text(text, max_length=100):
    """Tronque un texte"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def generate_slug(text):
    """Génère un slug à partir d'un texte"""
    from django.utils.text import slugify
    import uuid
    
    slug = slugify(text)
    if not slug:
        slug = str(uuid.uuid4())[:8]
    return slug


def get_file_icon(filename):
    """Retourne l'icône Font Awesome appropriée pour un type de fichier"""
    if not filename:
        return "fas fa-file"
    
    extension = filename.split('.')[-1].lower()
    
    icons = {
        'pdf': 'fas fa-file-pdf',
        'doc': 'fas fa-file-word',
        'docx': 'fas fa-file-word',
        'xls': 'fas fa-file-excel',
        'xlsx': 'fas fa-file-excel',
        'ppt': 'fas fa-file-powerpoint',
        'pptx': 'fas fa-file-powerpoint',
        'jpg': 'fas fa-file-image',
        'jpeg': 'fas fa-file-image',
        'png': 'fas fa-file-image',
        'gif': 'fas fa-file-image',
        'zip': 'fas fa-file-archive',
        'rar': 'fas fa-file-archive',
        'txt': 'fas fa-file-alt',
        'csv': 'fas fa-file-csv',
    }
    
    return icons.get(extension, 'fas fa-file')


def calculate_age(birth_date):
    """Calcule l'âge à partir d'une date de naissance"""
    if not birth_date:
        return None
    
    from datetime import date
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def format_currency(amount, currency='EUR'):
    """Formate un montant en devise"""
    if not amount:
        return ""
    
    symbols = {
        'EUR': '€',
        'USD': '$',
        'GBP': '£',
    }
    
    symbol = symbols.get(currency, currency)
    return f"{amount:,.0f} {symbol}".replace(',', ' ')


def get_time_since(datetime_obj):
    """Retourne le temps écoulé depuis une date"""
    from django.utils import timezone
    from datetime import timedelta
    
    if not datetime_obj:
        return ""
    
    now = timezone.now()
    diff = now - datetime_obj
    
    if diff.days > 365:
        years = diff.days // 365
        return f"il y a {years} an{'s' if years > 1 else ''}"
    elif diff.days > 30:
        months = diff.days // 30
        return f"il y a {months} mois"
    elif diff.days > 0:
        return f"il y a {diff.days} jour{'s' if diff.days > 1 else ''}"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"il y a {hours} heure{'s' if hours > 1 else ''}"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"il y a {minutes} minute{'s' if minutes > 1 else ''}"
    else:
        return "à l'instant"


def sanitize_html(html_content):
    """Nettoie le contenu HTML"""
    import bleach
    
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'
    ]
    
    allowed_attributes = {
        '*': ['class'],
    }
    
    return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attributes)


def log_user_activity(user, action, details=None):
    """Log l'activité utilisateur"""
    logger.info(f"User {user.id} ({user.email}) - {action}" + (f" - {details}" if details else ""))


def generate_password():
    """Génère un mot de passe aléatoire"""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    return password


def is_valid_email_domain(email):
    """Vérifie si le domaine email est valide"""
    import re
    
    # Liste des domaines temporaires/jetables à bloquer
    blocked_domains = [
        '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
        'mailinator.com', 'yopmail.com'
    ]
    
    domain = email.split('@')[-1].lower()
    return domain not in blocked_domains


def compress_image(image_path, quality=85):
    """Compresse une image"""
    try:
        with Image.open(image_path) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            img.save(image_path, optimize=True, quality=quality)
            return True
    except Exception as e:
        logger.error(f"Erreur compression image {image_path}: {str(e)}")
        return False