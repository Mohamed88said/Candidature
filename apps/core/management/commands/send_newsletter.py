from django.core.management.base import BaseCommand
from django.conf import settings
from apps.accounts.models import User
from apps.core.tasks import send_newsletter_task
from django.utils import timezone

class Command(BaseCommand):
    help = 'Envoyer la newsletter aux utilisateurs abonnés'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Envoyer un email test à l\'administrateur',
        )
        parser.add_argument(
            '--subject',
            type=str,
            help='Sujet de la newsletter',
            required=True,
        )
        parser.add_argument(
            '--template',
            type=str,
            help='Nom du template email',
            required=True,
        )
    
    def handle(self, *args, **options):
        test_mode = options['test']
        subject = options['subject']
        template_name = options['template']
        
        if test_mode:
            # Mode test : envoyer seulement à l'admin
            recipients = [settings.DEFAULT_FROM_EMAIL]
            self.stdout.write(self.style.WARNING('Mode test activé - Envoi à l\'administrateur seulement'))
        else:
            # Récupérer tous les utilisateurs abonnés à la newsletter
            recipients = User.objects.filter(
                is_active=True,
                candidate_profile__isnull=False
            ).values_list('email', flat=True)
            
            self.stdout.write(self.style.SUCCESS(f'Envoi de newsletter à {len(recipients)} destinataires'))
        
        # Préparer le contexte pour chaque destinataire
        context_list = []
        for email in recipients:
            context = {
                'current_date': timezone.now().date(),
                'unsubscribe_url': f"{settings.SITE_URL}/unsubscribe/?email={email}",
                'user_email': email,
                'platform_name': 'Plateforme de Recrutement'
            }
            context_list.append(context)
        
        # Lancer la tâche asynchrone
        result = send_newsletter_task.delay(subject, template_name, context_list, list(recipients))
        
        self.stdout.write(self.style.SUCCESS(
            f'Tâche d\'envoi de newsletter lancée avec ID: {result.id}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Sujet: {subject}, Template: {template_name}'
        ))