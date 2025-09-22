import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from apps.jobs.models import Job, JobAlert
from apps.accounts.models import CandidateProfile
from apps.core.emails import send_newsletter
from django.db.models import Q

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Envoie les alertes emploi quotidiennes aux candidats'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Début de l\'envoi des alertes quotidiennes...')
        
        try:
            # RÃ©cupÃ©rer toutes les alertes actives
            active_alerts = JobAlert.objects.filter(is_active=True)
            
            total_sent = 0
            total_alerts = active_alerts.count()
            
            for alert in active_alerts:
                try:
                    # Trouver les offres correspondant aux critÃ¨res de l'alerte
                    matching_jobs = self.get_matching_jobs(alert)
                    
                    if matching_jobs.exists():
                        # Envoyer l'email d'alerte
                        success = self.send_alert_email(alert, matching_jobs)
                        if success:
                            total_sent += 1
                            alert.last_sent = timezone.now()
                            alert.save()
                    
                except Exception as e:
                    logger.error(f"Erreur avec l'alerte {alert.id}: {e}")
                    continue
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Alertes envoyées : {total_sent}/{total_alerts}'
                )
            )
            
        except Exception as e:
            logger.error(f"Erreur générale lors de l'envoi des alertes: {e}")
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur: {e}')
            )

    def get_matching_jobs(self, alert):
        """Retourne les offres correspondant aux critÃ¨res de l'alerte"""
        queryset = Job.objects.filter(
            status='published',
            application_deadline__gte=timezone.now()
        )
        
        # Filtres basÃ©s sur les critÃ¨res de l'alerte
        if alert.keywords:
            keywords = [k.strip() for k in alert.keywords.split(',')]
            query = Q()
            for keyword in keywords:
                query |= Q(title__icontains=keyword)
                query |= Q(description__icontains=keyword)
                query |= Q(company__icontains=keyword)
            queryset = queryset.filter(query)
        
        if alert.location:
            queryset = queryset.filter(location__icontains=alert.location)
        
        if alert.category:
            queryset = queryset.filter(category=alert.category)
        
        if alert.job_type:
            queryset = queryset.filter(job_type=alert.job_type)
        
        if alert.experience_level:
            queryset = queryset.filter(experience_level=alert.experience_level)
        
        if alert.salary_min:
            queryset = queryset.filter(
                Q(salary_min__gte=alert.salary_min) | 
                Q(salary_max__gte=alert.salary_min)
            )
        
        if alert.remote_work:
            queryset = queryset.filter(remote_work=True)
        
        # Exclure les offres dÃ©jÃ  vues/vieilles de plus de 7 jours
        seven_days_ago = timezone.now() - timezone.timedelta(days=7)
        queryset = queryset.filter(created_at__gte=seven_days_ago)
        
        return queryset.order_by('-created_at')[:10]  # Limiter Ã  10 offres

    def send_alert_email(self, alert, matching_jobs):
        """Envoie l'email d'alerte au candidat"""
        try:
            user = alert.user
            candidate = getattr(user, 'candidate_profile', None)
            
            if not candidate or not user.email:
                return False
            
            context = {
                'email': user.email,
                'user_name': user.get_full_name() or user.username,
                'matching_jobs': matching_jobs,
                'alert_title': alert.title,
                'unsubscribe_url': f"{settings.SITE_URL}/job-alerts/unsubscribe/{alert.id}/",
                'SITE_URL': settings.SITE_URL,
                'current_date': timezone.now(),
            }
            
            subject = f"🔔 Alertes emploi - {alert.title}"
            
            # Utiliser la fonction d'envoi d'email
            success_count, total_count = send_newsletter(
                None,
                subject,
                'new_job_alert.html',
                context
            )
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email pour l'alerte {alert.id}: {e}")
            return False

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Mode test - affiche les alertes sans envoyer d\'emails'
        )
        parser.add_argument(
            '--user',
            type=int,
            help='ID utilisateur spécifique pour tester'
        )

