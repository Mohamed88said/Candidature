from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import AlertNotification, AlertPreference, AlertType
from .services import AlertGenerationService, AlertDeliveryService, AlertAnalyticsService
from apps.jobs.models import Job

logger = logging.getLogger(__name__)


@shared_task
def generate_alerts_for_new_job(job_id):
    """Tâche pour générer des alertes pour une nouvelle offre d'emploi"""
    try:
        logger.info(f"Début de la génération d'alertes pour l'offre {job_id}")
        
        service = AlertGenerationService()
        alerts_created = service.generate_job_alerts(job_id)
        
        logger.info(f"Génération terminée: {alerts_created} alertes créées pour l'offre {job_id}")
        return alerts_created
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération d'alertes pour l'offre {job_id}: {e}")
        return 0


@shared_task
def deliver_pending_alerts():
    """Tâche pour livrer toutes les alertes en attente"""
    try:
        logger.info("Début de la livraison des alertes en attente")
        
        service = AlertDeliveryService()
        delivered_count = service.deliver_pending_alerts()
        
        logger.info(f"Livraison terminée: {delivered_count} alertes livrées")
        return delivered_count
        
    except Exception as e:
        logger.error(f"Erreur lors de la livraison des alertes: {e}")
        return 0


@shared_task
def generate_daily_analytics():
    """Tâche pour générer les analytics quotidiennes"""
    try:
        logger.info("Génération des analytics quotidiennes")
        
        service = AlertAnalyticsService()
        yesterday = timezone.now().date() - timedelta(days=1)
        analytics = service.generate_daily_analytics(yesterday)
        
        if analytics:
            logger.info(f"Analytics générées pour {yesterday}")
            return analytics
        else:
            logger.warning(f"Impossible de générer les analytics pour {yesterday}")
            return None
            
    except Exception as e:
        logger.error(f"Erreur lors de la génération des analytics: {e}")
        return None


@shared_task
def cleanup_old_alerts():
    """Tâche pour nettoyer les anciennes alertes"""
    try:
        logger.info("Nettoyage des anciennes alertes")
        
        # Supprimer les alertes de plus de 90 jours
        cutoff_date = timezone.now() - timedelta(days=90)
        old_alerts = AlertNotification.objects.filter(created_at__lt=cutoff_date)
        
        count = old_alerts.count()
        old_alerts.delete()
        
        logger.info(f"Nettoyage terminé: {count} alertes supprimées")
        return count
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des alertes: {e}")
        return 0


@shared_task
def send_alert_summary():
    """Tâche pour envoyer un résumé des alertes aux utilisateurs"""
    try:
        logger.info("Envoi du résumé des alertes")
        
        # Récupérer les utilisateurs avec des préférences d'alertes
        users_with_preferences = AlertPreference.objects.filter(
            email_alerts=True,
            frequency__in=['daily', 'weekly']
        ).select_related('user')
        
        sent_count = 0
        
        for preference in users_with_preferences:
            try:
                # Déterminer la période selon la fréquence
                if preference.frequency == 'daily':
                    start_date = timezone.now().date()
                elif preference.frequency == 'weekly':
                    start_date = timezone.now().date() - timedelta(days=7)
                else:
                    continue
                
                # Récupérer les alertes de la période
                alerts = AlertNotification.objects.filter(
                    user=preference.user,
                    created_at__date__gte=start_date
                ).order_by('-created_at')
                
                if alerts.exists():
                    # Envoyer le résumé
                    if send_alert_summary_email(preference.user, alerts, preference.frequency):
                        sent_count += 1
                        
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du résumé pour {preference.user.email}: {e}")
        
        logger.info(f"Résumé envoyé: {sent_count} emails envoyés")
        return sent_count
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du résumé des alertes: {e}")
        return 0


