from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from datetime import datetime, timedelta
import logging

from .models import AlertNotification, AlertPreference, AlertType
from apps.jobs.models import Job
from apps.matching.services import IntelligentMatchingService

User = get_user_model()
logger = logging.getLogger(__name__)


class AlertGenerationService:
    """Service pour générer des alertes automatiques"""
    
    def __init__(self):
        self.matching_service = IntelligentMatchingService()
    
    def generate_job_alerts(self, job_id):
        """Générer des alertes pour une nouvelle offre d'emploi"""
        try:
            job = Job.objects.get(id=job_id)
            logger.info(f"Génération d'alertes pour l'offre: {job.title}")
            
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
                            logger.info(f"Alerte créée pour {user.full_name} - Score: {match_score}")
            
            logger.info(f"Génération terminée: {alerts_created} alertes créées")
            return alerts_created
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'alertes: {e}")
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
            logger.error(f"Erreur lors de la vérification des critères: {e}")
            return False
    
    def calculate_match_score(self, user, job):
        """Calculer le score de correspondance entre un utilisateur et une offre"""
        try:
            # Utiliser le service de matching intelligent
            match_result = self.matching_service.calculate_match_score(user, job)
            return match_result.get('total_score', 0)
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul du score: {e}")
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
            logger.error(f"Erreur lors de la création de l'alerte: {e}")
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


class AlertDeliveryService:
    """Service pour la livraison des alertes"""
    
    def __init__(self):
        self.email_service = EmailAlertService()
        self.push_service = PushNotificationService()
        self.sms_service = SMSAlertService()
    
    def deliver_alert(self, alert):
        """Livrer une alerte via tous les canaux activés"""
        try:
            preferences = alert.user.alert_preferences
            delivered = False
            
            # Email
            if preferences.email_alerts:
                if self.email_service.send_alert(alert):
                    alert.email_sent = True
                    delivered = True
            
            # Push notification
            if preferences.push_notifications:
                if self.push_service.send_alert(alert):
                    alert.push_sent = True
                    delivered = True
            
            # SMS
            if preferences.sms_alerts:
                if self.sms_service.send_alert(alert):
                    alert.sms_sent = True
                    delivered = True
            
            if delivered:
                alert.mark_as_delivered()
                logger.info(f"Alerte {alert.id} livrée avec succès")
            else:
                alert.status = 'failed'
                alert.save()
                logger.error(f"Échec de la livraison de l'alerte {alert.id}")
            
            return delivered
            
        except Exception as e:
            logger.error(f"Erreur lors de la livraison de l'alerte {alert.id}: {e}")
            return False
    
    def deliver_pending_alerts(self):
        """Livrer toutes les alertes en attente"""
        pending_alerts = AlertNotification.objects.filter(status='pending')
        delivered_count = 0
        
        for alert in pending_alerts:
            if self.deliver_alert(alert):
                delivered_count += 1
        
        logger.info(f"Livraison terminée: {delivered_count} alertes livrées")
        return delivered_count


