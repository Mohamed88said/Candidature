from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import (
    User, CandidateProfile, Education, Experience, 
    Skill, Language, Certification, Reference, Project, Award, SocialProfile
)
from .forms import (
    CustomUserCreationForm, CandidateProfileForm, EducationForm, 
    ExperienceForm, SkillForm, LanguageForm, CertificationForm, ReferenceForm
)
# Ajout des imports pour les emails
from django.core.mail import send_mail
from django.conf import settings
from apps.core.tasks import send_welcome_email, send_password_reset_email
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .utils import send_html_email, get_email_context 
from django.contrib.auth.views import PasswordResetView


def register(request):
    """Vue d'inscription"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé pour {username}!')
            
            # Créer automatiquement un profil candidat si c'est un candidat
            if user.user_type == 'candidate':
                CandidateProfile.objects.get_or_create(user=user)
            
            # Envoyer l'email de bienvenue de manière asynchrone
            send_welcome_email.delay(user.email, user.full_name)
            
            # Connecter automatiquement l'utilisateur
            login(request, user)
            return redirect('accounts:profile')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """Vue du profil utilisateur"""
    if request.user.user_type == 'candidate':
        profile, created = CandidateProfile.objects.get_or_create(user=request.user)
        if created:
            profile.calculate_profile_completion()
        
        # Calculer l'expérience
        profile.calculate_experience_years()
        
        # Obtenir les recommandations d'emploi
        from .utils import get_matching_jobs
        recommended_jobs = get_matching_jobs(profile, limit=6)
        
        context = {
            'profile': profile,
            'educations': profile.educations.all(),
            'experiences': profile.experiences.all(),
            'skills': profile.skills.all(),
            'languages': profile.languages.all(),
            'certifications': profile.certifications.all(),
            'references': profile.references.all(),
            'projects': profile.projects.all(),
            'social_profiles': profile.social_profiles.all(),
            'awards': profile.awards.all(),
            'recommended_jobs': [item['job'] for item in recommended_jobs],
        }
        return render(request, 'accounts/profile.html', context)
    else:
        return redirect('dashboard:admin_dashboard')


@login_required
def edit_profile(request):
    """Vue d'édition du profil"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('core:home')
    
    profile, created = CandidateProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = CandidateProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save()
            profile.calculate_profile_completion()
            messages.success(request, 'Profil mis à jour avec succès!')
            return redirect('accounts:profile')
    else:
        form = CandidateProfileForm(instance=profile)
    
    return render(request, 'accounts/profile_edit.html', {'form': form, 'profile': profile})


@login_required
def add_education(request):
    """Ajouter une formation"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.candidate = profile
            education.save()
            profile.calculate_profile_completion()
            messages.success(request, 'Formation ajoutée avec succès!')
            return redirect('accounts:profile')
    else:
        form = EducationForm()
    
    return render(request, 'accounts/add_education.html', {'form': form})


@login_required
def edit_education(request, education_id):
    """Modifier une formation"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    education = get_object_or_404(Education, id=education_id, candidate=profile)
    
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, 'Formation mise à jour avec succès!')
            return redirect('accounts:profile')
    else:
        form = EducationForm(instance=education)
    
    return render(request, 'accounts/edit_education.html', {'form': form, 'education': education})


@login_required
def delete_education(request, education_id):
    """Supprimer une formation"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    education = get_object_or_404(Education, id=education_id, candidate=profile)
    
    if request.method == 'POST':
        education.delete()
        profile.calculate_profile_completion()
        messages.success(request, 'Formation supprimée avec succès!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/confirm_delete.html', {
        'object': education,
        'object_type': 'formation'
    })


@login_required
def add_experience(request):
    """Ajouter une expérience"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.candidate = profile
            experience.save()
            profile.calculate_profile_completion()
            messages.success(request, 'Expérience ajoutée avec succès!')
            return redirect('accounts:profile')
    else:
        form = ExperienceForm()
    
    return render(request, 'accounts/add_experience.html', {'form': form})


