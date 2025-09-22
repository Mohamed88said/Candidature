from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Job
from apps.core.tasks import send_newsletter_task
from apps.core.models import Newsletter

@receiver(post_save, sender=Job)
def send_new_job_notification(sender, instance, created, **kwargs):
    """Envoyer une notification quand une nouvelle offre est publiée"""
    if created and instance.status == 'published':
        # Envoyer une notification pour les nouvelles offres
        subject = f"Nouvelle offre : {instance.title}"
        template_name = "new_job_alert.html"
        
        # Récupérer tous les abonnés actifs
        subscribers = Newsletter.objects.filter(is_active=True)
        recipient_emails = list(subscribers.values_list('email', flat=True))
        
        if recipient_emails:
            context_list = []
            for email in recipient_emails:
                context = {
                    'job': instance,
                    'email': email,
                    'unsubscribe_url': f"{settings.SITE_URL}/newsletter/unsubscribe/{email}/",
                    'SITE_URL': settings.SITE_URL,
                }
                context_list.append(context)
            
            send_newsletter_task.delay(subject, template_name, context_list, recipient_emails)
