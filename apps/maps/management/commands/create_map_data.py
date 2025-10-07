from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.maps.models import Location, JobLocation
from apps.jobs.models import Job
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Créer des données de test pour le système de cartes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la création même si les données existent déjà',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🗺️ Initialisation du système de cartes...')
        )
        
        try:
            # Créer les localisations
            locations = self.create_locations(options['force'])
            
            # Créer les liaisons emploi-localisation
            job_locations = self.create_job_locations(options['force'])
            
            self.stdout.write(
                self.style.SUCCESS('\n✅ Initialisation terminée avec succès !')
            )
            self.stdout.write(f"📊 Localisations: {locations}")
            self.stdout.write(f"📊 Liaisons emploi-localisation: {job_locations}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de l\'initialisation: {e}')
            )

    def create_locations(self, force=False):
        """Créer les localisations par défaut"""
        self.stdout.write("📍 Création des localisations...")
        
        locations_data = [
            {
                'name': 'Siège social',
                'address': '123 Avenue des Champs-Élysées',
                'city': 'Paris',
                'region': 'Île-de-France',
                'country': 'France',
                'postal_code': '75008',
                'latitude': 48.8566,
                'longitude': 2.3522,
                'is_remote': False,
                'is_hybrid': False
            },
            {
                'name': 'Bureau Lyon',
                'address': '45 Rue de la République',
                'city': 'Lyon',
                'region': 'Auvergne-Rhône-Alpes',
                'country': 'France',
                'postal_code': '69002',
                'latitude': 45.7640,
                'longitude': 4.8357,
                'is_remote': False,
                'is_hybrid': True
            },
            {
                'name': 'Bureau Marseille',
                'address': '78 La Canebière',
                'city': 'Marseille',
                'region': 'Provence-Alpes-Côte d\'Azur',
                'country': 'France',
                'postal_code': '13001',
                'latitude': 43.2965,
                'longitude': 5.3698,
                'is_remote': False,
                'is_hybrid': False
            },
            {
                'name': 'Bureau Toulouse',
                'address': '12 Place du Capitole',
                'city': 'Toulouse',
                'region': 'Occitanie',
                'country': 'France',
                'postal_code': '31000',
                'latitude': 43.6047,
                'longitude': 1.4442,
                'is_remote': False,
                'is_hybrid': True
            },
            {
                'name': 'Bureau Bordeaux',
                'address': '34 Cours de l\'Intendance',
                'city': 'Bordeaux',
                'region': 'Nouvelle-Aquitaine',
                'country': 'France',
                'postal_code': '33000',
                'latitude': 44.8378,
                'longitude': -0.5792,
                'is_remote': False,
                'is_hybrid': False
            },
            {
                'name': 'Bureau Nantes',
                'address': '56 Rue Crébillon',
                'city': 'Nantes',
                'region': 'Pays de la Loire',
                'country': 'France',
                'postal_code': '44000',
                'latitude': 47.2184,
                'longitude': -1.5536,
                'is_remote': False,
                'is_hybrid': True
            },
            {
                'name': 'Bureau Lille',
                'address': '89 Rue de la Barre',
                'city': 'Lille',
                'region': 'Hauts-de-France',
                'country': 'France',
                'postal_code': '59000',
                'latitude': 50.6292,
                'longitude': 3.0573,
                'is_remote': False,
                'is_hybrid': False
            },
            {
                'name': 'Bureau Strasbourg',
                'address': '23 Place Kléber',
                'city': 'Strasbourg',
                'region': 'Grand Est',
                'country': 'France',
                'postal_code': '67000',
                'latitude': 48.5734,
                'longitude': 7.7521,
                'is_remote': False,
                'is_hybrid': True
            },
            {
                'name': 'Bureau Montpellier',
                'address': '67 Rue de la Loge',
                'city': 'Montpellier',
                'region': 'Occitanie',
                'country': 'France',
                'postal_code': '34000',
                'latitude': 43.6110,
                'longitude': 3.8767,
                'is_remote': False,
                'is_hybrid': False
            },
            {
                'name': 'Bureau Rennes',
                'address': '45 Rue de la Monnaie',
                'city': 'Rennes',
                'region': 'Bretagne',
                'country': 'France',
                'postal_code': '35000',
                'latitude': 48.1173,
                'longitude': -1.6778,
                'is_remote': False,
                'is_hybrid': True
            },
            {
                'name': 'Télétravail',
                'address': 'Télétravail',
                'city': 'France',
                'region': 'France',
                'country': 'France',
                'postal_code': '00000',
                'latitude': 46.603354,
                'longitude': 1.888334,
                'is_remote': True,
                'is_hybrid': False
            }
        ]
        
        created_count = 0
        for location_data in locations_data:
            location, created = Location.objects.get_or_create(
                name=location_data['name'],
                city=location_data['city'],
                defaults=location_data
            )
            if created:
                created_count += 1
                self.stdout.write(f"  ✅ Créé: {location.name} - {location.city}")
            else:
                self.stdout.write(f"  ⚠️  Existe déjà: {location.name} - {location.city}")
        
        self.stdout.write(f"📊 {created_count} nouvelles localisations créées")
        return Location.objects.count()

    def create_job_locations(self, force=False):
        """Créer les liaisons emploi-localisation"""
        self.stdout.write("\n🔗 Création des liaisons emploi-localisation...")
        
        jobs = Job.objects.filter(status='active')
        locations = Location.objects.all()
        
        if not jobs.exists() or not locations.exists():
            self.stdout.write("  ⚠️  Pas assez de données pour créer des liaisons")
            return 0
        
        created_count = 0
        
        for job in jobs:
            # Choisir une localisation aléatoire
            location = random.choice(locations)
            
            # Vérifier si la liaison existe déjà
            if JobLocation.objects.filter(job=job, location=location).exists():
                continue
            
            # Déterminer le type de localisation
            location_type = 'primary'
            if location.is_remote:
                location_type = 'remote'
            elif location.is_hybrid:
                location_type = 'hybrid'
            
            # Créer la liaison
            job_location = JobLocation.objects.create(
                job=job,
                location=location,
                location_type=location_type,
                is_primary=True,
                work_days_per_week=5
            )
            
            created_count += 1
            self.stdout.write(f"  ✅ Liaison créée: {job.title} - {location.name}")
        
        self.stdout.write(f"📊 {created_count} liaisons emploi-localisation créées")
        return JobLocation.objects.count()

