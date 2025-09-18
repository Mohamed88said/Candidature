from .models import SiteSettings, ThemeSettings


def site_settings(request):
    """Context processor pour les paramètres du site"""
    try:
        settings = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        settings = None
    
    try:
        theme = ThemeSettings.objects.get(is_active=True)
    except ThemeSettings.DoesNotExist:
        theme = None
    
    return {
        'site_settings': settings,
        'active_theme': theme,
    }