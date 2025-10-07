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
from datetime import datetime, timedelta

from .models import (
    AlertPreference, AlertType, AlertNotification, AlertTemplate, 
    AlertCampaign, AlertAnalytics, AlertSubscription
)
from .forms import (
    AlertPreferenceForm, AlertTypeForm, AlertTemplateForm, AlertCampaignForm,
    AlertSubscriptionForm, AlertSearchForm, AlertSettingsForm, AlertFeedbackForm,
    BulkAlertActionForm
)
from apps.jobs.models import Job
from apps.matching.services import IntelligentMatchingService


@login_required
def alerts_dashboard(request):
    """Dashboard principal des alertes"""
    try:
        # Statistiques générales
        total_alerts = AlertNotification.objects.filter(user=request.user).count()
        unread_alerts = AlertNotification.objects.filter(user=request.user, status='delivered').count()
        clicked_alerts = AlertNotification.objects.filter(user=request.user, status='clicked').count()
        
        # Alertes récentes
        recent_alerts = AlertNotification.objects.filter(user=request.user).order_by('-created_at')[:5]
        
        # Types d'alertes les plus actifs
        active_alert_types = AlertType.objects.filter(
            is_active=True,
            alert_notifications__user=request.user
        ).annotate(
            alert_count=Count('alert_notifications')
        ).order_by('-alert_count')[:5]
        
        # Préférences d'alertes
        preferences, created = AlertPreference.objects.get_or_create(user=request.user)
        
        # Statistiques de la semaine
        week_ago = timezone.now() - timedelta(days=7)
        weekly_stats = {
            'alerts_received': AlertNotification.objects.filter(
                user=request.user,
                created_at__gte=week_ago
            ).count(),
            'alerts_clicked': AlertNotification.objects.filter(
                user=request.user,
                clicked_at__gte=week_ago
            ).count(),
            'avg_match_score': AlertNotification.objects.filter(
                user=request.user,
                created_at__gte=week_ago
            ).aggregate(avg_score=Avg('match_score'))['avg_score'] or 0
        }
        
        context = {
            'total_alerts': total_alerts,
            'unread_alerts': unread_alerts,
            'clicked_alerts': clicked_alerts,
            'recent_alerts': recent_alerts,
            'active_alert_types': active_alert_types,
            'preferences': preferences,
            'weekly_stats': weekly_stats,
        }
        
        return render(request, 'alerts/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du dashboard: {e}")
        return redirect('home')


@login_required
def alerts_list(request):
    """Liste de toutes les alertes de l'utilisateur"""
    try:
        alerts = AlertNotification.objects.filter(user=request.user).select_related('job', 'alert_type').order_by('-created_at')
        
        # Filtres
        search_query = request.GET.get('search', '')
        alert_type_id = request.GET.get('alert_type', '')
        status = request.GET.get('status', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        if search_query:
            alerts = alerts.filter(
                Q(title__icontains=search_query) |
                Q(message__icontains=search_query) |
                Q(job__title__icontains=search_query) |
                Q(job__company__icontains=search_query)
            )
        
        if alert_type_id:
            alerts = alerts.filter(alert_type_id=alert_type_id)
        
        if status:
            if status == 'unread':
                alerts = alerts.filter(status='delivered')
            elif status == 'read':
                alerts = alerts.filter(status='opened')
            elif status == 'clicked':
                alerts = alerts.filter(status='clicked')
            elif status == 'today':
                today = timezone.now().date()
                alerts = alerts.filter(created_at__date=today)
            elif status == 'week':
                week_ago = timezone.now() - timedelta(days=7)
                alerts = alerts.filter(created_at__gte=week_ago)
            elif status == 'month':
                month_ago = timezone.now() - timedelta(days=30)
                alerts = alerts.filter(created_at__gte=month_ago)
        
        if date_from:
            alerts = alerts.filter(created_at__date__gte=date_from)
        
        if date_to:
            alerts = alerts.filter(created_at__date__lte=date_to)
        
        # Pagination
        paginator = Paginator(alerts, 25)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Formulaires
        search_form = AlertSearchForm(request.GET)
        
        context = {
            'page_obj': page_obj,
            'search_form': search_form,
            'search_query': search_query,
            'alert_type_id': alert_type_id,
            'status': status,
            'date_from': date_from,
            'date_to': date_to,
        }
        
        return render(request, 'alerts/alerts_list.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des alertes: {e}")
        return redirect('alerts:dashboard')


@login_required
def alert_detail(request, alert_id):
    """Détail d'une alerte"""
    try:
        alert = get_object_or_404(AlertNotification, id=alert_id, user=request.user)
        
        # Marquer comme ouverte si ce n'est pas déjà fait
        if alert.status == 'delivered':
            alert.mark_as_opened()
        
        # Récupérer les alertes similaires
        similar_alerts = AlertNotification.objects.filter(
            user=request.user,
            job__category=alert.job.category,
            alert_type=alert.alert_type
        ).exclude(id=alert.id).order_by('-match_score')[:3]
        
        context = {
            'alert': alert,
            'similar_alerts': similar_alerts,
        }
        
        return render(request, 'alerts/alert_detail.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement de l'alerte: {e}")
        return redirect('alerts:alerts_list')


@login_required
def alert_preferences(request):
    """Gestion des préférences d'alertes"""
    try:
        preferences, created = AlertPreference.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            form = AlertPreferenceForm(request.POST, instance=preferences)
            if form.is_valid():
                form.save()
                messages.success(request, 'Préférences d\'alertes sauvegardées avec succès.')
                return redirect('alerts:preferences')
        else:
            form = AlertPreferenceForm(instance=preferences)
        
        # Types d'alertes disponibles
        alert_types = AlertType.objects.filter(is_active=True)
        
        context = {
            'form': form,
            'preferences': preferences,
            'alert_types': alert_types,
        }
        
        return render(request, 'alerts/preferences.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des préférences: {e}")
        return redirect('alerts:dashboard')


@login_required
def alert_subscriptions(request):
    """Gestion des abonnements d'alertes"""
    try:
        subscriptions = AlertSubscription.objects.filter(user=request.user).order_by('-created_at')
        
        if request.method == 'POST':
            form = AlertSubscriptionForm(request.POST)
            if form.is_valid():
                subscription = form.save(commit=False)
                subscription.user = request.user
                subscription.save()
                messages.success(request, 'Abonnement créé avec succès.')
                return redirect('alerts:subscriptions')
        else:
            form = AlertSubscriptionForm()
        
        context = {
            'subscriptions': subscriptions,
            'form': form,
        }
        
        return render(request, 'alerts/subscriptions.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des abonnements: {e}")
        return redirect('alerts:dashboard')


@login_required
@require_http_methods(["POST"])
def mark_alert_read(request, alert_id):
    """Marquer une alerte comme lue"""
    try:
        alert = get_object_or_404(AlertNotification, id=alert_id, user=request.user)
        alert.mark_as_opened()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def mark_alert_clicked(request, alert_id):
    """Marquer une alerte comme cliquée"""
    try:
        alert = get_object_or_404(AlertNotification, id=alert_id, user=request.user)
        alert.mark_as_clicked()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def submit_alert_feedback(request, alert_id):
    """Soumettre des commentaires sur une alerte"""
    try:
        alert = get_object_or_404(AlertNotification, id=alert_id, user=request.user)
        
        form = AlertFeedbackForm(request.POST)
        if form.is_valid():
            # Traiter les commentaires
            rating = form.cleaned_data['rating']
            feedback = form.cleaned_data['feedback']
            reason = form.cleaned_data['reason']
            
            # Sauvegarder les commentaires (vous pouvez créer un modèle pour cela)
            # AlertFeedback.objects.create(
            #     alert=alert,
            #     user=request.user,
            #     rating=rating,
            #     feedback=feedback,
            #     reason=reason
            # )
            
            messages.success(request, 'Merci pour vos commentaires !')
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Données invalides', 'errors': form.errors}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def bulk_alert_action(request):
    """Action en lot sur les alertes"""
    try:
        form = BulkAlertActionForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            alert_ids = form.cleaned_data['alert_ids']
            
            alerts = JobAlert.objects.filter(id__in=alert_ids, user=request.user)
            
            if action == 'mark_read':
                for alert in alerts:
                    alert.mark_as_opened()
                messages.success(request, f'{alerts.count()} alertes marquées comme lues.')
            elif action == 'mark_unread':
                alerts.update(status='delivered', opened_at=None)
                messages.success(request, f'{alerts.count()} alertes marquées comme non lues.')
            elif action == 'delete':
                count = alerts.count()
                alerts.delete()
                messages.success(request, f'{count} alertes supprimées.')
            elif action == 'archive':
                # Implémenter l'archivage si nécessaire
                messages.success(request, f'{alerts.count()} alertes archivées.')
            
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Données invalides', 'errors': form.errors}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def alert_analytics(request):
    """Analytics des alertes (admin)"""
    if not request.user.is_staff:
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        # Statistiques générales
        total_alerts = AlertNotification.objects.count()
        total_delivered = AlertNotification.objects.filter(status__in=['delivered', 'opened', 'clicked']).count()
        total_opened = AlertNotification.objects.filter(status__in=['opened', 'clicked']).count()
        total_clicked = AlertNotification.objects.filter(status='clicked').count()
        
        # Taux de conversion
        delivery_rate = (total_delivered / total_alerts * 100) if total_alerts > 0 else 0
        open_rate = (total_opened / total_delivered * 100) if total_delivered > 0 else 0
        click_rate = (total_clicked / total_opened * 100) if total_opened > 0 else 0
        
        # Alertes par type
        alerts_by_type = AlertType.objects.annotate(
            alert_count=Count('alert_notifications')
        ).order_by('-alert_count')
        
        # Alertes par jour (30 derniers jours)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_alerts = AlertNotification.objects.filter(
            created_at__gte=thirty_days_ago
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # Top des offres les plus alertées
        top_jobs = Job.objects.annotate(
            alert_count=Count('alerts')
        ).order_by('-alert_count')[:10]
        
        context = {
            'total_alerts': total_alerts,
            'total_delivered': total_delivered,
            'total_opened': total_opened,
            'total_clicked': total_clicked,
            'delivery_rate': delivery_rate,
            'open_rate': open_rate,
            'click_rate': click_rate,
            'alerts_by_type': alerts_by_type,
            'daily_alerts': list(daily_alerts),
            'top_jobs': top_jobs,
        }
        
        return render(request, 'alerts/analytics.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des analytics: {e}")
        return redirect('alerts:dashboard')


# Services pour la génération d'alertes

class AlertGenerationService:
    """Service pour générer des alertes automatiques"""
    
    def __init__(self):
        self.matching_service = IntelligentMatchingService()
    
    def generate_job_alerts(self, job_id):
        """Générer des alertes pour une nouvelle offre d'emploi"""
        try:
            job = Job.objects.get(id=job_id)
            
            # Récupérer les utilisateurs avec des préférences d'alertes actives
            users_with_preferences = User.objects.filter(
                alert_preferences__isnull=False,
                alert_preferences__email_alerts=True
            ).select_related('candidate_profile')
            
            alerts_created = 0
            
            for user in users_with_preferences:
                # Vérifier si l'utilisateur correspond aux critères
                if self.should_send_alert(user, job):
                    # Calculer le score de correspondance
                    match_score = self.calculate_match_score(user, job)
                    
                    # Vérifier si le score est suffisant
                    if match_score >= 50:  # Seuil minimum
                        # Créer l'alerte
                        alert = self.create_job_alert(user, job, match_score)
                        if alert:
                            alerts_created += 1
            
            return alerts_created
            
        except Exception as e:
            print(f"Erreur lors de la génération d'alertes: {e}")
            return 0
    
    def should_send_alert(self, user, job):
        """Vérifier si une alerte doit être envoyée à un utilisateur"""
        try:
            preferences = user.alert_preferences
            
            # Vérifier la fréquence
            if preferences.frequency == 'never':
                return False
            
            # Vérifier le nombre maximum d'alertes par jour
            today = timezone.now().date()
            today_alerts = AlertNotification.objects.filter(
                user=user,
                created_at__date=today
            ).count()
            
            if today_alerts >= preferences.max_alerts_per_day:
                return False
            
            # Vérifier les critères géographiques
            if not self.check_location_criteria(user, job, preferences):
                return False
            
            # Vérifier les critères de salaire
            if not self.check_salary_criteria(job, preferences):
                return False
            
            # Vérifier les critères d'expérience
            if not self.check_experience_criteria(job, preferences):
                return False
            
            # Vérifier les types d'emploi
            if not self.check_job_type_criteria(job, preferences):
                return False
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la vérification des critères: {e}")
            return False
    
    def calculate_match_score(self, user, job):
        """Calculer le score de correspondance entre un utilisateur et une offre"""
        try:
            # Utiliser le service de matching intelligent
            match_result = self.matching_service.calculate_match_score(user, job)
            return match_result.get('total_score', 0)
            
        except Exception as e:
            print(f"Erreur lors du calcul du score: {e}")
            return 0
    
    def create_job_alert(self, user, job, match_score):
        """Créer une alerte d'emploi"""
        try:
            # Récupérer le type d'alerte par défaut
            alert_type = AlertType.objects.filter(is_active=True).first()
            if not alert_type:
                return None
            
            # Générer le titre et le message
            title = f"Nouvelle offre correspondant à votre profil : {job.title}"
            message = self.generate_alert_message(user, job, match_score)
            
            # Créer l'alerte
            alert = AlertNotification.objects.create(
                user=user,
                job=job,
                alert_type=alert_type,
                title=title,
                message=message,
                match_score=match_score,
                match_reasons=self.get_match_reasons(user, job)
            )
            
            return alert
            
        except Exception as e:
            print(f"Erreur lors de la création de l'alerte: {e}")
            return None
    
    def generate_alert_message(self, user, job, match_score):
        """Générer le message de l'alerte"""
        message = f"Une nouvelle offre d'emploi correspond à {match_score:.0f}% à votre profil :\n\n"
        message += f"📋 {job.title}\n"
        message += f"🏢 {job.company}\n"
        message += f"📍 {job.location}\n"
        
        if job.salary_min and job.salary_max:
            message += f"💰 {job.salary_min:,} - {job.salary_max:,} {job.currency}\n"
        
        message += f"\n🎯 Score de correspondance : {match_score:.0f}%\n"
        message += f"🔗 Voir l'offre : {job.get_absolute_url()}"
        
        return message
    
    def get_match_reasons(self, user, job):
        """Obtenir les raisons de correspondance"""
        reasons = []
        
        # Vérifier les compétences
        if hasattr(user, 'candidate_profile'):
            user_skills = user.candidate_profile.skills.all()
            job_skills = job.required_skills.all()
            
            common_skills = user_skills.intersection(job_skills)
            if common_skills:
                reasons.append(f"Compétences communes : {', '.join([s.name for s in common_skills[:3]])}")
        
        # Vérifier l'expérience
        if hasattr(user, 'candidate_profile'):
            user_experience = user.candidate_profile.get_years_of_experience()
            if user_experience >= job.experience_level:
                reasons.append(f"Expérience suffisante ({user_experience} ans)")
        
        # Vérifier la localisation
        if job.location in user.alert_preferences.preferred_locations:
            reasons.append(f"Localisation préférée : {job.location}")
        
        return reasons
    
    def check_location_criteria(self, user, job, preferences):
        """Vérifier les critères de localisation"""
        if not preferences.preferred_locations:
            return True
        
        return job.location in preferences.preferred_locations
    
    def check_salary_criteria(self, job, preferences):
        """Vérifier les critères de salaire"""
        if not preferences.include_salary:
            return True
        
        if not job.salary_min:
            return True
        
        if preferences.min_salary and job.salary_max and job.salary_max < preferences.min_salary:
            return False
        
        if preferences.max_salary and job.salary_min and job.salary_min > preferences.max_salary:
            return False
        
        return True
    
    def check_experience_criteria(self, job, preferences):
        """Vérifier les critères d'expérience"""
        if preferences.min_experience and job.experience_level < preferences.min_experience:
            return False
        
        if preferences.max_experience and job.experience_level > preferences.max_experience:
            return False
        
        return True
    
    def check_job_type_criteria(self, job, preferences):
        """Vérifier les critères de type d'emploi"""
        if not preferences.preferred_job_types:
            return True
        
        return job.job_type in preferences.preferred_job_types