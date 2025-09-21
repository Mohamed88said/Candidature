from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from .models import Job, JobCategory, SavedJob, JobAlert
from .forms import JobForm, JobSearchForm, JobAlertForm
from apps.applications.models import Application


def job_list(request):
    """Liste des offres d'emploi avec recherche et filtres"""
    form = JobSearchForm(request.GET)
    jobs = Job.objects.filter(status='published').select_related('category', 'created_by')
    
    # Filtres de recherche
    if form.is_valid():
        keywords = form.cleaned_data.get('keywords')
        location = form.cleaned_data.get('location')
        category = form.cleaned_data.get('category')
        job_type = form.cleaned_data.get('job_type')
        experience_level = form.cleaned_data.get('experience_level')
        remote_work = form.cleaned_data.get('remote_work')
        salary_min = form.cleaned_data.get('salary_min')
        
        if keywords:
            jobs = jobs.filter(
                Q(title__icontains=keywords) |
                Q(description__icontains=keywords) |
                Q(company__icontains=keywords)
            )
        
        if location:
            jobs = jobs.filter(location__icontains=location)
        
        if category:
            jobs = jobs.filter(category=category)
        
        if job_type:
            jobs = jobs.filter(job_type=job_type)
        
        if experience_level:
            jobs = jobs.filter(experience_level=experience_level)
        
        if remote_work:
            jobs = jobs.filter(remote_work=True)
        
        if salary_min:
            jobs = jobs.filter(
                Q(salary_min__gte=salary_min) | Q(salary_max__gte=salary_min)
            )
    
    # Tri
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['-created_at', 'title', '-salary_max', '-applications_count']:
        jobs = jobs.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(jobs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    total_jobs = jobs.count()
    categories = JobCategory.objects.filter(is_active=True).annotate(
        job_count=Count('jobs', filter=Q(jobs__status='published'))
    )
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'total_jobs': total_jobs,
        'categories': categories,
        'current_sort': sort_by,
    }
    
    return render(request, 'jobs/job_list.html', context)


def job_detail(request, slug):
    """Détail d'une offre d'emploi"""
    try:
        # Essayer de trouver le job par son slug
        job = get_object_or_404(Job, slug=slug, status='published')
    except Http404:
        # Si le job n'existe pas, vérifier s'il a été déplacé ou renommé
        try:
            # Chercher parmi tous les jobs publiés par ID potentiel dans le slug
            published_jobs = Job.objects.filter(status='published')
            
            # Essayer d'extraire un UUID du slug
            import re
            uuid_pattern = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
            match = re.search(uuid_pattern, slug)
            
            if match:
                uuid_part = match.group(0)
                # Chercher un job avec cet UUID dans son slug
                for j in published_jobs:
                    if uuid_part in j.slug:
                        return redirect('job_detail', slug=j.slug, permanent=True)
            
            # Si on arrive ici, le job n'existe vraiment pas
            raise Http404("Cette offre d'emploi n'existe pas ou a été supprimée.")
            
        except Exception:
            # En cas d'erreur, lever une 404 normale
            raise Http404("Cette offre d'emploi n'existe pas.")
    
    # Incrémenter le nombre de vues
    job.increment_views()
    
    # Vérifier si l'utilisateur a sauvegardé cette offre
    is_saved = False
    user_applied = False
    
    if request.user.is_authenticated:
        is_saved = SavedJob.objects.filter(user=request.user, job=job).exists()
        if hasattr(request.user, 'candidate_profile'):
            user_applied = Application.objects.filter(
                candidate=request.user.candidate_profile, 
                job=job
            ).exists()
    
    # Offres similaires
    similar_jobs = Job.objects.filter(
        category=job.category,
        status='published'
    ).exclude(id=job.id)[:4]
    
    context = {
        'job': job,
        'is_saved': is_saved,
        'user_applied': user_applied,
        'similar_jobs': similar_jobs,
        'required_skills': job.required_skills.all(),
    }
    
    return render(request, 'jobs/job_detail.html', context)


@login_required
def create_job(request):
    """Créer une nouvelle offre d'emploi (admin/hr seulement)"""
    if not request.user.is_authenticated or request.user.user_type not in ['admin', 'hr']:
        messages.error(request, "Vous n'avez pas l'autorisation de créer des offres d'emploi.")
        return redirect('job_list')
    
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.status = 'published'
            
            # Sauvegarder pour générer le slug
            job.save()
            form.save_m2m()
            
            messages.success(request, 'Offre d\'emploi créée avec succès!')
            return redirect('jobs:job_detail', slug=job.slug)
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = JobForm()
    
    return render(request, 'jobs/job_create.html', {'form': form})


