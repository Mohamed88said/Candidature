from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import (
    Device, NotificationTemplate, PushNotification, NotificationPreference,
    NotificationCampaign, NotificationAnalytics, NotificationQueue
)
from .services import PushNotificationService, DeviceService
from .forms import (
    NotificationPreferenceForm, DeviceForm, NotificationTemplateForm,
    NotificationCampaignForm
)

def is_staff_or_superuser(user):
    return user.is_staff or user.is_superuser

@login_required
def notifications_dashboard(request):
    """Dashboard principal des notifications"""
    try:
        user = request.user
        
        # Statistiques générales
        total_notifications = PushNotification.objects.filter(user=user).count()
        unread_notifications = PushNotification.objects.filter(
            user=user,
            status__in=['sent', 'delivered']
        ).count()
        read_notifications = PushNotification.objects.filter(
            user=user,
            status='opened'
        ).count()
        
        # Notifications récentes
        recent_notifications = PushNotification.objects.filter(
            user=user
        ).order_by('-created_at')[:5]
        
        # Appareils enregistrés
        devices = Device.objects.filter(user=user, is_active=True)
        
        # Préférences
        preferences, created = NotificationPreference.objects.get_or_create(user=user)
        
        # Statistiques de la semaine
        week_ago = timezone.now() - timedelta(days=7)
        weekly_stats = {
            'notifications_received': PushNotification.objects.filter(
                user=user,
                created_at__gte=week_ago
            ).count(),
            'notifications_read': PushNotification.objects.filter(
                user=user,
                opened_at__gte=week_ago
            ).count(),
            'delivery_rate': _calculate_delivery_rate(user, week_ago),
        }
        
        context = {
            'total_notifications': total_notifications,
            'unread_notifications': unread_notifications,
            'read_notifications': read_notifications,
            'recent_notifications': recent_notifications,
            'devices': devices,
            'preferences': preferences,
            'weekly_stats': weekly_stats,
        }
        
        return render(request, 'push_notifications/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du dashboard: {e}")
        return redirect('home')

@login_required
def manage_preferences(request):
    """Gérer les préférences de notifications"""
    try:
        preferences, created = NotificationPreference.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            form = NotificationPreferenceForm(request.POST, instance=preferences)
            if form.is_valid():
                form.save()
                messages.success(request, 'Vos préférences de notifications ont été mises à jour.')
                return redirect('push_notifications:manage_preferences')
        else:
            form = NotificationPreferenceForm(instance=preferences)
        
        context = {
            'form': form,
            'preferences': preferences,
        }
        
        return render(request, 'push_notifications/preferences.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la gestion des préférences: {e}")
        return redirect('push_notifications:dashboard')

@login_required
def devices_list(request):
    """Liste des appareils enregistrés"""
    try:
        devices = Device.objects.filter(user=request.user).order_by('-last_seen')
        
        context = {
            'devices': devices,
        }
        
        return render(request, 'push_notifications/devices_list.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des appareils: {e}")
        return redirect('push_notifications:dashboard')

@login_required
def register_device(request):
    """Enregistrer un nouvel appareil"""
    try:
        if request.method == 'POST':
            form = DeviceForm(request.POST)
            if form.is_valid():
                device_service = DeviceService()
                device = device_service.register_device(
                    user=request.user,
                    device_id=form.cleaned_data['device_id'],
                    device_type=form.cleaned_data['device_type'],
                    push_token=form.cleaned_data['push_token'],
                    device_name=form.cleaned_data['device_name']
                )
                messages.success(request, 'Appareil enregistré avec succès.')
                return redirect('push_notifications:devices_list')
        else:
            form = DeviceForm()
        
        context = {
            'form': form,
        }
        
        return render(request, 'push_notifications/register_device.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de l'enregistrement de l'appareil: {e}")
        return redirect('push_notifications:devices_list')

@login_required
def unregister_device(request, device_id):
    """Désenregistrer un appareil"""
    try:
        device = get_object_or_404(Device, id=device_id, user=request.user)
        
        if request.method == 'POST':
            device_service = DeviceService()
            success = device_service.unregister_device(request.user, device.device_id)
            
            if success:
                messages.success(request, 'Appareil désenregistré avec succès.')
            else:
                messages.error(request, 'Erreur lors du désenregistrement de l\'appareil.')
            
            return redirect('push_notifications:devices_list')
        
        context = {
            'device': device,
        }
        
        return render(request, 'push_notifications/unregister_device.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du désenregistrement de l'appareil: {e}")
        return redirect('push_notifications:devices_list')

@login_required
def notifications_list(request):
    """Liste des notifications"""
    try:
        notifications = PushNotification.objects.filter(user=request.user).order_by('-created_at')
        
        # Filtres
        status = request.GET.get('status', '')
        if status:
            notifications = notifications.filter(status=status)
        
        # Pagination
        paginator = Paginator(notifications, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'status': status,
        }
        
        return render(request, 'push_notifications/notifications_list.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des notifications: {e}")
        return redirect('push_notifications:dashboard')

@login_required
def notification_detail(request, notification_id):
    """Détail d'une notification"""
    try:
        notification = get_object_or_404(PushNotification, id=notification_id, user=request.user)
        
        # Marquer comme ouverte si ce n'est pas déjà fait
        if notification.status == 'delivered':
            notification.mark_as_opened()
        
        context = {
            'notification': notification,
        }
        
        return render(request, 'push_notifications/notification_detail.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement de la notification: {e}")
        return redirect('push_notifications:notifications_list')

@login_required
def mark_notification_read(request, notification_id):
    """Marquer une notification comme lue"""
    try:
        notification = get_object_or_404(PushNotification, id=notification_id, user=request.user)
        
        if notification.status in ['sent', 'delivered']:
            notification.mark_as_opened()
            messages.success(request, 'Notification marquée comme lue.')
        
        return redirect('push_notifications:notifications_list')
        
    except Exception as e:
        messages.error(request, f"Erreur lors du marquage de la notification: {e}")
        return redirect('push_notifications:notifications_list')

# --- Admin/Staff Views ---

@login_required
@user_passes_test(is_staff_or_superuser)
def campaigns_list(request):
    """Liste des campagnes de notifications (Admin)"""
    try:
        campaigns = NotificationCampaign.objects.all().order_by('-created_at')
        
        context = {
            'campaigns': campaigns,
        }
        
        return render(request, 'push_notifications/admin/campaigns_list.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des campagnes: {e}")
        return redirect('push_notifications:dashboard')

@login_required
@user_passes_test(is_staff_or_superuser)
def campaign_detail(request, campaign_id):
    """Détail d'une campagne (Admin)"""
    try:
        campaign = get_object_or_404(NotificationCampaign, id=campaign_id)
        
        context = {
            'campaign': campaign,
        }
        
        return render(request, 'push_notifications/admin/campaign_detail.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement de la campagne: {e}")
        return redirect('push_notifications:campaigns_list')

@login_required
@user_passes_test(is_staff_or_superuser)
def send_campaign(request, campaign_id):
    """Envoyer une campagne (Admin)"""
    try:
        campaign = get_object_or_404(NotificationCampaign, id=campaign_id)
        
        if request.method == 'POST':
            if campaign.is_sent:
                messages.error(request, 'Cette campagne a déjà été envoyée.')
                return redirect('push_notifications:campaign_detail', campaign_id=campaign.id)
            
            # Envoyer la campagne
            push_service = PushNotificationService()
            results = push_service.send_campaign(campaign)
            
            messages.success(request, f'Campagne envoyée: {results["total_sent"]} notifications envoyées.')
            return redirect('push_notifications:campaign_detail', campaign_id=campaign.id)
        
        context = {
            'campaign': campaign,
        }
        
        return render(request, 'push_notifications/admin/send_campaign.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de l'envoi de la campagne: {e}")
        return redirect('push_notifications:campaigns_list')

@login_required
@user_passes_test(is_staff_or_superuser)
def templates_list(request):
    """Liste des modèles de notifications (Admin)"""
    try:
        templates = NotificationTemplate.objects.all().order_by('notification_type', 'name')
        
        context = {
            'templates': templates,
        }
        
        return render(request, 'push_notifications/admin/templates_list.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des modèles: {e}")
        return redirect('push_notifications:dashboard')

@login_required
@user_passes_test(is_staff_or_superuser)
def template_detail(request, template_id):
    """Détail d'un modèle (Admin)"""
    try:
        template = get_object_or_404(NotificationTemplate, id=template_id)
        
        context = {
            'template': template,
        }
        
        return render(request, 'push_notifications/admin/template_detail.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du modèle: {e}")
        return redirect('push_notifications:templates_list')

@login_required
@user_passes_test(is_staff_or_superuser)
def analytics_dashboard(request):
    """Dashboard des analyses (Admin)"""
    try:
        # Statistiques générales
        total_notifications = PushNotification.objects.count()
        total_delivered = PushNotification.objects.filter(status__in=['delivered', 'opened']).count()
        total_opened = PushNotification.objects.filter(status='opened').count()
        total_failed = PushNotification.objects.filter(status='failed').count()
        
        # Taux de conversion
        delivery_rate = (total_delivered / total_notifications * 100) if total_notifications > 0 else 0
        open_rate = (total_opened / total_delivered * 100) if total_delivered > 0 else 0
        
        # Notifications par type
        notifications_by_type = NotificationTemplate.objects.annotate(
            notification_count=Count('notifications')
        ).order_by('-notification_count')
        
        # Notifications par jour (30 derniers jours)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_notifications = PushNotification.objects.filter(
            created_at__gte=thirty_days_ago
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # Top des utilisateurs
        top_users = PushNotification.objects.values('user__username').annotate(
            notification_count=Count('id')
        ).order_by('-notification_count')[:10]
        
        context = {
            'total_notifications': total_notifications,
            'total_delivered': total_delivered,
            'total_opened': total_opened,
            'total_failed': total_failed,
            'delivery_rate': delivery_rate,
            'open_rate': open_rate,
            'notifications_by_type': notifications_by_type,
            'daily_notifications': daily_notifications,
            'top_users': top_users,
        }
        
        return render(request, 'push_notifications/admin/analytics.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des analyses: {e}")
        return redirect('push_notifications:dashboard')

# --- API Views ---

@login_required
@require_http_methods(["POST"])
def register_device_api(request):
    """API pour enregistrer un appareil"""
    try:
        data = json.loads(request.body)
        
        device_service = DeviceService()
        device = device_service.register_device(
            user=request.user,
            device_id=data.get('device_id'),
            device_type=data.get('device_type'),
            push_token=data.get('push_token'),
            device_name=data.get('device_name', '')
        )
        
        return JsonResponse({
            'success': True,
            'device_id': device.id,
            'message': 'Appareil enregistré avec succès'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def unregister_device_api(request):
    """API pour désenregistrer un appareil"""
    try:
        data = json.loads(request.body)
        device_id = data.get('device_id')
        
        device_service = DeviceService()
        success = device_service.unregister_device(request.user, device_id)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Appareil désenregistré avec succès'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Appareil non trouvé'
            }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def send_notification_api(request):
    """API pour envoyer une notification"""
    try:
        data = json.loads(request.body)
        
        push_service = PushNotificationService()
        success = push_service.send_notification(
            user=request.user,
            title=data.get('title'),
            body=data.get('body'),
            icon=data.get('icon', ''),
            image_url=data.get('image_url', ''),
            action_url=data.get('action_url', ''),
            notification_type=data.get('notification_type', 'system'),
            metadata=data.get('metadata', {})
        )
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Notification envoyée avec succès'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Échec de l\'envoi de la notification'
            }, status=500)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def mark_notification_read_api(request):
    """API pour marquer une notification comme lue"""
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        
        notification = get_object_or_404(PushNotification, id=notification_id, user=request.user)
        
        if notification.status in ['sent', 'delivered']:
            notification.mark_as_opened()
            return JsonResponse({
                'success': True,
                'message': 'Notification marquée comme lue'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Notification déjà lue ou invalide'
            }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def update_preferences_api(request):
    """API pour mettre à jour les préférences"""
    try:
        data = json.loads(request.body)
        
        preferences, created = NotificationPreference.objects.get_or_create(user=request.user)
        
        # Mettre à jour les préférences
        for field, value in data.items():
            if hasattr(preferences, field):
                setattr(preferences, field, value)
        
        preferences.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Préférences mises à jour avec succès'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def _calculate_delivery_rate(user, since_date):
    """Calcule le taux de livraison pour un utilisateur"""
    try:
        total_sent = PushNotification.objects.filter(
            user=user,
            created_at__gte=since_date
        ).count()
        
        total_delivered = PushNotification.objects.filter(
            user=user,
            status__in=['delivered', 'opened'],
            created_at__gte=since_date
        ).count()
        
        return (total_delivered / total_sent * 100) if total_sent > 0 else 0
        
    except Exception:
        return 0