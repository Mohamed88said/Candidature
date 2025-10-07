from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, F
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import render_to_string
from django.conf import settings
import json
import math
from datetime import datetime, timedelta

from .models import (
    Location, JobLocation, MapView, MapBookmark, MapAnalytics, 
    MapHeatmap, MapCluster, MapSearch
)
from .forms import (
    LocationForm, JobLocationForm, MapViewForm, MapBookmarkForm,
    MapSearchForm, MapFilterForm, MapSettingsForm
)
from apps.jobs.models import Job
from apps.accounts.models import CandidateProfile


def maps_dashboard(request):
    """Dashboard principal de la carte interactive"""
    try:
        # Statistiques générales
        total_locations = Location.objects.count()
        total_jobs = Job.objects.filter(status='active').count()
        total_job_locations = JobLocation.objects.count()
        
        # Localisations les plus populaires
        popular_locations = Location.objects.annotate(
            job_count=Count('job_locations')
        ).order_by('-job_count')[:10]
        
        # Statistiques par type de localisation
        remote_jobs = JobLocation.objects.filter(location_type='remote').count()
        hybrid_jobs = JobLocation.objects.filter(location_type='hybrid').count()
        on_site_jobs = JobLocation.objects.filter(location_type='primary').count()
        
        # Statistiques géographiques
        cities_with_jobs = Location.objects.annotate(
            job_count=Count('job_locations')
        ).filter(job_count__gt=0).values('city').annotate(
            total_jobs=Count('job_locations')
        ).order_by('-total_jobs')[:10]
        
        # Vues récentes de l'utilisateur
        recent_views = []
        if request.user.is_authenticated:
            recent_views = MapView.objects.filter(user=request.user).order_by('-updated_at')[:5]
        
        context = {
            'total_locations': total_locations,
            'total_jobs': total_jobs,
            'total_job_locations': total_job_locations,
            'popular_locations': popular_locations,
            'remote_jobs': remote_jobs,
            'hybrid_jobs': hybrid_jobs,
            'on_site_jobs': on_site_jobs,
            'cities_with_jobs': cities_with_jobs,
            'recent_views': recent_views,
        }
        
        return render(request, 'maps/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du dashboard: {e}")
        return redirect('home')


def interactive_map(request):
    """Vue principale de la carte interactive"""
    try:
        # Récupérer les localisations avec des offres
        job_locations = JobLocation.objects.select_related(
            'job', 'location'
        ).filter(
            job__status='active'
        ).order_by('-job__created_at')
        
        # Appliquer les filtres si présents
        search_form = MapSearchForm(request.GET)
        filter_form = MapFilterForm(request.GET)
        
        if search_form.is_valid():
            query = search_form.cleaned_data.get('query')
            location_query = search_form.cleaned_data.get('location_query')
            radius = search_form.cleaned_data.get('radius', 50)
            
            if query:
                job_locations = job_locations.filter(
                    Q(job__title__icontains=query) |
                    Q(job__company__icontains=query) |
                    Q(job__description__icontains=query)
                )
            
            if location_query:
                job_locations = job_locations.filter(
                    Q(location__city__icontains=location_query) |
                    Q(location__region__icontains=location_query) |
                    Q(location__country__icontains=location_query)
                )
        
        # Préparer les données pour la carte
        map_data = []
        for job_location in job_locations[:1000]:  # Limiter pour les performances
            map_data.append({
                'id': job_location.id,
                'job_id': job_location.job.id,
                'job_title': job_location.job.title,
                'company': job_location.job.company,
                'location_name': job_location.location.name,
                'city': job_location.location.city,
                'address': job_location.location.address,
                'latitude': float(job_location.location.latitude),
                'longitude': float(job_location.location.longitude),
                'location_type': job_location.location_type,
                'is_remote': job_location.location.is_remote,
                'is_hybrid': job_location.location.is_hybrid,
                'job_type': job_location.job.job_type,
                'experience_level': job_location.job.experience_level,
                'salary_min': job_location.job.salary_min,
                'salary_max': job_location.job.salary_max,
                'created_at': job_location.job.created_at.isoformat(),
                'url': job_location.job.get_absolute_url(),
            })
        
        # Paramètres de la carte
        map_settings = {
            'center_lat': 46.603354,  # Centre de la France
            'center_lng': 1.888334,
            'zoom': 6,
            'style': 'roadmap',
            'enable_clustering': True,
            'enable_heatmap': False,
        }
        
        # Récupérer les signets de l'utilisateur
        bookmarks = []
        if request.user.is_authenticated:
            bookmarks = MapBookmark.objects.filter(user=request.user).order_by('-updated_at')
        
        context = {
            'map_data': json.dumps(map_data, cls=DjangoJSONEncoder),
            'map_settings': json.dumps(map_settings),
            'search_form': search_form,
            'filter_form': filter_form,
            'bookmarks': bookmarks,
            'total_jobs': len(map_data),
        }
        
        return render(request, 'maps/interactive_map.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement de la carte: {e}")
        return redirect('maps:dashboard')


@login_required
def save_map_view(request):
    """Sauvegarder la vue actuelle de la carte"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Créer ou mettre à jour la vue
            map_view, created = MapView.objects.update_or_create(
                user=request.user,
                defaults={
                    'center_latitude': data.get('center_lat'),
                    'center_longitude': data.get('center_lng'),
                    'zoom_level': data.get('zoom'),
                    'filters': data.get('filters', {})
                }
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Vue sauvegardée avec succès'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)


@login_required
def create_bookmark(request):
    """Créer un signet de carte"""
    if request.method == 'POST':
        try:
            form = MapBookmarkForm(request.POST)
            if form.is_valid():
                bookmark = form.save(commit=False)
                bookmark.user = request.user
                bookmark.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Signet créé avec succès',
                    'bookmark_id': bookmark.id
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)


@login_required
def delete_bookmark(request, bookmark_id):
    """Supprimer un signet"""
    try:
        bookmark = get_object_or_404(MapBookmark, id=bookmark_id, user=request.user)
        bookmark.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Signet supprimé avec succès'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def search_locations(request):
    """Rechercher des localisations"""
    try:
        query = request.GET.get('q', '')
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        locations = Location.objects.filter(
            Q(name__icontains=query) |
            Q(city__icontains=query) |
            Q(region__icontains=query) |
            Q(country__icontains=query)
        ).annotate(
            job_count=Count('job_locations')
        ).order_by('-job_count')[:10]
        
        results = []
        for location in locations:
            results.append({
                'id': location.id,
                'name': location.name,
                'city': location.city,
                'region': location.region,
                'country': location.country,
                'latitude': float(location.latitude),
                'longitude': float(location.longitude),
                'job_count': location.job_count,
                'full_address': location.get_full_address()
            })
        
        return JsonResponse({'results': results})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_jobs_in_radius(request):
    """Récupérer les offres dans un rayon donné"""
    try:
        lat = float(request.GET.get('lat', 0))
        lng = float(request.GET.get('lng', 0))
        radius = float(request.GET.get('radius', 50))
        
        if not lat or not lng:
            return JsonResponse({'error': 'Coordonnées manquantes'}, status=400)
        
        # Calculer les bornes du rectangle
        lat_delta = radius / 111.0  # Approximation: 1 degré ≈ 111 km
        lng_delta = radius / (111.0 * math.cos(math.radians(lat)))
        
        min_lat = lat - lat_delta
        max_lat = lat + lat_delta
        min_lng = lng - lng_delta
        max_lng = lng + lng_delta
        
        # Récupérer les offres dans le rectangle
        job_locations = JobLocation.objects.filter(
            location__latitude__range=(min_lat, max_lat),
            location__longitude__range=(min_lng, max_lng),
            job__status='active'
        ).select_related('job', 'location')
        
        # Filtrer par distance exacte (optionnel, plus précis mais plus lent)
        results = []
        for job_location in job_locations:
            distance = calculate_distance(
                lat, lng,
                float(job_location.location.latitude),
                float(job_location.location.longitude)
            )
            
            if distance <= radius:
                results.append({
                    'id': job_location.id,
                    'job_id': job_location.job.id,
                    'title': job_location.job.title,
                    'company': job_location.job.company,
                    'location': job_location.location.name,
                    'city': job_location.location.city,
                    'latitude': float(job_location.location.latitude),
                    'longitude': float(job_location.location.longitude),
                    'distance': round(distance, 2),
                    'job_type': job_location.job.job_type,
                    'experience_level': job_location.job.experience_level,
                    'salary_min': job_location.job.salary_min,
                    'salary_max': job_location.job.salary_max,
                    'url': job_location.job.get_absolute_url(),
                })
        
        return JsonResponse({'results': results})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculer la distance entre deux points en km (formule de Haversine)"""
    R = 6371  # Rayon de la Terre en km
    
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    
    a = (math.sin(dlat/2) * math.sin(dlat/2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng/2) * math.sin(dlng/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance


@login_required
def map_analytics(request):
    """Analytics de la carte (admin)"""
    if not request.user.is_staff:
        messages.error(request, 'Accès non autorisé.')
        return redirect('maps:dashboard')
    
    try:
        # Statistiques générales
        total_views = MapView.objects.count()
        total_searches = MapSearch.objects.count()
        total_bookmarks = MapBookmark.objects.count()
        
        # Statistiques par jour (30 derniers jours)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_stats = MapView.objects.filter(
            created_at__gte=thirty_days_ago
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            views=Count('id')
        ).order_by('day')
        
        # Localisations les plus recherchées
        popular_locations = Location.objects.annotate(
            search_count=Count('job_locations__job__applications')
        ).order_by('-search_count')[:10]
        
        # Types de localisation les plus populaires
        location_types = JobLocation.objects.values('location_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        context = {
            'total_views': total_views,
            'total_searches': total_searches,
            'total_bookmarks': total_bookmarks,
            'daily_stats': list(daily_stats),
            'popular_locations': popular_locations,
            'location_types': list(location_types),
        }
        
        return render(request, 'maps/analytics.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des analytics: {e}")
        return redirect('maps:dashboard')


@login_required
def my_bookmarks(request):
    """Vue des signets de l'utilisateur"""
    try:
        bookmarks = MapBookmark.objects.filter(user=request.user).order_by('-updated_at')
        
        # Pagination
        paginator = Paginator(bookmarks, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
        }
        
        return render(request, 'maps/my_bookmarks.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des signets: {e}")
        return redirect('maps:dashboard')


@login_required
def bookmark_detail(request, bookmark_id):
    """Détail d'un signet"""
    try:
        bookmark = get_object_or_404(MapBookmark, id=bookmark_id, user=request.user)
        
        # Récupérer les offres dans la zone du signet
        radius = 50  # km
        lat = float(bookmark.center_latitude)
        lng = float(bookmark.center_longitude)
        
        # Calculer les bornes
        lat_delta = radius / 111.0
        lng_delta = radius / (111.0 * math.cos(math.radians(lat)))
        
        min_lat = lat - lat_delta
        max_lat = lat + lat_delta
        min_lng = lng - lng_delta
        max_lng = lng + lng_delta
        
        job_locations = JobLocation.objects.filter(
            location__latitude__range=(min_lat, max_lat),
            location__longitude__range=(min_lng, max_lng),
            job__status='active'
        ).select_related('job', 'location')
        
        context = {
            'bookmark': bookmark,
            'job_locations': job_locations,
            'map_data': json.dumps([{
                'id': jl.id,
                'job_id': jl.job.id,
                'title': jl.job.title,
                'company': jl.job.company,
                'latitude': float(jl.location.latitude),
                'longitude': float(jl.location.longitude),
                'url': jl.job.get_absolute_url(),
            } for jl in job_locations], cls=DjangoJSONEncoder),
        }
        
        return render(request, 'maps/bookmark_detail.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du signet: {e}")
        return redirect('maps:my_bookmarks')