@login_required
def edit_job(request, slug):
    """Modifier une offre d'emploi"""
    job = get_object_or_404(Job, slug=slug)
    
    # Vérifier les permissions
    if request.user.user_type not in ['admin', 'hr'] and job.created_by != request.user:
        messages.error(request, "Vous n'avez pas l'autorisation de modifier cette offre.")
        return redirect('job_detail', slug=job.slug)
    
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Offre d\'emploi mise à jour avec succès!')
            return redirect('job_detail', slug=job.slug)
    else:
        form = JobForm(instance=job)
    
    return render(request, 'jobs/job_edit.html', {'form': form, 'job': job})


@login_required
@require_http_methods(["POST"])
def toggle_save_job(request, job_id):
    """Sauvegarder/Désauvegarder une offre d'emploi (AJAX)"""
    job = get_object_or_404(Job, id=job_id, status='published')
    
    saved_job, created = SavedJob.objects.get_or_create(
        user=request.user,
        job=job
    )
    
    if not created:
        saved_job.delete()
        is_saved = False
        message = "Offre retirée des favoris"
    else:
        is_saved = True
        message = "Offre ajoutée aux favoris"
    
    return JsonResponse({
        'success': True,
        'is_saved': is_saved,
        'message': message
    })


@login_required
def saved_jobs(request):
    """Liste des offres sauvegardées par l'utilisateur"""
    saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job', 'job__category')
    
    # Pagination
    paginator = Paginator(saved_jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'jobs/saved_jobs.html', {'page_obj': page_obj})


@login_required
def job_alerts(request):
    """Gestion des alertes emploi"""
    alerts = JobAlert.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'jobs/job_alerts.html', {'alerts': alerts})


@login_required
def create_job_alert(request):
    """Créer une alerte emploi"""
    if request.method == 'POST':
        form = JobAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.user = request.user
            alert.save()
            messages.success(request, 'Alerte emploi créée avec succès!')
            return redirect('job_alerts')
    else:
        form = JobAlertForm()
    
    return render(request, 'jobs/create_job_alert.html', {'form': form})


@login_required
def edit_job_alert(request, alert_id):
    """Modifier une alerte emploi"""
    alert = get_object_or_404(JobAlert, id=alert_id, user=request.user)
    
    if request.method == 'POST':
        form = JobAlertForm(request.POST, instance=alert)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alerte emploi mise à jour avec succès!')
            return redirect('job_alerts')
    else:
        form = JobAlertForm(instance=alert)
    
    return render(request, 'jobs/edit_job_alert.html', {'form': form, 'alert': alert})


@login_required
@require_http_methods(["POST"])
def delete_job_alert(request, alert_id):
    """Supprimer une alerte emploi"""
    alert = get_object_or_404(JobAlert, id=alert_id, user=request.user)
    alert.delete()
    messages.success(request, 'Alerte emploi supprimée avec succès!')
    return redirect('job_alerts')


@login_required
@require_http_methods(["POST"])
def toggle_job_alert(request, alert_id):
    """Activer/Désactiver une alerte emploi (AJAX)"""
    alert = get_object_or_404(JobAlert, id=alert_id, user=request.user)
    alert.is_active = not alert.is_active
    alert.save()
    
    return JsonResponse({
        'success': True,
        'is_active': alert.is_active,
        'message': 'Alerte activée' if alert.is_active else 'Alerte désactivée'
    })


def job_categories(request):
    """Liste des catégories d'emploi"""
    categories = JobCategory.objects.filter(is_active=True).annotate(
        job_count=Count('jobs', filter=Q(jobs__status='published'))
    ).order_by('name')
    
    return render(request, 'jobs/job_categories.html', {'categories': categories})


def jobs_by_category(request, category_id):
    """Offres d'emploi par catégorie"""
    category = get_object_or_404(JobCategory, id=category_id, is_active=True)
    jobs = Job.objects.filter(category=category, status='published').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(jobs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'jobs/jobs_by_category.html', {
        'category': category,
        'page_obj': page_obj
    })