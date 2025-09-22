from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import (
    Application, ApplicationComment, Interview, 
    ApplicationRating, ApplicationStatusHistory
)
from .forms import (
    ApplicationForm, ApplicationStatusForm, ApplicationCommentForm,
    InterviewForm, InterviewFeedbackForm, ApplicationRatingForm,
    ApplicationSearchForm
)
from apps.jobs.models import Job
from apps.accounts.models import CandidateProfile
# Ajout des imports pour les emails
from apps.core.tasks import send_application_received_email, send_interview_invitation_email


@login_required
def apply_to_job(request, job_id):
    """Postuler à une offre d'emploi"""
    job = get_object_or_404(Job, id=job_id, status='published')
    
    # Vérifier que l'utilisateur est un candidat
    if request.user.user_type != 'candidate':
        messages.error(request, "Seuls les candidats peuvent postuler aux offres.")
        return redirect('jobs:job_detail', slug=job.slug)
    
    # Vérifier que le candidat a un profil
    try:
        candidate_profile = request.user.candidate_profile
    except CandidateProfile.DoesNotExist:
        messages.error(request, "Vous devez compléter votre profil avant de postuler.")
        return redirect('accounts:edit_profile')
    
    # Vérifier si le candidat a déjà postulé
    if Application.objects.filter(candidate=candidate_profile, job=job).exists():
        messages.warning(request, "Vous avez déjà postulé à cette offre.")
        return redirect('jobs:job_detail', slug=job.slug)
    
    # Vérifier si l'offre est encore active
    if not job.is_active:
        messages.error(request, "Cette offre n'est plus disponible.")
        return redirect('jobs:job_detail', slug=job.slug)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES, job=job)
        if form.is_valid():
            application = form.save(commit=False)
            application.candidate = candidate_profile
            application.job = job
            application.save()
            
            # Envoyer l'email de confirmation
            send_application_received_email.delay(application.id)
            
            # Incrémenter le compteur de candidatures du job
            job.increment_applications()
            
            messages.success(request, 'Votre candidature a été envoyée avec succès!')
            return redirect('applications:my_applications')
    else:
        form = ApplicationForm(job=job)
    
    return render(request, 'applications/apply.html', {
        'form': form,
        'job': job,
        'candidate_profile': candidate_profile
    })


@login_required
def my_applications(request):
    """Mes candidatures (pour les candidats)"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('core:home')
    
    try:
        candidate_profile = request.user.candidate_profile
    except CandidateProfile.DoesNotExist:
        messages.error(request, "Profil candidat non trouvé.")
        return redirect('accounts:edit_profile')
    
    applications = Application.objects.filter(candidate=candidate_profile).select_related('job')
    
    # Filtres
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total': applications.count(),
        'pending': applications.filter(status='pending').count(),
        'reviewing': applications.filter(status='reviewing').count(),
        'shortlisted': applications.filter(status='shortlisted').count(),
        'rejected': applications.filter(status='rejected').count(),
    }
    
    return render(request, 'applications/my_applications.html', {
        'page_obj': page_obj,
        'stats': stats,
        'status_choices': Application.STATUS_CHOICES,
        'current_status': status_filter
    })


@login_required
def application_detail(request, pk):
    """Détail d'une candidature"""
    application = get_object_or_404(Application, pk=pk)
    
    # Vérifier les permissions
    if request.user.user_type == 'candidate':
        if application.candidate.user != request.user:
            messages.error(request, "Vous ne pouvez voir que vos propres candidatures.")
            return redirect('applications:my_applications')
    elif request.user.user_type not in ['admin', 'hr']:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    # Marquer comme examiné si c'est un admin/hr
    if request.user.user_type in ['admin', 'hr'] and not application.reviewed_by:
        application.mark_as_reviewed(request.user)
    
    # Récupérer les données associées
    comments = application.comments.all().select_related('author')
    interviews = application.interviews.all().select_related('created_by')
    ratings = application.ratings.all().select_related('evaluator')
    status_history = application.status_history.all().select_related('changed_by')
    
    # Calculer la note moyenne
    avg_rating = ratings.aggregate(avg_score=Avg('score'))['avg_score']
    
    context = {
        'application': application,
        'comments': comments,
        'interviews': interviews,
        'ratings': ratings,
        'status_history': status_history,
        'avg_rating': avg_rating,
        'can_edit': request.user.user_type in ['admin', 'hr'],
    }
    
    return render(request, 'applications/application_detail.html', context)


@login_required
def update_application_status(request, pk):
    """Mettre à jour le statut d'une candidature"""
    if request.user.user_type not in ['admin', 'hr']:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    application = get_object_or_404(Application, pk=pk)
    
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            old_status = application.status
            new_application = form.save()
            
            # Enregistrer l'historique si le statut a changé
            if old_status != new_application.status:
                ApplicationStatusHistory.objects.create(
                    application=new_application,
                    previous_status=old_status,
                    new_status=new_application.status,
                    changed_by=request.user,
                    reason=form.cleaned_data.get('reason', '')
                )
            
            messages.success(request, 'Statut mis à jour avec succès!')
            return redirect('applications:application_detail', pk=application.pk)
    else:
        form = ApplicationStatusForm(instance=application)
    
    return render(request, 'applications/update_status.html', {
        'form': form,
        'application': application
    })


@login_required
def add_comment(request, pk):
    """Ajouter un commentaire à une candidature"""
    if request.user.user_type not in ['admin', 'hr']:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    application = get_object_or_404(Application, pk=pk)
    
    if request.method == 'POST':
        form = ApplicationCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.application = application
            comment.author = request.user
            comment.save()
            
            messages.success(request, 'Commentaire ajouté avec succès!')
            return redirect('applications:application_detail', pk=application.pk)
    else:
        form = ApplicationCommentForm()
    
    return render(request, 'applications/add_comment.html', {
        'form': form,
        'application': application
    })


