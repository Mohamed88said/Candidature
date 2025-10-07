from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import logging

from .tasks import generate_alerts_for_new_job
from apps.jobs.models import Job

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Job)
def generate_alerts_on_job_creation(sender, instance, created, **kwargs):
    """Déclencher la génération d'alertes quand une nouvelle offre est créée"""
    if created and instance.is_active:
        try:
            logger.info(f"Nouvelle offre créée: {instance.title} (ID: {instance.id})")
            
            # Déclencher la tâche Celery pour générer les alertes
            if settings.CELERY_TASK_ALWAYS_EAGER:
                # Mode synchrone pour les tests
                generate_alerts_for_new_job(instance.id)
            else:
                # Mode asynchrone pour la production
                generate_alerts_for_new_job.delay(instance.id)
                
        except Exception as e:
            logger.error(f"Erreur lors du déclenchement de la génération d'alertes pour l'offre {instance.id}: {e}")


@receiver(post_save, sender=Job)
def update_alerts_on_job_modification(sender, instance, created, **kwargs):
    """Mettre à jour les alertes existantes quand une offre est modifiée"""
    if not created and instance.is_active:
        try:
            from .models import AlertNotification, AlertType
            
            # Récupérer le type d'alerte "Offre mise à jour"
            update_alert_type = AlertType.objects.filter(
                name='Offre mise à jour',
                is_active=True
            ).first()
            
            if update_alert_type:
                # Récupérer les utilisateurs qui ont déjà reçu une alerte pour cette offre
                existing_alerts = AlertNotification.objects.filter(
                    job=instance,
                    alert_type__name='Nouvelle offre'
                ).select_related('user')
                
                for existing_alert in existing_alerts:
                    # Vérifier si l'utilisateur a activé les alertes de mise à jour
                    if (existing_alert.user.alert_preferences and 
                        update_alert_type in existing_alert.user.alert_preferences.enabled_alert_types.all()):
                        
                        # Créer une nouvelle alerte de mise à jour
                        AlertNotification.objects.create(
                            user=existing_alert.user,
                            job=instance,
                            alert_type=update_alert_type,
                            title=f"Offre mise à jour : {instance.title}",
                            message=f"L'offre '{instance.title}' que vous suivez a été mise à jour.\n\n"
                                   f"📋 {instance.title}\n"
                                   f"🏢 {instance.company}\n"
                                   f"📍 {instance.location}\n\n"
                                   f"🔗 Voir les modifications : {instance.get_absolute_url()}",
                            match_score=existing_alert.match_score,
                            match_reasons=existing_alert.match_reasons,
                            status='pending'
                        )
                        
                        logger.info(f"Alerte de mise à jour créée pour {existing_alert.user.email}")
                        
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des alertes pour l'offre {instance.id}: {e}")