class EmailAlertService:
    """Service pour l'envoi d'alertes par email"""
    
    def send_alert(self, alert):
        """Envoyer une alerte par email"""
        try:
            subject = f"[Alerte Emploi] {alert.title}"
            
            # Template HTML pour l'email
            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 24px;">🔔 Nouvelle alerte emploi</h1>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px;">
                        <h2 style="color: #007bff; margin-top: 0;">{alert.job.title}</h2>
                        
                        <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                            <p><strong>🏢 Entreprise :</strong> {alert.job.company}</p>
                            <p><strong>📍 Localisation :</strong> {alert.job.location}</p>
                            <p><strong>💼 Type :</strong> {alert.job.get_job_type_display()}</p>
                            <p><strong>⏰ Expérience :</strong> {alert.job.get_experience_level_display()}</p>
                        </div>
                        
                        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                            <h3 style="color: #1976d2; margin-top: 0;">🎯 Score de correspondance : {alert.match_score:.0f}%</h3>
                            
                            <h4>Pourquoi cette offre vous correspond :</h4>
                            <ul>
                                {''.join([f'<li>{reason}</li>' for reason in alert.match_reasons])}
                            </ul>
                        </div>
                        
                        <div style="text-align: center; margin: 20px 0;">
                            <a href="{alert.job.get_absolute_url()}" 
                               style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                📋 Voir l'offre complète
                            </a>
                        </div>
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                            <p style="margin: 0; color: #856404;">
                                <strong>💡 Conseil :</strong> Postulez rapidement ! Les meilleures offres sont souvent prises rapidement.
                            </p>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #dee2e6; margin: 20px 0;">
                        
                        <p style="font-size: 12px; color: #6c757d; text-align: center;">
                            Vous recevez cette alerte car vous avez activé les notifications pour ce type d'offre.<br>
                            <a href="{settings.SITE_URL}/alerts/preferences/">Modifier mes préférences</a>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Message texte simple
            plain_message = alert.message
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[alert.user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Email envoyé pour l'alerte {alert.id} à {alert.user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email pour l'alerte {alert.id}: {e}")
            return False


class PushNotificationService:
    """Service pour les notifications push"""
    
    def send_alert(self, alert):
        """Envoyer une notification push"""
        try:
            # Ici, vous intégreriez avec un service de notifications push
            # comme Firebase Cloud Messaging, OneSignal, etc.
            
            # Pour l'instant, on simule l'envoi
            logger.info(f"Notification push envoyée pour l'alerte {alert.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification push pour l'alerte {alert.id}: {e}")
            return False


class SMSAlertService:
    """Service pour l'envoi d'alertes par SMS"""
    
    def send_alert(self, alert):
        """Envoyer une alerte par SMS"""
        try:
            # Ici, vous intégreriez avec un service SMS
            # comme Twilio, Nexmo, etc.
            
            # Pour l'instant, on simule l'envoi
            logger.info(f"SMS envoyé pour l'alerte {alert.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du SMS pour l'alerte {alert.id}: {e}")
            return False


class AlertAnalyticsService:
    """Service pour les analytics des alertes"""
    
    def generate_daily_analytics(self, date=None):
        """Générer les analytics pour une date donnée"""
        if date is None:
            date = timezone.now().date()
        
        try:
            # Statistiques générales
            total_alerts = AlertNotification.objects.filter(created_at__date=date).count()
            total_delivered = AlertNotification.objects.filter(
                created_at__date=date,
                status__in=['delivered', 'opened', 'clicked']
            ).count()
            total_opened = AlertNotification.objects.filter(
                created_at__date=date,
                status__in=['opened', 'clicked']
            ).count()
            total_clicked = AlertNotification.objects.filter(
                created_at__date=date,
                status='clicked'
            ).count()
            
            # Taux de conversion
            delivery_rate = (total_delivered / total_alerts * 100) if total_alerts > 0 else 0
            open_rate = (total_opened / total_delivered * 100) if total_delivered > 0 else 0
            click_rate = (total_clicked / total_opened * 100) if total_opened > 0 else 0
            
            # Statistiques par type
            alerts_by_type = {}
            for alert_type in AlertType.objects.all():
                count = AlertNotification.objects.filter(
                    created_at__date=date,
                    alert_type=alert_type
                ).count()
                alerts_by_type[alert_type.name] = count
            
            # Statistiques par canal
            email_alerts_sent = AlertNotification.objects.filter(
                created_at__date=date,
                email_sent=True
            ).count()
            push_alerts_sent = AlertNotification.objects.filter(
                created_at__date=date,
                push_sent=True
            ).count()
            sms_alerts_sent = AlertNotification.objects.filter(
                created_at__date=date,
                sms_sent=True
            ).count()
            
            return {
                'date': date,
                'total_alerts_sent': total_alerts,
                'total_alerts_delivered': total_delivered,
                'total_alerts_opened': total_opened,
                'total_alerts_clicked': total_clicked,
                'delivery_rate': delivery_rate,
                'open_rate': open_rate,
                'click_rate': click_rate,
                'alerts_by_type': alerts_by_type,
                'email_alerts_sent': email_alerts_sent,
                'push_alerts_sent': push_alerts_sent,
                'sms_alerts_sent': sms_alerts_sent
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des analytics pour {date}: {e}")
            return None


