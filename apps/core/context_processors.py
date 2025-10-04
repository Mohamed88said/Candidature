from django.conf import settings
from django.utils.translation import gettext_lazy as _

def site_settings(request):
    """Context processor pour les paramètres du site"""
    
    # Vérifier si Cloudinary est actif
    cloudinary_active = getattr(settings, 'CLOUDINARY_ACTIVE', False)
    
    # Paramètres par défaut du site
    default_settings = {
        'site_name': "Plateforme de Recrutement Expert",
        'site_description': "Plateforme complète de gestion de recrutement et de mise en relation talents-entreprises",
        'contact_email': "mohamedsaiddiallo88@gmail.com",
        'contact_phone': "+33 06 28 53 09 45",
        'address': "2 A rue du commandant l'Herminier, Rouen, France",
        'company_name': "SARL",
        'about_title': "À propos de SARL",
        'about_content': "SARL est une plateforme innovante de recrutement qui connecte les talents aux meilleures opportunités professionnelles.",
        'about_mission': "Notre mission est de simplifier et optimiser le processus de recrutement.",
        'about_vision': "Devenir la référence en matière de plateforme de recrutement en Europe.",
        'about_values': "Innovation, Transparence, Excellence, Collaboration, Diversité",
        'hero_title': "Trouvez votre emploi idéal",
        'hero_subtitle': "Découvrez des milliers d'opportunités d'emploi et connectez-vous avec les meilleures entreprises.",
        'footer_text': "© 2025 SARL. Tous droits réservés.",
        'email_signature': "L'équipe SARL \nmohamedsaiddiallo88@gmail.com\n+33 06 28 53 09 45",
    }
    
    # Essayer de récupérer les paramètres depuis la base de données
    try:
        # Import ici pour éviter les problèmes de dépendance circulaire
        from .models import SiteSettings, ThemeSettings
        
        site_settings_obj = SiteSettings.objects.first()
        if not site_settings_obj:
            # Créer des paramètres par défaut si aucun n'existe
            site_settings_obj = SiteSettings.objects.create(**default_settings)
        
        theme_settings_obj = None
        try:
            theme_settings_obj = ThemeSettings.objects.get(is_active=True)
        except ThemeSettings.DoesNotExist:
            theme_settings_obj = None
            
        return {
            'site_settings': site_settings_obj,
            'active_theme': theme_settings_obj,
            'CLOUDINARY_ACTIVE': cloudinary_active,
        }
        
    except Exception as e:
        # En cas d'erreur (migrations non appliquées, etc.), utiliser les paramètres par défaut
        return {
            'site_settings': type('DefaultSettings', (), default_settings)(),
            'active_theme': None,
            'CLOUDINARY_ACTIVE': cloudinary_active,
        }