@login_required
def schedule_interview(request, pk):
    """Programmer un entretien"""
    if request.user.user_type not in ['admin', 'hr']:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    application = get_object_or_404(Application, pk=pk)
    
    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.created_by = request.user
            interview.save()
            form.save_m2m()  # Pour les ManyToMany fields
            
            # Envoyer l'email d'invitation
            send_interview_invitation_email.delay(interview.id)
            
            # Mettre à jour le statut de la candidature
            if application.status in ['pending', 'reviewing']:
                application.status = 'interview_scheduled'
                application.save()
            
            messages.success(request, 'Entretien programmé avec succès!')
            return redirect('applications:application_detail', pk=application.pk)
    else:
        form = InterviewForm()
    
    return render(request, 'applications/schedule_interview.html', {
        'form': form,
        'application': application
    })


@login_required
def interview_feedback(request, interview_id):
    """Feedback d'entretien"""
    if request.user.user_type not in ['admin', 'hr']:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    interview = get_object_or_404(Interview, id=interview_id)
    
    # Vérifier que l'utilisateur est un des interviewers
    if not interview.interviewers.filter(id=request.user.id).exists():
        messages.error(request, "Vous n'êtes pas autorisé à donner un feedback pour cet entretien.")
        return redirect('applications:application_detail', pk=interview.application.pk)
    
    if request.method == 'POST':
        form = InterviewFeedbackForm(request.POST, instance=interview)
        if form.is_valid():
            interview = form.save()
            
            # Mettre à jour le statut de la candidature si nécessaire
            if interview.status == 'completed' and interview.application.status == 'interview_scheduled':
                interview.application.status = 'interview_completed'
                interview.application.save()
            
            messages.success(request, 'Feedback enregistré avec succès!')
            return redirect('applications:application_detail', pk=interview.application.pk)
    else:
        form = InterviewFeedbackForm(instance=interview)
    
    return render(request, 'applications/interview_feedback.html', {
        'form': form,
        'interview': interview
    })


@login_required
def rate_application(request, pk):
    """Évaluer une candidature"""
    if request.user.user_type not in ['admin', 'hr']:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    application = get_object_or_404(Application, pk=pk)
    
    if request.method == 'POST':
        form = ApplicationRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.application = application
            rating.evaluator = request.user
            rating.save()
            
            messages.success(request, 'Évaluation enregistrée avec succès!')
            return redirect('applications:application_detail', pk=application.pk)
    else:
        form = ApplicationRatingForm()
    
    return render(request, 'applications/rate_application.html', {
        'form': form,
        'application': application
    })


@login_required
def applications_list(request):
    """Liste des candidatures (pour admin/hr)"""
    if request.user.user_type not in ['admin', 'hr']:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    applications = Application.objects.all().select_related(
        'candidate__user', 'job', 'reviewed_by'
    )
    
    # Recherche et filtres
    form = ApplicationSearchForm(request.GET)
    if form.is_valid():
        keywords = form.cleaned_data.get('keywords')
        job = form.cleaned_data.get('job')
        status = form.cleaned_data.get('status')
        priority = form.cleaned_data.get('priority')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if keywords:
            applications = applications.filter(
                Q(candidate__user__first_name__icontains=keywords) |
                Q(candidate__user__last_name__icontains=keywords) |
                Q(candidate__user__email__icontains=keywords) |
                Q(job__title__icontains=keywords)
            )
        
        if job:
            applications = applications.filter(job=job)
        
        if status:
            applications = applications.filter(status=status)
        
        if priority:
            applications = applications.filter(priority=priority)
        
        if date_from:
            applications = applications.filter(applied_at__date__gte=date_from)
        
        if date_to:
            applications = applications.filter(applied_at__date__lte=date_to)
    
    # Tri
    sort_by = request.GET.get('sort', '-applied_at')
    if sort_by in ['-applied_at', 'candidate__user__last_name', 'job__title', 'status']:
        applications = applications.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(applications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total': applications.count(),
        'pending': applications.filter(status='pending').count(),
        'reviewing': applications.filter(status='reviewing').count(),
        'shortlisted': applications.filter(status='shortlisted').count(),
        'interviews': applications.filter(status__in=['interview_scheduled', 'interview_completed']).count(),
    }
    
    return render(request, 'applications/applications_list.html', {
        'form': form,
        'page_obj': page_obj,
        'stats': stats,
        'current_sort': sort_by
    })


@login_required
def withdraw_application(request, pk):
    """Retirer une candidature"""
    application = get_object_or_404(Application, pk=pk)
    
    # Vérifier que c'est le candidat qui retire sa candidature
    if request.user.user_type != 'candidate' or application.candidate.user != request.user:
        messages.error(request, "Vous ne pouvez retirer que vos propres candidatures.")
        return redirect('applications:my_applications')
    
    # Vérifier que la candidature peut être retirée
    if application.status in ['accepted', 'rejected']:
        messages.error(request, "Cette candidature ne peut plus être retirée.")
        return redirect('applications:application_detail', pk=application.pk)
    
    if request.method == 'POST':
        old_status = application.status
        application.status = 'withdrawn'
        application.save()
        
        # Enregistrer l'historique
        ApplicationStatusHistory.objects.create(
            application=application,
            previous_status=old_status,
            new_status='withdrawn',
            changed_by=request.user,
            reason="Candidature retirée par le candidat"
        )
        
        messages.success(request, 'Candidature retirée avec succès.')
        return redirect('applications:my_applications')
    
    return render(request, 'applications/withdraw_application.html', {
        'application': application
    })
