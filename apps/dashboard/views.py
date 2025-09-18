from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
import json
from django.shortcuts import get_object_or_404

# Import des modèles
from apps.accounts.models import User, CandidateProfile
from apps.jobs.models import Job, JobCategory
from apps.applications.models import Application, Interview
from .models import SystemNotification, UserNotificationRead
from .utils import generate_excel_report, get_dashboard_stats


@login_required
def admin_dashboard(request):
    """Dashboard principal pour admin/hr"""
    if request.user.user_type not in ['admin', 'hr']:
        messages.error(request, "Accès non autorisé.")
        return redirect('core:home')
    
    # Statistiques générales
    stats = get_dashboard_stats()
    
    # Activité récente
    recent_applications = Application.objects.select_related(
        'candidate__user', 'job'
    ).order_by('-applied_at')[:10]
    
    recent_interviews = Interview.objects.select_related(
        'application__candidate__user', 'application__job'
    ).filter(scheduled_date__gte=timezone.now()).order_by('scheduled_date')[:5]
    
    # Graphiques de données (derniers 30 jours)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Applications par jour
    applications_by_day = []
    for i in range(30):
        date = (timezone.now() - timedelta(days=i)).date()
        count = Application.objects.filter(applied_at__date=date).count()
        applications_by_day.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    applications_by_day.reverse()
    
    # Applications par statut
    applications_by_status = []
    for status_code, status_name in Application.STATUS_CHOICES:
        count = Application.objects.filter(status=status_code).count()
        applications_by_status.append({
            'status': status_name,
            'count': count
        })
    
    # Top 5 des offres les plus populaires
    top_jobs = Job.objects.filter(
        status='published'
    ).annotate(
        app_count=Count('applications')
    ).order_by('-app_count')[:5]
    
    # Notifications non lues
    notifications = SystemNotification.objects.filter(
        Q(is_global=True) | Q(target_users=request.user),
        is_active=True
    ).exclude(
        usernotificationread__user=request.user
    ).order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_applications': recent_applications,
        'recent_interviews': recent_interviews,
        'applications_by_day': json.dumps(applications_by_day),
        'applications_by_status': json.dumps(applications_by_status),
        'top_jobs': top_jobs,
        'notifications': notifications,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def statistics(request):
    """Page de statistiques détaillées"""
    if request.user.user_type not in ['admin', 'hr']:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    # Période sélectionnée
    period = request.GET.get('period', '30')  # 7, 30, 90, 365 jours
    try:
        days = int(period)
    except ValueError:
        days = 30
    
    start_date = timezone.now() - timedelta(days=days)
    
    # Statistiques de base
    stats = {
        'total_applications': Application.objects.filter(applied_at__gte=start_date).count(),
        'total_candidates': CandidateProfile.objects.filter(created_at__gte=start_date).count(),
        'total_jobs': Job.objects.filter(created_at__gte=start_date).count(),
        'total_interviews': Interview.objects.filter(created_at__gte=start_date).count(),
    }
    
    # Taux de conversion
    total_apps = Application.objects.count()
    if total_apps > 0:
        conversion_rates = {
            'shortlisted': (Application.objects.filter(status='shortlisted').count() / total_apps) * 100,
            'interviewed': (Application.objects.filter(status__in=['interview_scheduled', 'interview_completed']).count() / total_apps) * 100,
            'hired': (Application.objects.filter(status='accepted').count() / total_apps) * 100,
        }
    else:
        conversion_rates = {'shortlisted': 0, 'interviewed': 0, 'hired': 0}
    
    # Applications par mois (12 derniers mois)
    monthly_data = []
    for i in range(12):
        date = timezone.now() - timedelta(days=30*i)
        month_start = date.replace(day=1)
        if i == 0:
            month_end = timezone.now()
        else:
            month_end = (date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        count = Application.objects.filter(
            applied_at__gte=month_start,
            applied_at__lte=month_end
        ).count()
        
        monthly_data.append({
            'month': date.strftime('%Y-%m'),
            'count': count
        })
    monthly_data.reverse()
    
    # Top catégories
    top_categories = JobCategory.objects.annotate(
        job_count=Count('jobs', filter=Q(jobs__status='published')),
        app_count=Count('jobs__applications')
    ).order_by('-app_count')[:10]
    
    # Statistiques par source (si implémenté)
    # source_stats = Application.objects.values('source').annotate(count=Count('id')).order_by('-count')
    
    context = {
        'stats': stats,
        'conversion_rates': conversion_rates,
        'monthly_data': json.dumps(monthly_data),
        'top_categories': top_categories,
        'selected_period': period,
        'period_choices': [
            ('7', '7 derniers jours'),
            ('30', '30 derniers jours'),
            ('90', '3 derniers mois'),
            ('365', 'Dernière année'),
        ]
    }
    
    return render(request, 'dashboard/statistics.html', context)


@login_required
def candidates_management(request):
    """Gestion des candidats"""
    if request.user.user_type not in ['admin', 'hr']:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    candidates = CandidateProfile.objects.select_related('user').all()
    
    # Filtres
    search = request.GET.get('search')
    if search:
        candidates = candidates.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(current_position__icontains=search) |
            Q(current_company__icontains=search)
        )
    
    experience_filter = request.GET.get('experience')
    if experience_filter:
        try:
            min_exp = int(experience_filter)
            candidates = candidates.filter(years_of_experience__gte=min_exp)
        except ValueError:
            pass
    
    location_filter = request.GET.get('location')
    if location_filter:
        candidates = candidates.filter(city__icontains=location_filter)
    
    # Tri
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['-created_at', 'user__last_name', 'years_of_experience', 'profile_completion']:
        candidates = candidates.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(candidates, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    candidate_stats = {
        'total': candidates.count(),
        'active': candidates.filter(is_active=True).count(),
        'with_cv': candidates.exclude(cv_file='').count(),
        'high_completion': candidates.filter(profile_completion__gte=80).count(),
    }
    
    context = {
        'page_obj': page_obj,
        'candidate_stats': candidate_stats,
        'search': search,
        'experience_filter': experience_filter,
        'location_filter': location_filter,
        'current_sort': sort_by,
    }
    
    return render(request, 'dashboard/candidates.html', context)


@login_required
def export_data(request):
    """Export des données en Excel"""
    if request.user.user_type not in ['admin', 'hr']:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    export_type = request.GET.get('type', 'applications')
    
    try:
        if export_type == 'applications':
            response = generate_excel_report('applications')
            filename = f'candidatures_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        elif export_type == 'candidates':
            response = generate_excel_report('candidates')
            filename = f'candidats_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        elif export_type == 'jobs':
            response = generate_excel_report('jobs')
            filename = f'offres_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        else:
            messages.error(request, "Type d'export non valide.")
            return redirect('dashboard:admin_dashboard')
        
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except Exception as e:
        messages.error(request, f"Erreur lors de l'export: {str(e)}")
        return redirect('dashboard:admin_dashboard')


@login_required
def reports(request):
    """Page de rapports"""
    if request.user.user_type not in ['admin', 'hr']:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    # Rapport de performance des recruteurs
    recruiters = User.objects.filter(user_type__in=['admin', 'hr']).annotate(
        jobs_created=Count('created_jobs'),
        applications_reviewed=Count('reviewed_applications'),
        interviews_conducted=Count('conducted_interviews')
    )
    
    # Rapport de performance des offres
    job_performance = Job.objects.filter(status='published').annotate(
        applications_count=Count('applications'),
        avg_rating=Avg('applications__ratings__score')
    ).order_by('-applications_count')[:10]
    
    # Temps moyen de traitement
    avg_processing_time = Application.objects.filter(
        status__in=['accepted', 'rejected']
    ).extra(
        select={'processing_days': 'DATEDIFF(updated_at, applied_at)'}
    ).aggregate(
        avg_days=Avg('processing_days')
    )['avg_days'] or 0
    
    context = {
        'recruiters': recruiters,
        'job_performance': job_performance,
        'avg_processing_time': round(avg_processing_time, 1),
    }
    
    return render(request, 'dashboard/reports.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Marquer une notification comme lue"""
    try:
        notification = SystemNotification.objects.get(id=notification_id)
        UserNotificationRead.objects.get_or_create(
            user=request.user,
            notification=notification
        )
        return JsonResponse({'success': True})
    except SystemNotification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification non trouvée'})


@login_required
def ajax_dashboard_stats(request):
    """API AJAX pour les statistiques du dashboard"""
    if request.user.user_type not in ['admin', 'hr']:
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    stats = get_dashboard_stats()
    return JsonResponse(stats)


@login_required
def candidate_profile_view(request, candidate_id):
    """Vue détaillée d'un profil candidat"""
    if request.user.user_type not in ['admin', 'hr']:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    candidate = get_object_or_404(CandidateProfile, id=candidate_id)
    
    # Applications du candidat
    applications = candidate.applications.select_related('job').order_by('-applied_at')
    
    # Statistiques du candidat
    candidate_stats = {
        'total_applications': applications.count(),
        'pending_applications': applications.filter(status='pending').count(),
        'interviews': applications.filter(status__in=['interview_scheduled', 'interview_completed']).count(),
        'offers': applications.filter(status='offer_made').count(),
    }
    
    context = {
        'candidate': candidate,
        'applications': applications,
        'candidate_stats': candidate_stats,
    }
    
    return render(request, 'dashboard/candidate_profile.html', context)