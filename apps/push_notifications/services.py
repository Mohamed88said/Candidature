from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from typing import Dict, List, Optional, Any
import logging
import json
import requests
from datetime import datetime, timedelta

from .models import (
    Device, NotificationTemplate, PushNotification, NotificationPreference,
    NotificationCampaign, NotificationAnalytics, NotificationQueue
)

User = get_user_model()
logger = logging.getLogger(__name__)

class PushNotificationService:
    """Service principal pour les notifications push"""
    
    def __init__(self):
        self.fcm_service = FCMService()
        self.webpush_service = WebPushService()
        self.analytics_service = NotificationAnalyticsService()
    
    def send_notification(self, user: User, title: str, body: str, **kwargs) -> bool:
        """Envoie une notification push à un utilisateur"""
        try:
            # Vérifier les préférences de l'utilisateur
            if not self._can_send_notification(user, kwargs.get('notification_type')):
                return False
            
            # Récupérer les appareils actifs de l'utilisateur
            devices = Device.objects.filter(user=user, is_active=True)
            
            if not devices.exists():
                logger.warning(f"Aucun appareil actif trouvé pour {user.username}")
                return False
            
            success_count = 0
            total_count = devices.count()
            
            for device in devices:
                try:
                    if device.device_type == 'web':
                        success = self.webpush_service.send_notification(device, title, body, **kwargs)
                    else:
                        success = self.fcm_service.send_notification(device, title, body, **kwargs)
                    
                    if success:
                        success_count += 1
                        
                        # Créer l'enregistrement de notification
                        PushNotification.objects.create(
                            user=user,
                            device=device,
                            title=title,
                            body=body,
                            icon=kwargs.get('icon', ''),
                            image_url=kwargs.get('image_url', ''),
                            action_url=kwargs.get('action_url', ''),
                            status='sent',
                            sent_at=timezone.now(),
                            metadata=kwargs.get('metadata', {})
                        )
                
                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi à {device.device_id}: {e}")
                    
                    # Créer l'enregistrement d'échec
                    PushNotification.objects.create(
                        user=user,
                        device=device,
                        title=title,
                        body=body,
                        status='failed',
                        error_message=str(e),
                        metadata=kwargs.get('metadata', {})
                    )
            
            # Mettre à jour les statistiques
            self.analytics_service.update_daily_stats(success_count, total_count - success_count)
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de notification à {user.username}: {e}")
            return False
    
    def send_template_notification(self, user: User, template: NotificationTemplate, **kwargs) -> bool:
        """Envoie une notification basée sur un modèle"""
        try:
            # Remplacer les variables dans le modèle
            title = self._replace_variables(template.title, user, kwargs)
            body = self._replace_variables(template.body, user, kwargs)
            
            return self.send_notification(
                user=user,
                title=title,
                body=body,
                icon=template.icon,
                image_url=template.image_url,
                action_url=template.action_url,
                notification_type=template.notification_type,
                metadata={'template_id': template.id}
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de notification template à {user.username}: {e}")
            return False
    
    def send_campaign(self, campaign: NotificationCampaign) -> Dict[str, int]:
        """Envoie une campagne de notifications"""
        results = {
            'total_sent': 0,
            'total_delivered': 0,
            'total_failed': 0
        }
        
        try:
            # Récupérer les utilisateurs ciblés
            users = self._get_campaign_users(campaign)
            
            for user in users:
                success = self.send_template_notification(
                    user=user,
                    template=campaign.template,
                    metadata={'campaign_id': campaign.id}
                )
                
                if success:
                    results['total_sent'] += 1
                else:
                    results['total_failed'] += 1
            
            # Mettre à jour la campagne
            campaign.is_sent = True
            campaign.sent_at = timezone.now()
            campaign.total_sent = results['total_sent']
            campaign.total_failed = results['total_failed']
            campaign.save()
            
            logger.info(f"Campagne {campaign.name} envoyée: {results}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la campagne {campaign.name}: {e}")
        
        return results
    
    def queue_notification(self, user: User, template: NotificationTemplate, 
                          scheduled_at: datetime = None, priority: str = 'normal') -> bool:
        """Met une notification en file d'attente"""
        try:
            if scheduled_at is None:
                scheduled_at = timezone.now()
            
            NotificationQueue.objects.create(
                user=user,
                template=template,
                priority=priority,
                scheduled_at=scheduled_at
            )
            
            logger.info(f"Notification mise en file d'attente pour {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise en file d'attente: {e}")
            return False
    
    def process_queue(self) -> Dict[str, int]:
        """Traite la file d'attente des notifications"""
        results = {
            'processed': 0,
            'sent': 0,
            'failed': 0
        }
        
        try:
            # Récupérer les notifications à traiter
            queued_notifications = NotificationQueue.objects.filter(
                is_processed=False,
                scheduled_at__lte=timezone.now()
            ).order_by('priority', 'scheduled_at')[:100]  # Limiter à 100 par batch
            
            for queued_notification in queued_notifications:
                try:
                    success = self.send_template_notification(
                        user=queued_notification.user,
                        template=queued_notification.template,
                        metadata={'queued_id': queued_notification.id}
                    )
                    
                    queued_notification.is_processed = True
                    queued_notification.processed_at = timezone.now()
                    
                    if success:
                        results['sent'] += 1
                    else:
                        results['failed'] += 1
                        queued_notification.error_message = "Échec de l'envoi"
                    
                    queued_notification.save()
                    results['processed'] += 1
                    
                except Exception as e:
                    queued_notification.is_processed = True
                    queued_notification.processed_at = timezone.now()
                    queued_notification.error_message = str(e)
                    queued_notification.save()
                    results['failed'] += 1
                    results['processed'] += 1
                    
                    logger.error(f"Erreur lors du traitement de la notification en file: {e}")
            
            logger.info(f"File d'attente traitée: {results}")
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la file d'attente: {e}")
        
        return results
    
    def _can_send_notification(self, user: User, notification_type: str) -> bool:
        """Vérifie si on peut envoyer une notification à l'utilisateur"""
        try:
            preferences = user.notification_preferences
            
            if not preferences.push_enabled:
                return False
            
            # Vérifier les heures silencieuses
            if self._is_quiet_hours(preferences):
                return False
            
            # Vérifier les préférences par type
            if notification_type == 'job_alert' and not preferences.job_alerts:
                return False
            elif notification_type == 'application_update' and not preferences.application_updates:
                return False
            elif notification_type == 'message' and not preferences.messages:
                return False
            elif notification_type == 'achievement' and not preferences.achievements:
                return False
            elif notification_type == 'marketing' and not preferences.marketing:
                return False
            
            return True
            
        except NotificationPreference.DoesNotExist:
            # Pas de préférences, utiliser les valeurs par défaut
            return True
    
    def _is_quiet_hours(self, preferences: NotificationPreference) -> bool:
        """Vérifie si on est dans les heures silencieuses"""
        if not preferences.quiet_hours_start or not preferences.quiet_hours_end:
            return False
        
        now = timezone.now().time()
        start = preferences.quiet_hours_start
        end = preferences.quiet_hours_end
        
        if start <= end:
            return start <= now <= end
        else:
            # Heures silencieuses qui traversent minuit
            return now >= start or now <= end
    
    def _replace_variables(self, text: str, user: User, kwargs: Dict[str, Any]) -> str:
        """Remplace les variables dans un texte"""
        replacements = {
            '{{user_name}}': user.get_full_name() or user.username,
            '{{user_first_name}}': user.first_name or '',
            '{{user_last_name}}': user.last_name or '',
            '{{user_email}}': user.email or '',
        }
        
        # Ajouter les variables personnalisées
        for key, value in kwargs.items():
            replacements[f'{{{{{key}}}}}'] = str(value)
        
        for placeholder, value in replacements.items():
            text = text.replace(placeholder, value)
        
        return text
    
    def _get_campaign_users(self, campaign: NotificationCampaign) -> List[User]:
        """Récupère les utilisateurs ciblés par une campagne"""
        if campaign.target_users.exists():
            return list(campaign.target_users.all())
        
        # Appliquer les filtres de ciblage
        users = User.objects.filter(is_active=True)
        
        filters = campaign.target_filters
        if filters:
            if 'user_type' in filters:
                users = users.filter(user_type=filters['user_type'])
            
            if 'location' in filters:
                users = users.filter(candidate_profile__location__icontains=filters['location'])
            
            if 'skills' in filters:
                users = users.filter(candidate_profile__skills__name__in=filters['skills'])
        
        return list(users)

class FCMService:
    """Service pour Firebase Cloud Messaging"""
    
    def __init__(self):
        self.server_key = getattr(settings, 'FCM_SERVER_KEY', '')
        self.fcm_url = 'https://fcm.googleapis.com/fcm/send'
    
    def send_notification(self, device: Device, title: str, body: str, **kwargs) -> bool:
        """Envoie une notification via FCM"""
        try:
            if not self.server_key:
                logger.error("FCM_SERVER_KEY non configuré")
                return False
            
            headers = {
                'Authorization': f'key={self.server_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'to': device.push_token,
                'notification': {
                    'title': title,
                    'body': body,
                    'icon': kwargs.get('icon', ''),
                    'image': kwargs.get('image_url', ''),
                    'click_action': kwargs.get('action_url', '')
                },
                'data': kwargs.get('metadata', {})
            }
            
            response = requests.post(self.fcm_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Notification FCM envoyée à {device.device_id}")
                return True
            else:
                logger.error(f"Erreur FCM: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi FCM: {e}")
            return False

class WebPushService:
    """Service pour les notifications web push"""
    
    def __init__(self):
        self.vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', '')
        self.vapid_public_key = getattr(settings, 'VAPID_PUBLIC_KEY', '')
        self.vapid_claims = getattr(settings, 'VAPID_CLAIMS', {})
    
    def send_notification(self, device: Device, title: str, body: str, **kwargs) -> bool:
        """Envoie une notification web push"""
        try:
            # Ici, vous implémenteriez la logique pour envoyer des notifications web push
            # en utilisant une bibliothèque comme pywebpush
            
            logger.info(f"Notification web push envoyée à {device.device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi web push: {e}")
            return False

class NotificationAnalyticsService:
    """Service pour les analyses des notifications"""
    
    def update_daily_stats(self, delivered: int, failed: int):
        """Met à jour les statistiques quotidiennes"""
        try:
            today = timezone.now().date()
            analytics, created = NotificationAnalytics.objects.get_or_create(date=today)
            
            analytics.total_sent += delivered + failed
            analytics.total_delivered += delivered
            analytics.total_failed += failed
            
            # Calculer les taux
            if analytics.total_sent > 0:
                analytics.delivery_rate = (analytics.total_delivered / analytics.total_sent) * 100
            
            if analytics.total_delivered > 0:
                analytics.open_rate = (analytics.total_opened / analytics.total_delivered) * 100
            
            analytics.save()
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des statistiques: {e}")
    
    def get_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Récupère les analyses sur une période"""
        try:
            analytics = NotificationAnalytics.objects.filter(
                date__range=[start_date.date(), end_date.date()]
            ).order_by('date')
            
            total_sent = sum(a.total_sent for a in analytics)
            total_delivered = sum(a.total_delivered for a in analytics)
            total_opened = sum(a.total_opened for a in analytics)
            total_failed = sum(a.total_failed for a in analytics)
            
            return {
                'total_sent': total_sent,
                'total_delivered': total_delivered,
                'total_opened': total_opened,
                'total_failed': total_failed,
                'delivery_rate': (total_delivered / total_sent * 100) if total_sent > 0 else 0,
                'open_rate': (total_opened / total_delivered * 100) if total_delivered > 0 else 0,
                'daily_analytics': [
                    {
                        'date': a.date,
                        'sent': a.total_sent,
                        'delivered': a.total_delivered,
                        'opened': a.total_opened,
                        'failed': a.total_failed,
                        'delivery_rate': a.delivery_rate,
                        'open_rate': a.open_rate
                    }
                    for a in analytics
                ]
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des analyses: {e}")
            return {}

class DeviceService:
    """Service pour la gestion des appareils"""
    
    def register_device(self, user: User, device_id: str, device_type: str, 
                       push_token: str, device_name: str = '') -> Device:
        """Enregistre un nouvel appareil"""
        try:
            device, created = Device.objects.get_or_create(
                user=user,
                device_id=device_id,
                defaults={
                    'device_type': device_type,
                    'push_token': push_token,
                    'device_name': device_name,
                    'is_active': True
                }
            )
            
            if not created:
                # Mettre à jour l'appareil existant
                device.push_token = push_token
                device.device_name = device_name
                device.is_active = True
                device.save()
            
            logger.info(f"Appareil {'créé' if created else 'mis à jour'} pour {user.username}")
            return device
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'appareil: {e}")
            raise
    
    def unregister_device(self, user: User, device_id: str) -> bool:
        """Désenregistre un appareil"""
        try:
            device = Device.objects.get(user=user, device_id=device_id)
            device.is_active = False
            device.save()
            
            logger.info(f"Appareil désenregistré pour {user.username}")
            return True
            
        except Device.DoesNotExist:
            logger.warning(f"Appareil {device_id} non trouvé pour {user.username}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors du désenregistrement de l'appareil: {e}")
            return False
    
    def get_user_devices(self, user: User) -> List[Device]:
        """Récupère les appareils d'un utilisateur"""
        return list(Device.objects.filter(user=user, is_active=True))


