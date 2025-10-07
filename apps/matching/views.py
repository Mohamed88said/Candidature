from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from apps.accounts.models import CandidateProfile
from apps.jobs.models import Job
from apps.matching.models import JobMatch, MatchingAlgorithm, CandidatePreference
from apps.matching.services import IntelligentMatchingService, MatchingAnalytics
from apps.matching.forms import CandidatePreferenceForm


@login_required
def matching_dashboard(request):
    """Dashboard principal du système de matching"""
    try:
        candidate_profile = request.user.candidate_profile
        
        # Récupérer les matches récents
        recent_matches = JobMatch.objects.filter(
            candidate=candidate_profile
        ).order_by('-created_at')[:10]
        
        # Statistiques personnelles
        total_matches = JobMatch.objects.filter(candidate=candidate_profile).count()
        high_matches = JobMatch.objects.filter(
            candidate=candidate_profile,
            overall_score__gte=80
        ).count()
        viewed_matches = JobMatch.objects.filter(
            candidate=candidate_profile,
            is_viewed_by_candidate=True
        ).count()
        
        # Matches recommandés (non vus)
        recommended_matches = JobMatch.objects.filter(
            candidate=candidate_profile,
            is_viewed_by_candidate=False,
            overall_score__gte=70
        ).order_by('-overall_score')[:5]
        
        context = {
            'recent_matches': recent_matches,
            'recommended_matches': recommended_matches,
            'total_matches': total_matches,
            'high_matches': high_matches,
            'viewed_matches': viewed_matches,
            'match_rate': round((viewed_matches / total_matches * 100) if total_matches > 0 else 0, 1)
        }
        
        return render(request, 'matching/dashboard.html', context)
        
    except CandidateProfile.DoesNotExist:
        messages.error(request, "Profil candidat non trouvé. Veuillez compléter votre profil.")
        return redirect('accounts:profile_edit')


@login_required
def job_matches(request):
    """Liste des matches d'emploi pour le candidat"""
    try:
        candidate_profile = request.user.candidate_profile
        
        # Filtres
        search_query = request.GET.get('search', '')
        min_score = request.GET.get('min_score', '')
        match_level = request.GET.get('match_level', '')
        
        # Base queryset
        matches = JobMatch.objects.filter(candidate=candidate_profile)
        
        # Appliquer les filtres
        if search_query:
            matches = matches.filter(
                Q(job__title__icontains=search_query) |
                Q(job__company__icontains=search_query) |
                Q(job__location__icontains=search_query)
            )
        
        if min_score:
            try:
                min_score_int = int(min_score)
                matches = matches.filter(overall_score__gte=min_score_int)
            except ValueError:
                pass
        
        if match_level:
            if match_level == 'excellent':
                matches = matches.filter(overall_score__gte=90)
            elif match_level == 'very_good':
                matches = matches.filter(overall_score__gte=80, overall_score__lt=90)
            elif match_level == 'good':
                matches = matches.filter(overall_score__gte=70, overall_score__lt=80)
            elif match_level == 'correct':
                matches = matches.filter(overall_score__gte=60, overall_score__lt=70)
        
        # Pagination
        paginator = Paginator(matches.order_by('-overall_score', '-created_at'), 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'search_query': search_query,
            'min_score': min_score,
            'match_level': match_level,
            'total_matches': matches.count()
        }
        
        return render(request, 'matching/job_matches.html', context)
        
    except CandidateProfile.DoesNotExist:
        messages.error(request, "Profil candidat non trouvé.")
        return redirect('accounts:profile_edit')


@login_required
def match_detail(request, match_id):
    """Détail d'un match d'emploi"""
    try:
        candidate_profile = request.user.candidate_profile
        match = get_object_or_404(JobMatch, id=match_id, candidate=candidate_profile)
        
        # Marquer comme vu
        if not match.is_viewed_by_candidate:
            match.is_viewed_by_candidate = True
            match.save(update_fields=['is_viewed_by_candidate'])
        
        # Récupérer des matches similaires
        similar_matches = JobMatch.objects.filter(
            candidate=candidate_profile,
            job__category=match.job.category,
            overall_score__gte=match.overall_score - 10,
            overall_score__lte=match.overall_score + 10
        ).exclude(id=match.id)[:3]
        
        context = {
            'match': match,
            'similar_matches': similar_matches,
        }
        
        return render(request, 'matching/match_detail.html', context)
        
    except CandidateProfile.DoesNotExist:
        messages.error(request, "Profil candidat non trouvé.")
        return redirect('accounts:profile_edit')


