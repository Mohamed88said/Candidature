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
    ApplicationRating, ApplicationStatusHistory, VideoQuestion, VideoApplication
)
from .forms import (
    ApplicationForm, ApplicationStatusForm, ApplicationCommentForm,
    InterviewForm, InterviewFeedbackForm, ApplicationRatingForm,
    ApplicationSearchForm, VideoApplicationForm, VideoQuestionForm, 
    VideoResponseForm, VideoApplicationSearchForm
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


# =============================================================================
# VUES POUR LES CANDIDATURES VIDÉO
# =============================================================================

@login_required
def apply_with_video(request, job_id):
    """Postuler avec une vidéo de présentation"""
    job = get_object_or_404(Job, id=job_id, status='published')
    
    # Vérifier que l'utilisateur est un candidat
    if request.user.user_type != 'candidate':
        messages.error(request, 'Seuls les candidats peuvent postuler.')
        return redirect('jobs:job_detail', job_id=job_id)
    
    try:
        candidate_profile = request.user.candidate_profile
    except CandidateProfile.DoesNotExist:
        messages.error(request, 'Veuillez compléter votre profil avant de postuler.')
        return redirect('accounts:profile_edit')
    
    # Vérifier si le candidat a déjà postulé
    if Application.objects.filter(candidate=candidate_profile, job=job).exists():
        messages.warning(request, 'Vous avez déjà postulé à cette offre.')
        return redirect('jobs:job_detail', job_id=job_id)
    
    if request.method == 'POST':
        form = VideoApplicationForm(request.POST, request.FILES, job=job)
        if form.is_valid():
            # Créer d'abord l'application de base
            application = Application.objects.create(
                candidate=candidate_profile,
                job=job,
                cover_letter="Candidature avec vidéo de présentation",
                presentation_video=form.cleaned_data['main_video'],
                video_duration=form.cleaned_data['total_duration'],
                status='pending'
            )
            
            # Créer la candidature vidéo spécialisée
            video_application = form.save(commit=False)
            video_application.application = application
            video_application.save()
            
            # Envoyer email de confirmation
            send_application_received_email.delay(application.id)
            
            messages.success(request, 'Votre candidature vidéo a été envoyée avec succès !')
            return redirect('applications:application_detail', pk=application.pk)
    else:
        form = VideoApplicationForm(job=job)
    
    # Récupérer les questions vidéo pour cette offre
    video_questions = VideoQuestion.objects.filter(job=job, is_active=True).order_by('order')
    
    context = {
        'form': form,
        'job': job,
        'video_questions': video_questions,
    }
    
    return render(request, 'applications/apply_with_video.html', context)


@login_required
def video_questions_management(request, job_id):
    """Gestion des questions vidéo pour une offre (admin/HR)"""
    if not request.user.is_staff and request.user.user_type != 'hr':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    job = get_object_or_404(Job, id=job_id)
    questions = VideoQuestion.objects.filter(job=job).order_by('order')
    
    if request.method == 'POST':
        form = VideoQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.job = job
            question.save()
            messages.success(request, 'Question vidéo ajoutée avec succès.')
            return redirect('applications:video_questions_management', job_id=job_id)
    else:
        form = VideoQuestionForm()
    
    context = {
        'job': job,
        'questions': questions,
        'form': form,
    }
    
    return render(request, 'applications/video_questions_management.html', context)


@login_required
def edit_video_question(request, question_id):
    """Modifier une question vidéo"""
    if not request.user.is_staff and request.user.user_type != 'hr':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    question = get_object_or_404(VideoQuestion, id=question_id)
    
    if request.method == 'POST':
        form = VideoQuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question vidéo modifiée avec succès.')
            return redirect('applications:video_questions_management', job_id=question.job.id)
    else:
        form = VideoQuestionForm(instance=question)
    
    context = {
        'form': form,
        'question': question,
    }
    
    return render(request, 'applications/edit_video_question.html', context)


@login_required
def delete_video_question(request, question_id):
    """Supprimer une question vidéo"""
    if not request.user.is_staff and request.user.user_type != 'hr':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    question = get_object_or_404(VideoQuestion, id=question_id)
    job_id = question.job.id
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question vidéo supprimée avec succès.')
        return redirect('applications:video_questions_management', job_id=job_id)
    
    return render(request, 'applications/delete_video_question.html', {
        'question': question
    })


@login_required
def video_applications_list(request):
    """Liste des candidatures vidéo (admin/HR)"""
    if not request.user.is_staff and request.user.user_type != 'hr':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    # Filtres
    search_form = VideoApplicationSearchForm(request.GET)
    video_applications = VideoApplication.objects.select_related(
        'application__candidate__user', 'application__job'
    ).order_by('-created_at')
    
    if search_form.is_valid():
        if search_form.cleaned_data.get('keywords'):
            keywords = search_form.cleaned_data['keywords']
            video_applications = video_applications.filter(
                Q(application__candidate__user__first_name__icontains=keywords) |
                Q(application__candidate__user__last_name__icontains=keywords) |
                Q(application__job__title__icontains=keywords) |
                Q(application__job__company__icontains=keywords)
            )
        
        if search_form.cleaned_data.get('job'):
            video_applications = video_applications.filter(application__job=search_form.cleaned_data['job'])
        
        if search_form.cleaned_data.get('video_quality'):
            video_applications = video_applications.filter(video_quality=search_form.cleaned_data['video_quality'])
        
        if search_form.cleaned_data.get('processing_status'):
            video_applications = video_applications.filter(processing_status=search_form.cleaned_data['processing_status'])
        
        if search_form.cleaned_data.get('has_transcript'):
            video_applications = video_applications.exclude(transcript='')
        
        if search_form.cleaned_data.get('date_from'):
            video_applications = video_applications.filter(created_at__date__gte=search_form.cleaned_data['date_from'])
        
        if search_form.cleaned_data.get('date_to'):
            video_applications = video_applications.filter(created_at__date__lte=search_form.cleaned_data['date_to'])
    
    # Pagination
    paginator = Paginator(video_applications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_count': video_applications.count(),
    }
    
    return render(request, 'applications/video_applications_list.html', context)


@login_required
def video_application_detail(request, video_app_id):
    """Détail d'une candidature vidéo"""
    video_application = get_object_or_404(VideoApplication, id=video_app_id)
    
    # Vérifier les permissions
    if (request.user.user_type == 'candidate' and 
        video_application.application.candidate.user != request.user):
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    if (request.user.user_type in ['admin', 'hr'] and 
        not request.user.is_staff and 
        request.user.user_type != 'hr'):
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    context = {
        'video_application': video_application,
        'application': video_application.application,
    }
    
    return render(request, 'applications/video_application_detail.html', context)


@login_required
@require_http_methods(["POST"])
def process_video_application(request, video_app_id):
    """Traiter une candidature vidéo (transcription, analyse)"""
    if not request.user.is_staff and request.user.user_type != 'hr':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    video_application = get_object_or_404(VideoApplication, id=video_app_id)
    
    # Simuler le traitement (dans un vrai projet, ceci serait fait par une tâche asynchrone)
    video_application.processing_status = 'processing'
    video_application.save()
    
    # Ici, vous pourriez lancer une tâche Celery pour :
    # - Extraire l'audio de la vidéo
    # - Faire la transcription avec un service comme Google Speech-to-Text
    # - Analyser les mots-clés
    # - Faire l'analyse de sentiment
    
    # Pour l'instant, on simule juste le traitement
    import time
    time.sleep(2)  # Simulation du traitement
    
    video_application.processing_status = 'completed'
    video_application.is_processed = True
    video_application.transcript = "Transcription simulée de la vidéo de candidature..."
    video_application.keywords_extracted = ['motivation', 'expérience', 'compétences']
    video_application.sentiment_analysis = {
        'positive': 0.8,
        'neutral': 0.2,
        'negative': 0.0
    }
    video_application.save()
    
    messages.success(request, 'Candidature vidéo traitée avec succès.')
    return redirect('applications:video_application_detail', video_app_id=video_app_id)


@login_required
def video_application_analytics(request):
    """Analytics des candidatures vidéo (admin)"""
    if not request.user.is_staff:
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    # Statistiques générales
    total_video_applications = VideoApplication.objects.count()
    processed_applications = VideoApplication.objects.filter(is_processed=True).count()
    applications_with_transcript = VideoApplication.objects.exclude(transcript='').count()
    
    # Statistiques par qualité vidéo
    quality_stats = VideoApplication.objects.values('video_quality').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Statistiques par statut de traitement
    processing_stats = VideoApplication.objects.values('processing_status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Durée moyenne des vidéos
    avg_duration = VideoApplication.objects.aggregate(
        avg_duration=Avg('total_duration')
    )['avg_duration'] or 0
    
    context = {
        'total_video_applications': total_video_applications,
        'processed_applications': processed_applications,
        'applications_with_transcript': applications_with_transcript,
        'quality_stats': quality_stats,
        'processing_stats': processing_stats,
        'avg_duration': round(avg_duration, 1),
    }
    
    return render(request, 'applications/video_application_analytics.html', context)
