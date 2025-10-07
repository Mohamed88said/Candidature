from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import render_to_string
from django.conf import settings
import json
import os
import uuid
from datetime import datetime, timedelta

from .models import (
    CV, CVTemplate, CVSection, CVShare, CVExport, 
    CVFeedback, CVBuilderSettings, CVAnalytics
)
from .forms import (
    CVForm, PersonalInfoForm, ExperienceForm, EducationForm, SkillForm,
    ProjectForm, LanguageForm, CertificationForm, ReferenceForm,
    CVShareForm, CVFeedbackForm, CVBuilderSettingsForm
)


@login_required
def cv_builder_dashboard(request):
    """Dashboard principal du constructeur de CV"""
    try:
        # Statistiques de l'utilisateur
        total_cvs = CV.objects.filter(user=request.user).count()
        published_cvs = CV.objects.filter(user=request.user, status='published').count()
        draft_cvs = CV.objects.filter(user=request.user, status='draft').count()
        
        # CVs récents
        recent_cvs = CV.objects.filter(user=request.user).order_by('-last_modified')[:5]
        
        # Modèles disponibles
        available_templates = CVTemplate.objects.filter(is_active=True).order_by('name')
        
        # Paramètres de l'utilisateur
        settings, created = CVBuilderSettings.objects.get_or_create(user=request.user)
        
        context = {
            'total_cvs': total_cvs,
            'published_cvs': published_cvs,
            'draft_cvs': draft_cvs,
            'recent_cvs': recent_cvs,
            'available_templates': available_templates,
            'settings': settings,
        }
        
        return render(request, 'cv_builder/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du dashboard: {e}")
        return redirect('home')


@login_required
def template_gallery(request):
    """Galerie des modèles de CV"""
    try:
        templates = CVTemplate.objects.filter(is_active=True).order_by('category', 'name')
        
        # Filtrer par catégorie
        category = request.GET.get('category', '')
        if category:
            templates = templates.filter(category=category)
        
        # Pagination
        paginator = Paginator(templates, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Catégories disponibles
        categories = CVTemplate.TEMPLATE_CATEGORY_CHOICES
        
        context = {
            'page_obj': page_obj,
            'categories': categories,
            'selected_category': category,
        }
        
        return render(request, 'cv_builder/template_gallery.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement de la galerie: {e}")
        return redirect('cv_builder:dashboard')


@login_required
def create_cv(request, template_id=None):
    """Créer un nouveau CV"""
    try:
        if request.method == 'POST':
            form = CVForm(request.POST)
            if form.is_valid():
                cv = form.save(commit=False)
                cv.user = request.user
                cv.save()
                
                messages.success(request, 'CV créé avec succès !')
                return redirect('cv_builder:edit_cv', cv_id=cv.id)
        else:
            # Pré-sélectionner le modèle si spécifié
            initial_data = {}
            if template_id:
                template = get_object_or_404(CVTemplate, id=template_id, is_active=True)
                initial_data['template'] = template
            
            form = CVForm(initial=initial_data)
        
        # Modèles disponibles
        templates = CVTemplate.objects.filter(is_active=True).order_by('name')
        
        context = {
            'form': form,
            'templates': templates,
            'selected_template_id': template_id,
        }
        
        return render(request, 'cv_builder/create_cv.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la création du CV: {e}")
        return redirect('cv_builder:dashboard')


@login_required
def edit_cv(request, cv_id):
    """Éditer un CV existant"""
    try:
        cv = get_object_or_404(CV, id=cv_id, user=request.user)
        
        if request.method == 'POST':
            form = CVForm(request.POST, instance=cv)
            if form.is_valid():
                form.save()
                messages.success(request, 'CV mis à jour avec succès !')
                return redirect('cv_builder:edit_cv', cv_id=cv.id)
        else:
            form = CVForm(instance=cv)
        
        # Formulaires pour les différentes sections
        personal_info_form = PersonalInfoForm(initial=cv.personal_info)
        experience_form = ExperienceForm()
        education_form = EducationForm()
        skill_form = SkillForm()
        project_form = ProjectForm()
        language_form = LanguageForm()
        certification_form = CertificationForm()
        reference_form = ReferenceForm()
        
        context = {
            'cv': cv,
            'form': form,
            'personal_info_form': personal_info_form,
            'experience_form': experience_form,
            'education_form': education_form,
            'skill_form': skill_form,
            'project_form': project_form,
            'language_form': language_form,
            'certification_form': certification_form,
            'reference_form': reference_form,
        }
        
        return render(request, 'cv_builder/edit_cv.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de l\'édition du CV: {e}")
        return redirect('cv_builder:dashboard')


@login_required
def preview_cv(request, cv_id):
    """Prévisualiser un CV"""
    try:
        cv = get_object_or_404(CV, id=cv_id, user=request.user)
        
        context = {
            'cv': cv,
        }
        
        return render(request, f'cv_builder/templates/{cv.template.name.lower()}.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la prévisualisation: {e}")
        return redirect('cv_builder:edit_cv', cv_id=cv_id)


def public_cv_view(request, share_url):
    """Voir un CV partagé publiquement"""
    try:
        cv_share = get_object_or_404(CVShare, share_url=share_url)
        
        # Vérifier si le partage est expiré
        if cv_share.is_expired():
            raise Http404("Ce partage a expiré")
        
        # Vérifier le mot de passe si nécessaire
        if cv_share.share_type == 'password':
            password = request.GET.get('password', '')
            if password != cv_share.password:
                return render(request, 'cv_builder/password_required.html', {
                    'cv_share': cv_share
                })
        
        # Incrémenter le compteur de vues
        cv_share.view_count += 1
        cv_share.save()
        
        # Créer une entrée d'analytics
        analytics, created = CVAnalytics.objects.get_or_create(
            cv=cv_share.cv,
            date=timezone.now().date(),
            defaults={'views': 1}
        )
        if not created:
            analytics.views += 1
            analytics.save()
        
        context = {
            'cv': cv_share.cv,
            'cv_share': cv_share,
        }
        
        return render(request, f'cv_builder/templates/{cv_share.cv.template.name.lower()}.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de l\'affichage du CV: {e}")
        return redirect('home')


@login_required
def my_cvs(request):
    """Liste des CVs de l'utilisateur"""
    try:
        cvs = CV.objects.filter(user=request.user).order_by('-last_modified')
        
        # Filtres
        status = request.GET.get('status', '')
        if status:
            cvs = cvs.filter(status=status)
        
        # Pagination
        paginator = Paginator(cvs, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'status': status,
        }
        
        return render(request, 'cv_builder/my_cvs.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement de vos CVs: {e}")
        return redirect('cv_builder:dashboard')


@login_required
def delete_cv(request, cv_id):
    """Supprimer un CV"""
    try:
        cv = get_object_or_404(CV, id=cv_id, user=request.user)
        
        if request.method == 'POST':
            cv.delete()
            messages.success(request, 'CV supprimé avec succès !')
            return redirect('cv_builder:my_cvs')
        
        context = {
            'cv': cv,
        }
        
        return render(request, 'cv_builder/delete_cv.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression: {e}")
        return redirect('cv_builder:my_cvs')


@login_required
def share_cv(request, cv_id):
    """Partager un CV"""
    try:
        cv = get_object_or_404(CV, id=cv_id, user=request.user)
        
        if request.method == 'POST':
            form = CVShareForm(request.POST)
            if form.is_valid():
                share = form.save(commit=False)
                share.cv = cv
                share.share_url = str(uuid.uuid4())
                share.save()
                
                messages.success(request, 'CV partagé avec succès !')
                return redirect('cv_builder:share_cv', cv_id=cv.id)
        else:
            form = CVShareForm()
        
        # Partages existants
        existing_shares = CVShare.objects.filter(cv=cv).order_by('-created_at')
        
        context = {
            'cv': cv,
            'form': form,
            'existing_shares': existing_shares,
        }
        
        return render(request, 'cv_builder/share_cv.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du partage: {e}")
        return redirect('cv_builder:my_cvs')


@login_required
def download_cv(request, cv_id, format='pdf'):
    """Télécharger un CV"""
    try:
        cv = get_object_or_404(CV, id=cv_id, user=request.user)
        
        # Créer l'export
        export = CVExport.objects.create(
            cv=cv,
            export_format=format,
            file_path=f"exports/cv_{cv.id}_{uuid.uuid4().hex}.{format}",
            file_size=0  # Sera mis à jour après génération
        )
        
        # Incrémenter le compteur de téléchargements
        cv.download_count += 1
        cv.save()
        
        # Créer une entrée d'analytics
        analytics, created = CVAnalytics.objects.get_or_create(
            cv=cv,
            date=timezone.now().date(),
            defaults={'downloads': 1}
        )
        if not created:
            analytics.downloads += 1
            analytics.save()
        
        # Ici, vous généreriez le fichier selon le format
        # Pour l'instant, on simule
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{cv.title}.pdf"'
        response.write(b'PDF content would be here')
        
        return response
        
    except Exception as e:
        messages.error(request, f"Erreur lors du téléchargement: {e}")
        return redirect('cv_builder:my_cvs')


@login_required
def cv_analytics(request, cv_id):
    """Analytics d'un CV"""
    try:
        cv = get_object_or_404(CV, id=cv_id, user=request.user)
        
        # Statistiques générales
        total_views = CVAnalytics.objects.filter(cv=cv).aggregate(
            total_views=models.Sum('views')
        )['total_views'] or 0
        
        total_downloads = CVAnalytics.objects.filter(cv=cv).aggregate(
            total_downloads=models.Sum('downloads')
        )['total_downloads'] or 0
        
        # Statistiques par jour (30 derniers jours)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_stats = CVAnalytics.objects.filter(
            cv=cv,
            date__gte=thirty_days_ago
        ).order_by('date')
        
        # Partages
        shares = CVShare.objects.filter(cv=cv).order_by('-created_at')
        
        context = {
            'cv': cv,
            'total_views': total_views,
            'total_downloads': total_downloads,
            'daily_stats': daily_stats,
            'shares': shares,
        }
        
        return render(request, 'cv_builder/cv_analytics.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des analytics: {e}")
        return redirect('cv_builder:my_cvs')


@login_required
def cv_settings(request):
    """Paramètres du constructeur de CV"""
    try:
        settings, created = CVBuilderSettings.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            form = CVBuilderSettingsForm(request.POST, instance=settings)
            if form.is_valid():
                form.save()
                messages.success(request, 'Paramètres mis à jour avec succès !')
                return redirect('cv_builder:cv_settings')
        else:
            form = CVBuilderSettingsForm(instance=settings)
        
        context = {
            'form': form,
            'settings': settings,
        }
        
        return render(request, 'cv_builder/cv_settings.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des paramètres: {e}")
        return redirect('cv_builder:dashboard')


# API Views pour AJAX
@login_required
@require_http_methods(["POST"])
def save_cv_section(request, cv_id):
    """Sauvegarder une section de CV via AJAX"""
    try:
        cv = get_object_or_404(CV, id=cv_id, user=request.user)
        
        section = request.POST.get('section')
        data = json.loads(request.POST.get('data', '{}'))
        
        if section == 'personal_info':
            cv.personal_info = data
        elif section == 'experience':
            cv.experience = data
        elif section == 'education':
            cv.education = data
        elif section == 'skills':
            cv.skills = data
        elif section == 'projects':
            cv.projects = data
        elif section == 'languages':
            cv.languages = data
        elif section == 'certifications':
            cv.certifications = data
        elif section == 'references':
            cv.references = data
        
        cv.save()
        
        return JsonResponse({'success': True, 'message': 'Section sauvegardée'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def duplicate_cv(request, cv_id):
    """Dupliquer un CV"""
    try:
        original_cv = get_object_or_404(CV, id=cv_id, user=request.user)
        
        # Créer une copie
        new_cv = CV.objects.create(
            user=request.user,
            template=original_cv.template,
            title=f"{original_cv.title} (Copie)",
            status='draft',
            personal_info=original_cv.personal_info,
            professional_summary=original_cv.professional_summary,
            experience=original_cv.experience,
            education=original_cv.education,
            skills=original_cv.skills,
            projects=original_cv.projects,
            languages=original_cv.languages,
            certifications=original_cv.certifications,
            references=original_cv.references,
            custom_colors=original_cv.custom_colors,
            custom_fonts=original_cv.custom_fonts,
            layout_settings=original_cv.layout_settings
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'CV dupliqué avec succès',
            'new_cv_id': new_cv.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def change_cv_template(request, cv_id):
    """Changer le modèle d'un CV"""
    try:
        cv = get_object_or_404(CV, id=cv_id, user=request.user)
        template_id = request.POST.get('template_id')
        
        template = get_object_or_404(CVTemplate, id=template_id, is_active=True)
        cv.template = template
        cv.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Modèle changé avec succès'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})