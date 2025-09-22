from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse


def admin_required(view_func):
    """DécoratGNF pour restreindre l'accès aux admins et HR"""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type not in ['admin', 'hr']:
            messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def candidate_required(view_func):
    """DécoratGNF pour restreindre l'accès aux candidats"""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type != 'candidate':
            messages.error(request, "Cette page est réservée aux candidats.")
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def ajax_required(view_func):
    """DécoratGNF pour les vues AJAX uniquement"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Cette requête doit être AJAX'}, status=400)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def profile_complete_required(view_func):
    """DécoratGNF pour s'assurer que le profil candidat est complet"""
    @wraps(view_func)
    @candidate_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            profile = request.user.candidate_profile
            if profile.profile_completion < 50:  # Minimum 50% de completion
                messages.warning(request, "Veuillez compléter votre profil avant de continuer.")
                return redirect('accounts:edit_profile')
        except:
            messages.error(request, "Profil candidat non trouvé.")
            return redirect('accounts:edit_profile')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def ratelimit(max_requests=10, period=60):
    """DécoratGNF simple de limitation de taux"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Implémentation basique - en production, utiliser django-ratelimit
            # ou Redis pour une solution plus robuste
            from django.core.cache import cache
            
            key = f"ratelimit:{request.META.get('REMOTE_ADDR')}:{view_func.__name__}"
            current_requests = cache.get(key, 0)
            
            if current_requests >= max_requests:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Trop de requêtes'}, status=429)
                messages.error(request, "Trop de requêtes. Veuillez patienter.")
                return redirect('core:home')
            
            cache.set(key, current_requests + 1, period)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
