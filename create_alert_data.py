#!/usr/bin/env python
"""
Script pour créer des données de test pour le système d'alertes
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.alerts.models import AlertType, AlertPreference, AlertNotification
from apps.jobs.models import Job
from apps.accounts.models import CandidateProfile

User = get_user_model()

def create_alert_types():
    """Créer les types d'alertes par défaut"""
    print("🔔 Création des types d'alertes...")
    
    alert_types = [
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
    for alert_data in alert_types:
        alert_type, created = AlertType.objects.get_or_create(
            name=alert_data['name'],
            defaults=alert_data
        )
        if created:
            created_count += 1
            print(f"  ✅ Créé: {alert_type.name}")
        else:
            print(f"  ⚠️  Existe déjà: {alert_type.name}")
    
    print(f"📊 {created_count} nouveaux types d'alertes créés")
    return AlertType.objects.all()

def create_alert_preferences():
    """Créer des préférences d'alertes pour les utilisateurs existants"""
    print("\n👤 Création des préférences d'alertes...")
    
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
            print(f"  ✅ Préférences créées pour: {user.full_name}")
        else:
            print(f"  ⚠️  Préférences existantes pour: {user.full_name}")
    
    print(f"📊 {created_count} nouvelles préférences créées")
    return AlertPreference.objects.all()

def create_sample_alerts():
    """Créer quelques alertes d'exemple"""
    print("\n🔔 Création d'alertes d'exemple...")
    
    # from apps.alerts.services import AlertGenerationService
    
    # Récupérer quelques utilisateurs et offres
    users = User.objects.filter(user_type='candidate')[:3]
    jobs = Job.objects.filter(is_active=True)[:5]
    alert_types = AlertType.objects.filter(is_active=True)
    
    if not users.exists() or not jobs.exists() or not alert_types.exists():
        print("  ⚠️  Pas assez de données pour créer des alertes d'exemple")
        return
    
    # service = AlertGenerationService()
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
            print(f"  ✅ Alerte créée: {user.full_name} - {job.title}")
    
    print(f"📊 {created_count} alertes d'exemple créées")

def main():
    """Fonction principale"""
    print("🚀 Initialisation du système d'alertes...")
    print("=" * 50)
    
    try:
        # Créer les types d'alertes
        alert_types = create_alert_types()
        
        # Créer les préférences d'alertes
        preferences = create_alert_preferences()
        
        # Créer des alertes d'exemple
        create_sample_alerts()
        
        print("\n" + "=" * 50)
        print("✅ Initialisation terminée avec succès !")
        print(f"📊 Types d'alertes: {alert_types.count()}")
        print(f"📊 Préférences: {preferences.count()}")
        print(f"📊 Alertes: {AlertNotification.objects.count()}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
