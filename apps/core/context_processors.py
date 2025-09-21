from .models import SiteSettings, ThemeSettings
from django.utils.translation import gettext_lazy as _


def site_settings(request):
    """Context processor pour les paramètres du site"""
    try:
        settings = SiteSettings.objects.first()
        # Si aucun paramètre n'existe, créer des paramètres par défaut
        if not settings:
            settings = SiteSettings.objects.create(
                site_name="Plateforme de Recrutement Expert",
                site_description="Plateforme complète de gestion de recrutement et de mise en relation talents-entreprises",
                contact_email="mohamedsaiddiallo88@gmail.com",
                contact_phone="+33 06 28 53 09 45",
                address="2 A rue du commandant l'Herminier, Rouen, France",
                company_name="SARL",
                about_title="À propos deSARL",
                about_content="SARL est une plateforme innovante de recrutement qui connecte les talents aux meilleures opportunités professionnelles.",
                about_mission="Notre mission est de simplifier et optimiser le processus de recrutement.",
                about_vision="Devenir la référence en matière de plateforme de recrutement en Europe.",
                about_values="Innovation, Transparence, Excellence, Collaboration, Diversité",
                hero_title="Trouvez votre emploi idéal",
                hero_subtitle="Découvrez des milliers d'opportunités d'emploi et connectez-vous avec les meilleures entreprises.",
                footer_text="© 2025 SARL. Tous droits réservés.",
                email_signature="L'équipe SARL \nmohamedsaiddiallo88@.com\n+33 06 28 53 09 45",
            )
    except Exception as e:
        # En cas d'erreur (migrations non appliquées), retourner un dictionnaire vide
        settings = None
    
    try:
        theme = ThemeSettings.objects.get(is_active=True)
    except ThemeSettings.DoesNotExist:
        theme = None
    
    return {
        'site_settings': settings,
        'active_theme': theme,
    }