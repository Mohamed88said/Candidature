from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.referrals.models import ReferralProgram
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Créer le programme de recommandation par défaut'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la création même si le programme existe déjà',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🎯 Initialisation du programme de recommandation...')
        )
        
        try:
            # Créer le programme de recommandation
            program = self.create_referral_program(options['force'])
            
            self.stdout.write(
                self.style.SUCCESS('\n✅ Initialisation terminée avec succès !')
            )
            self.stdout.write(f"📊 Programme: {program}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de l\'initialisation: {e}')
            )

    def create_referral_program(self, force=False):
        """Créer le programme de recommandation par défaut"""
        self.stdout.write("🎯 Création du programme de recommandation...")
        
        program_data = {
            'name': 'Programme de Recommandation 2024',
            'description': 'Invitez vos amis et gagnez des récompenses ! Partagez votre code de recommandation et recevez des points pour chaque ami qui s\'inscrit.',
            'referrer_reward': {
                'type': 'points',
                'amount': 100,
                'description': '100 points pour chaque ami inscrit'
            },
            'referee_reward': {
                'type': 'points',
                'amount': 50,
                'description': '50 points de bienvenue'
            },
            'min_referrals_for_bonus': 5,
            'bonus_reward': {
                'type': 'points',
                'amount': 500,
                'description': '500 points bonus pour 5 recommandations'
            },
            'max_referrals_per_user': 20,
            'max_rewards_per_user': 2000,
            'is_active': True,
            'start_date': timezone.now(),
            'end_date': timezone.now() + timedelta(days=365)  # 1 an
        }
        
        program, created = ReferralProgram.objects.get_or_create(
            name=program_data['name'],
            defaults=program_data
        )
        
        if created:
            self.stdout.write(f"  ✅ Créé: {program.name}")
        else:
            self.stdout.write(f"  ⚠️  Existe déjà: {program.name}")
        
        self.stdout.write(f"📊 Programme de recommandation créé")
        return ReferralProgram.objects.count()