@login_required
def edit_experience(request, experience_id):
    """Modifier une expérience"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    experience = get_object_or_404(Experience, id=experience_id, candidate=profile)
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expérience mise à jour avec succès!')
            return redirect('accounts:profile')
    else:
        form = ExperienceForm(instance=experience)
    
    return render(request, 'accounts/edit_experience.html', {'form': form, 'experience': experience})


@login_required
def delete_experience(request, experience_id):
    """Supprimer une expérience"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    experience = get_object_or_404(Experience, id=experience_id, candidate=profile)
    
    if request.method == 'POST':
        experience.delete()
        profile.calculate_profile_completion()
        messages.success(request, 'Expérience supprimée avec succès!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/confirm_delete.html', {
        'object': experience,
        'object_type': 'expérience'
    })


@login_required
def add_skill(request):
    """Ajouter une compétence"""
    if request.user.user_type != 'candidate':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.candidate = profile
            skill.save()
            profile.calculate_profile_completion()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'skill': {
                        'id': skill.id,
                        'name': skill.name,
                        'level': skill.get_level_display(),
                        'category': skill.get_category_display()
                    }
                })
            
            messages.success(request, 'Compétence ajoutée avec succès!')
            return redirect('accounts:profile')
    else:
        form = SkillForm()
    
    return render(request, 'accounts/add_skill.html', {'form': form})


@login_required
@require_http_methods(["DELETE"])
def delete_skill(request, skill_id):
    """Supprimer une compétence (AJAX)"""
    if request.user.user_type != 'candidate':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    skill = get_object_or_404(Skill, id=skill_id, candidate=profile)
    
    skill.delete()
    profile.calculate_profile_completion()
    
    return JsonResponse({'success': True})


@login_required
def add_language(request):
    """Ajouter une langue"""
    if request.user.user_type != 'candidate':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    
    if request.method == 'POST':
        form = LanguageForm(request.POST)
        if form.is_valid():
            language = form.save(commit=False)
            language.candidate = profile
            language.save()
            profile.calculate_profile_completion()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'language': {
                        'id': language.id,
                        'language': language.language,
                        'proficiency': language.get_proficiency_display()
                    }
                })
            
            messages.success(request, 'Langue ajoutée avec succès!')
            return redirect('accounts:profile')
    else:
        form = LanguageForm()
    
    return render(request, 'accounts/add_language.html', {'form': form})


@login_required
@require_http_methods(["DELETE"])
def delete_language(request, language_id):
    """Supprimer une langue (AJAX)"""
    if request.user.user_type != 'candidate':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    language = get_object_or_404(Language, id=language_id, candidate=profile)
    
    language.delete()
    profile.calculate_profile_completion()
    
    return JsonResponse({'success': True})


@login_required
def add_certification(request):
    """Ajouter une certification"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    
    if request.method == 'POST':
        form = CertificationForm(request.POST)
        if form.is_valid():
            certification = form.save(commit=False)
            certification.candidate = profile
            certification.save()
            profile.calculate_profile_completion()
            messages.success(request, 'Certification ajoutée avec succès!')
            return redirect('accounts:profile')
    else:
        form = CertificationForm()
    
    return render(request, 'accounts/add_certification.html', {'form': form})


@login_required
def delete_certification(request, certification_id):
    """Supprimer une certification"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    certification = get_object_or_404(Certification, id=certification_id, candidate=profile)
    
    if request.method == 'POST':
        certification.delete()
        profile.calculate_profile_completion()
        messages.success(request, 'Certification supprimée avec succès!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/confirm_delete.html', {
        'object': certification,
        'object_type': 'certification'
    })


@login_required
def add_reference(request):
    """Ajouter une référence"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    
    if request.method == 'POST':
        form = ReferenceForm(request.POST)
        if form.is_valid():
            reference = form.save(commit=False)
            reference.candidate = profile
            reference.save()
            profile.calculate_profile_completion()
            messages.success(request, 'Référence ajoutée avec succès!')
            return redirect('accounts:profile')
    else:
        form = ReferenceForm()
    
    return render(request, 'accounts/add_reference.html', {'form': form})


@login_required
def delete_reference(request, reference_id):
    """Supprimer une référence"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    reference = get_object_or_404(Reference, id=reference_id, candidate=profile)
    
    if request.method == 'POST':
        reference.delete()
        profile.calculate_profile_completion()
        messages.success(request, 'Référence supprimée avec succès!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/confirm_delete.html', {
        'object': reference,
        'object_type': 'référence'
    })


@login_required
def dashboard(request):
    """Dashboard utilisateur"""
    if request.user.user_type == 'candidate':
        return redirect('accounts:profile')
    else:
        return redirect('dashboard:admin_dashboard')