@login_required
@require_http_methods(["POST"])
def update_match_interest(request, match_id):
    """Met à jour l'intérêt du candidat pour un match"""
    try:
        candidate_profile = request.user.candidate_profile
        match = get_object_or_404(JobMatch, id=match_id, candidate=candidate_profile)
        
        interest = request.POST.get('interest')
        if interest in ['not_interested', 'interested', 'very_interested', 'applied']:
            match.candidate_interest = interest
            match.save(update_fields=['candidate_interest'])
            
            # Si le candidat a postulé, rediriger vers la page de candidature
            if interest == 'applied':
                return redirect('applications:apply', job_id=match.job.id)
            
            messages.success(request, "Votre intérêt a été mis à jour.")
        else:
            messages.error(request, "Valeur d'intérêt invalide.")
        
        return redirect('matching:match_detail', match_id=match_id)
        
    except CandidateProfile.DoesNotExist:
        messages.error(request, "Profil candidat non trouvé.")
        return redirect('accounts:profile_edit')


@login_required
def matching_preferences(request):
    """Gestion des préférences de matching"""
    try:
        candidate_profile = request.user.candidate_profile
        
        try:
            preferences = candidate_profile.matching_preferences
        except CandidatePreference.DoesNotExist:
            preferences = CandidatePreference.objects.create(candidate=candidate_profile)
        
        if request.method == 'POST':
            form = CandidatePreferenceForm(request.POST, instance=preferences)
            if form.is_valid():
                form.save()
                messages.success(request, "Vos préférences de matching ont été mises à jour.")
                
                # Relancer le matching avec les nouvelles préférences
                matching_service = IntelligentMatchingService()
                new_matches = matching_service.find_matches_for_candidate(candidate_profile, limit=10)
                
                if new_matches:
                    messages.info(request, f"{len(new_matches)} nouveaux matches trouvés !")
                
                return redirect('matching:preferences')
        else:
            form = CandidatePreferenceForm(instance=preferences)
        
        context = {
            'form': form,
            'preferences': preferences,
        }
        
        return render(request, 'matching/preferences.html', context)
        
    except CandidateProfile.DoesNotExist:
        messages.error(request, "Profil candidat non trouvé.")
        return redirect('accounts:profile_edit')


@login_required
def generate_new_matches(request):
    """Génère de nouveaux matches pour le candidat"""
    try:
        candidate_profile = request.user.candidate_profile
        
        # Générer de nouveaux matches
        matching_service = IntelligentMatchingService()
        new_matches = matching_service.find_matches_for_candidate(candidate_profile, limit=20)
        
        if new_matches:
            messages.success(request, f"{len(new_matches)} nouveaux matches générés !")
        else:
            messages.info(request, "Aucun nouveau match trouvé pour le moment.")
        
        return redirect('matching:dashboard')
        
    except CandidateProfile.DoesNotExist:
        messages.error(request, "Profil candidat non trouvé.")
        return redirect('accounts:profile_edit')


@login_required
def matching_analytics(request):
    """Analytics du système de matching (pour les admins)"""
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    try:
        # Statistiques générales
        stats = MatchingAnalytics.get_matching_statistics()
        
        # Top compétences
        top_skills = MatchingAnalytics.get_top_matching_skills()
        
        # Tendance
        trends = MatchingAnalytics.get_matching_trends()
        
        # Matches récents
        recent_matches = JobMatch.objects.select_related(
            'candidate__user', 'job'
        ).order_by('-created_at')[:20]
        
        context = {
            'stats': stats,
            'top_skills': top_skills,
            'trends': trends,
            'recent_matches': recent_matches,
        }
        
        return render(request, 'matching/analytics.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des analytics: {e}")
        return redirect('dashboard:admin_dashboard')


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def ajax_match_interest(request, match_id):
    """API AJAX pour mettre à jour l'intérêt d'un match"""
    try:
        candidate_profile = request.user.candidate_profile
        match = get_object_or_404(JobMatch, id=match_id, candidate=candidate_profile)
        
        data = json.loads(request.body)
        interest = data.get('interest')
        
        if interest in ['not_interested', 'interested', 'very_interested', 'applied']:
            match.candidate_interest = interest
            match.save(update_fields=['candidate_interest'])
            
            return JsonResponse({
                'success': True,
                'message': 'Intérêt mis à jour avec succès',
                'interest': interest
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Valeur d\'intérêt invalide'
            }, status=400)
        
    except CandidateProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Profil candidat non trouvé'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=500)


@login_required
def recruiter_matches(request, job_id):
    """Matches pour une offre spécifique (vue recruteur)"""
    if not request.user.is_staff and not request.user.user_type == 'hr':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    try:
        job = get_object_or_404(Job, id=job_id)
        
        # Récupérer les matches pour cette offre
        matches = JobMatch.objects.filter(job=job).order_by('-overall_score')
        
        # Filtres
        min_score = request.GET.get('min_score', '')
        if min_score:
            try:
                min_score_int = int(min_score)
                matches = matches.filter(overall_score__gte=min_score_int)
            except ValueError:
                pass
        
        # Pagination
        paginator = Paginator(matches, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'job': job,
            'page_obj': page_obj,
            'min_score': min_score,
            'total_matches': matches.count()
        }
        
        return render(request, 'matching/recruiter_matches.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur: {e}")
        return redirect('jobs:job_detail', job_id=job_id)

