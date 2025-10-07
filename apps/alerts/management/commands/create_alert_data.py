from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.alerts.models import AlertType, AlertPreference, AlertNotification
from apps.jobs.models import Job

User = get_user_model()


class Command(BaseCommand):
    help = 'Créer des données de test pour le système d\'alertes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la création même si les données existent déjà',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Initialisation du système d\'alertes...')
        )
        
        try:
            # Créer les types d'alertes
            alert_types = self.create_alert_types(options['force'])
            
            # Créer les préférences d'alertes
            preferences = self.create_alert_preferences(options['force'])
            
            # Créer des alertes d'exemple
            alerts = self.create_sample_alerts(options['force'])
            
            self.stdout.write(
                self.style.SUCCESS('\n✅ Initialisation terminée avec succès !')
            )
            self.stdout.write(f"📊 Types d'alertes: {alert_types}")
            self.stdout.write(f"📊 Préférences: {preferences}")
            self.stdout.write(f"📊 Alertes: {alerts}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de l\'initialisation: {e}')
            )

    def create_alert_types(self, force=False):
        """Créer les types d'alertes par défaut"""
        self.stdout.write("🔔 Création des types d'alertes...")
        
        alert_types_data = [
            {
                'name': 'Nouvelle offre',
                'description': 'Notification pour une nouvelle offre d\'emploi correspondant à votre profil',
                'icon': 'fas fa-briefcase',
                'color': '#007bff',
                'is_active': True
            },
            {
                'name': 'Offre mise à jour',
                'description': 'Notification quand une offre que vous suivez est mise à jour',
                'icon': 'fas fa-edit',
                'color': '#28a745',
                'is_active': True
            },
            {
                'name': 'Offre expirant bientôt',
                'description': 'Notification pour les offres qui expirent dans les 7 prochains jours',
                'icon': 'fas fa-clock',
                'color': '#ffc107',
                'is_active': True
            },
            {
                'name': 'Recommandation personnalisée',
                'description': 'Recommandations d\'offres basées sur votre profil et vos préférences',
                'icon': 'fas fa-star',
                'color': '#6f42c1',
                'is_active': True
            },
            {
                'name': 'Offre urgente',
                'description': 'Offres marquées comme urgentes par les recruteurs',
                'icon': 'fas fa-exclamation-triangle',
                'color': '#dc3545',
                'is_active': True
            },
            {
                'name': 'Offre à distance',
                'description': 'Nouvelles offres de télétravail correspondant à votre profil',
                'icon': 'fas fa-home',
                'color': '#17a2b8',
                'is_active': True
            }
        ]
        
        created_count = 0
        for alert_data in alert_types_data:
            alert_type, created = AlertType.objects.get_or_create(
                name=alert_data['name'],
                defaults=alert_data
            )
            if created:
                created_count += 1
                self.stdout.write(f"  ✅ Créé: {alert_type.name}")
            else:
                self.stdout.write(f"  ⚠️  Existe déjà: {alert_type.name}")
        
        self.stdout.write(f"📊 {created_count} nouveaux types d'alertes créés")
        return AlertType.objects.count()

    def create_alert_preferences(self, force=False):
        """Créer des préférences d'alertes pour les utilisateurs existants"""
        self.stdout.write("\n👤 Création des préférences d'alertes...")
        
        users = User.objects.filter(user_type='candidate')
        created_count = 0
        
        for user in users:
            preference, created = AlertPreference.objects.get_or_create(
                user=user,
                defaults={
                    'email_alerts': True,
                    'push_notifications': True,
                    'sms_alerts': False,
                    'frequency': 'daily',
                    'max_alerts_per_day': 5,
                    'include_salary': True,
                    'include_remote_jobs': True,
                    'include_part_time': False,
                    'include_internships': False,
                    'max_distance': 50,
                    'preferred_locations': ['Paris', 'Lyon', 'Marseille'],
                    'min_salary': 30000,
                    'max_salary': 80000,
                    'min_experience': 0,
                    'max_experience': 10,
                    'preferred_job_types': ['CDI', 'CDD'],
                    'preferred_industries': ['Informatique', 'Marketing', 'Finance'],
                    'preferred_skills': ['Python', 'JavaScript', 'React', 'Django']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"  ✅ Préférences créées pour: {user.full_name}")
            else:
                self.stdout.write(f"  ⚠️  Préférences existantes pour: {user.full_name}")
        
        self.stdout.write(f"📊 {created_count} nouvelles préférences créées")
        return AlertPreference.objects.count()

    def create_sample_alerts(self, force=False):
        """Créer quelques alertes d'exemple"""
        self.stdout.write("\n🔔 Création d'alertes d'exemple...")
        
        # Récupérer quelques utilisateurs et offres
        users = User.objects.filter(user_type='candidate')[:3]
        jobs = Job.objects.filter(status='active')[:5]
        alert_types = AlertType.objects.filter(is_active=True)
        
        if not users.exists() or not jobs.exists() or not alert_types.exists():
            self.stdout.write("  ⚠️  Pas assez de données pour créer des alertes d'exemple")
            return 0
        
        created_count = 0
        
        for user in users:
            for job in jobs[:2]:  # 2 alertes par utilisateur
                alert_type = alert_types.first()
                
                # Vérifier si l'alerte existe déjà
                if AlertNotification.objects.filter(user=user, job=job, alert_type=alert_type).exists():
                    continue
                
                # Créer l'alerte
                alert = AlertNotification.objects.create(
                    user=user,
                    job=job,
                    alert_type=alert_type,
                    title=f"Nouvelle offre correspondant à votre profil : {job.title}",
                    message=f"Une nouvelle offre d'emploi correspond à votre profil :\n\n"
                           f"📋 {job.title}\n"
                           f"🏢 {job.company}\n"
                           f"📍 {job.location}\n"
                           f"💰 {job.salary_min:,} - {job.salary_max:,} {job.currency}\n\n"
                           f"🎯 Score de correspondance : 85%\n"
                           f"🔗 Voir l'offre : {job.get_absolute_url()}",
                    match_score=85.0,
                    match_reasons=[
                        "Compétences communes : Python, Django",
                        "Expérience suffisante (3 ans)",
                        "Localisation préférée : Paris"
                    ],
                    status='delivered'
                )
                
                created_count += 1
                self.stdout.write(f"  ✅ Alerte créée: {user.full_name} - {job.title}")
        
        self.stdout.write(f"📊 {created_count} alertes d'exemple créées")
        return AlertNotification.objects.count()