@login_required
def add_project(request):
    """Ajouter un projet"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    
    if request.method == 'POST':
        messages.success(request, 'Fonctionnalité projet à implémenter!')
        return redirect('accounts:profile')
    else:
        return render(request, 'accounts/under_construction.html', {
            'message': 'La fonctionnalité d\'ajout de projet sera bientôt disponible'
        })


@login_required
def edit_project(request, project_id):
    """Modifier un projet"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    project = get_object_or_404(Project, id=project_id, candidate=profile)
    
    if request.method == 'POST':
        messages.success(request, 'Projet modifié avec succès!')
        return redirect('accounts:profile')
    else:
        return render(request, 'accounts/under_construction.html', {
            'message': 'La fonctionnalité de modification de projet sera bientôt disponible'
        })


@login_required
def delete_project(request, project_id):
    """Supprimer un projet"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    project = get_object_or_404(Project, id=project_id, candidate=profile)
    
    if request.method == 'POST':
        project.delete()
        profile.calculate_profile_completion()
        messages.success(request, 'Projet supprimé avec succès!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/confirm_delete.html', {
        'object': project,
        'object_type': 'projet'
    })


@login_required
def add_award(request):
    """Ajouter un prix/reconnaissance"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    
    if request.method == 'POST':
        messages.success(request, 'Prix ajouté avec succès!')
        return redirect('accounts:profile')
    else:
        return render(request, 'accounts/under_construction.html', {
            'message': 'La fonctionnalité d\'ajout de prix sera bientôt disponible'
        })


@login_required
def delete_award(request, award_id):
    """Supprimer un prix/reconnaissance"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    award = get_object_or_404(Award, id=award_id, candidate=profile)
    
    if request.method == 'POST':
        award.delete()
        profile.calculate_profile_completion()
        messages.success(request, 'Prix supprimé avec succès!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/confirm_delete.html', {
        'object': award,
        'object_type': 'prix'
    })


@login_required
def add_social_profile(request):
    """Ajouter un profil social"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    
    if request.method == 'POST':
        messages.success(request, 'Profil social ajouté avec succès!')
        return redirect('accounts:profile')
    else:
        return render(request, 'accounts/under_construction.html', {
            'message': 'La fonctionnalité d\'ajout de profil social sera bientôt disponible'
        })


@login_required
def delete_social_profile(request, profile_id):
    """Supprimer un profil social"""
    if request.user.user_type != 'candidate':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    profile = get_object_or_404(CandidateProfile, user=request.user)
    social_profile = get_object_or_404(SocialProfile, id=profile_id, candidate=profile)
    
    if request.method == 'POST':
        social_profile.delete()
        profile.calculate_profile_completion()
        messages.success(request, 'Profil social supprimé avec succès!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/confirm_delete.html', {
        'object': social_profile,
        'object_type': 'profil social'
    })
# Ajoute ces imports en haut du fichier si pas déjà présents


def get_email_context():
    """Retourne le contexte commun pour tous les emails"""
    return {
        'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@recruitment-platform.com'),
        'site_name': getattr(settings, 'SITE_NAME', 'Plateforme de Recrutement')
    }

def send_custom_password_reset_email(user, reset_url):
    """Envoie un email de réinitialisation personnalisé"""
    context = get_email_context()
    context.update({
        'user': user,
        'user_name': user.get_full_name() or user.username,
        'reset_url': reset_url,
        'protocol': 'https' if not settings.DEBUG else 'http',
        'domain': settings.SITE_URL.split('://')[-1] if hasattr(settings, 'SITE_URL') else 'localhost:8000'
    })
    
    subject = "Réinitialisation de votre mot de passe"
    html_message = render_to_string('emails/password_reset.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False
    




class CustomPasswordResetView(PasswordResetView):
    """Vue personnalisée pour l'envoi d'emails HTML"""
    
    def form_valid(self, form):
        # Préparer le contexte pour l'email
        context = {
            'email': form.cleaned_data["email"],
            'domain': self.request.get_host(),
            'site_name': getattr(settings, 'SITE_NAME', 'Plateforme de Recrutement'),
            'protocol': 'https' if self.request.is_secure() else 'http',
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'mohamedsaiddiallo88@gmail.com'),
        }
        
        # Appeler la méthode parente
        return super().form_valid(form)