def send_alert_summary_email(user, alerts, frequency):
    """Envoyer un email de résumé des alertes"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        period_text = "aujourd'hui" if frequency == 'daily' else "cette semaine"
        subject = f"Résumé de vos alertes emploi - {period_text}"
        
        # Compter les statistiques
        total_alerts = alerts.count()
        clicked_alerts = alerts.filter(status='clicked').count()
        avg_score = alerts.aggregate(avg_score=models.Avg('match_score'))['avg_score'] or 0
        
        # Template HTML pour le résumé
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">📊 Résumé de vos alertes emploi</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">{period_text.title()}</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px;">
                    <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h2 style="color: #007bff; margin-top: 0;">📈 Statistiques</h2>
                        <div style="display: flex; justify-content: space-around; text-align: center;">
                            <div>
                                <div style="font-size: 2em; font-weight: bold; color: #007bff;">{total_alerts}</div>
                                <div>Alertes reçues</div>
                            </div>
                            <div>
                                <div style="font-size: 2em; font-weight: bold; color: #28a745;">{clicked_alerts}</div>
                                <div>Alertes cliquées</div>
                            </div>
                            <div>
                                <div style="font-size: 2em; font-weight: bold; color: #ffc107;">{avg_score:.0f}%</div>
                                <div>Score moyen</div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px;">
                        <h2 style="color: #007bff; margin-top: 0;">🔔 Vos dernières alertes</h2>
                        """
        
        # Ajouter les alertes récentes
        for alert in alerts[:5]:
            html_message += f"""
            <div style="border-left: 4px solid #007bff; padding-left: 15px; margin-bottom: 15px;">
                <h3 style="margin: 0 0 5px 0; color: #2c3e50;">{alert.job.title}</h3>
                <p style="margin: 0 0 5px 0; color: #6c757d;">{alert.job.company} - {alert.job.location}</p>
                <p style="margin: 0; color: #007bff; font-weight: bold;">Score: {alert.match_score:.0f}%</p>
            </div>
            """
        
        html_message += """
                        </div>
                        
                        <div style="text-align: center; margin: 20px 0;">
                            <a href="{settings.SITE_URL}/alerts/" 
                               style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                📋 Voir toutes mes alertes
                            </a>
                        </div>
                        
                        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                            <p style="margin: 0; color: #1976d2;">
                                <strong>💡 Conseil :</strong> Consultez régulièrement vos alertes pour ne pas manquer les meilleures opportunités !
                            </p>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #dee2e6; margin: 20px 0;">
                        
                        <p style="font-size: 12px; color: #6c757d; text-align: center;">
                            Vous recevez ce résumé selon vos préférences d'alertes.<br>
                            <a href="{settings.SITE_URL}/alerts/preferences/">Modifier mes préférences</a>
                        </p>
                    </div>
                </div>
            </body>
            </html>
        """
        
        # Message texte simple
        plain_message = f"""
        Résumé de vos alertes emploi - {period_text}
        
        Statistiques:
        - {total_alerts} alertes reçues
        - {clicked_alerts} alertes cliquées
        - Score moyen: {avg_score:.0f}%
        
        Vos dernières alertes:
        """
        
        for alert in alerts[:5]:
            plain_message += f"\n- {alert.job.title} ({alert.job.company}) - Score: {alert.match_score:.0f}%"
        
        plain_message += f"\n\nVoir toutes vos alertes: {settings.SITE_URL}/alerts/"
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du résumé pour {user.email}: {e}")
        return False


@shared_task
def process_alert_feedback(alert_id, rating, feedback, reason):
    """Tâche pour traiter les commentaires sur les alertes"""
    try:
        logger.info(f"Traitement des commentaires pour l'alerte {alert_id}")
        
        # Ici, vous pourriez sauvegarder les commentaires dans une base de données
        # ou les envoyer à un service d'analyse
        
        # Pour l'instant, on log juste les informations
        logger.info(f"Alerte {alert_id} - Note: {rating}, Raison: {reason}, Commentaire: {feedback}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement des commentaires pour l'alerte {alert_id}: {e}")
        return False


@shared_task
def optimize_alert_preferences():
    """Tâche pour optimiser les préférences d'alertes basées sur l'historique"""
    try:
        logger.info("Optimisation des préférences d'alertes")
        
        # Analyser l'historique des alertes pour suggérer des améliorations
        users_with_preferences = AlertPreference.objects.all()
        optimized_count = 0
        
        for preference in users_with_preferences:
            try:
                # Analyser les alertes de l'utilisateur
                user_alerts = AlertNotification.objects.filter(user=preference.user)
                
                if user_alerts.count() < 10:  # Pas assez de données
                    continue
                
                # Calculer les statistiques
                avg_score = user_alerts.aggregate(avg_score=models.Avg('match_score'))['avg_score'] or 0
                click_rate = user_alerts.filter(status='clicked').count() / user_alerts.count()
                
                # Suggestions d'optimisation
                suggestions = []
                
                if avg_score < 60:
                    suggestions.append("Considérez ajuster vos critères de localisation ou de salaire")
                
                if click_rate < 0.1:
                    suggestions.append("Vous pourriez être trop restrictif dans vos préférences")
                
                if preference.max_alerts_per_day < 3 and click_rate > 0.3:
                    suggestions.append("Vous pourriez augmenter le nombre d'alertes par jour")
                
                # Ici, vous pourriez envoyer des suggestions à l'utilisateur
                if suggestions:
                    logger.info(f"Suggestions pour {preference.user.email}: {suggestions}")
                    optimized_count += 1
                    
            except Exception as e:
                logger.error(f"Erreur lors de l'optimisation pour {preference.user.email}: {e}")
        
        logger.info(f"Optimisation terminée: {optimized_count} utilisateurs avec suggestions")
        return optimized_count
        
    except Exception as e:
        logger.error(f"Erreur lors de l'optimisation des préférences: {e}")
        return 0


