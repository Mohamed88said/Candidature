import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import json

from apps.company_reviews.models import (
    Company, CompanyReview, CompanySalary, CompanyInterview, 
    CompanyBenefit, CompanyPhoto, CompanyFollow
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Initializes companies, reviews, salaries, and interviews with example data.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🔄 Système keep-alive activé'))
        self.stdout.write(self.style.SUCCESS('🏢 Initialisation du système d\'avis sur les entreprises...'))

        self.create_companies()
        self.create_benefits()
        self.create_reviews()
        self.create_salaries()
        self.create_interviews()
        self.create_follows()

        self.stdout.write(self.style.SUCCESS('\n✅ Initialisation terminée avec succès !'))
        self.stdout.write(self.style.SUCCESS(f'🏢 Entreprises: {Company.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'⭐ Avis: {CompanyReview.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'💰 Salaires: {CompanySalary.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'🎯 Entretiens: {CompanyInterview.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'🎁 Avantages: {CompanyBenefit.objects.count()}'))

    def create_companies(self):
        """Créer des entreprises d'exemple"""
        self.stdout.write("\n🏢 Création des entreprises...")
        
        companies_data = [
            {
                'name': 'TechCorp Solutions',
                'description': 'Leader en solutions technologiques innovantes pour les entreprises. Nous développons des logiciels de pointe et offrons des services de conseil en transformation digitale.',
                'industry': 'Technologie',
                'size': '201-500',
                'founded_year': 2015,
                'headquarters': 'Paris, France',
                'website': 'https://www.techcorp-solutions.com',
                'email': 'contact@techcorp-solutions.com',
                'phone': '+33 1 23 45 67 89'
            },
            {
                'name': 'GreenEnergy France',
                'description': 'Entreprise spécialisée dans les énergies renouvelables et le développement durable. Nous proposons des solutions solaires et éoliennes pour particuliers et entreprises.',
                'industry': 'Énergie',
                'size': '51-200',
                'founded_year': 2010,
                'headquarters': 'Lyon, France',
                'website': 'https://www.greenenergy-france.fr',
                'email': 'info@greenenergy-france.fr',
                'phone': '+33 4 78 90 12 34'
            },
            {
                'name': 'FinancePro Consulting',
                'description': 'Cabinet de conseil financier spécialisé dans l\'accompagnement des PME et startups. Nous offrons des services de gestion financière, levée de fonds et stratégie d\'entreprise.',
                'industry': 'Finance',
                'size': '11-50',
                'founded_year': 2018,
                'headquarters': 'Marseille, France',
                'website': 'https://www.financepro-consulting.fr',
                'email': 'contact@financepro-consulting.fr',
                'phone': '+33 4 91 23 45 67'
            },
            {
                'name': 'HealthCare Plus',
                'description': 'Réseau de cliniques privées offrant des soins de qualité dans toute la France. Nous nous spécialisons dans la médecine préventive et les soins spécialisés.',
                'industry': 'Santé',
                'size': '501-1000',
                'founded_year': 2005,
                'headquarters': 'Toulouse, France',
                'website': 'https://www.healthcare-plus.fr',
                'email': 'contact@healthcare-plus.fr',
                'phone': '+33 5 61 23 45 67'
            },
            {
                'name': 'EduTech Academy',
                'description': 'Plateforme d\'apprentissage en ligne révolutionnaire qui propose des cours interactifs et des certifications professionnelles dans le domaine de la technologie.',
                'industry': 'Éducation',
                'size': '51-200',
                'founded_year': 2020,
                'headquarters': 'Nantes, France',
                'website': 'https://www.edutech-academy.fr',
                'email': 'hello@edutech-academy.fr',
                'phone': '+33 2 40 12 34 56'
            },
            {
                'name': 'RetailMax',
                'description': 'Chaîne de magasins de détail spécialisée dans l\'électronique et les produits high-tech. Nous offrons une large gamme de produits et des services après-vente de qualité.',
                'industry': 'Commerce de détail',
                'size': '1000+',
                'founded_year': 1995,
                'headquarters': 'Lille, France',
                'website': 'https://www.retailmax.fr',
                'email': 'contact@retailmax.fr',
                'phone': '+33 3 20 12 34 56'
            }
        ]
        
        new_count = 0
        for data in companies_data:
            # Créer le slug à partir du nom
            slug = data['name'].lower().replace(' ', '-').replace('&', 'et')
            
            company, created = Company.objects.get_or_create(
                name=data['name'],
                defaults={
                    'slug': slug,
                    'description': data['description'],
                    'industry': data['industry'],
                    'size': data['size'],
                    'founded_year': data['founded_year'],
                    'headquarters': data['headquarters'],
                    'website': data['website'],
                    'email': data['email'],
                    'phone': data['phone'],
                    'is_verified': random.choice([True, False]),
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f"  ✅ Créé: {company.name}")
                new_count += 1
            else:
                self.stdout.write(f"  ⚠️  Existe déjà: {company.name}")
        
        self.stdout.write(f"📊 {new_count} nouvelles entreprises créées")

    def create_benefits(self):
        """Créer des avantages pour les entreprises"""
        self.stdout.write("\n🎁 Création des avantages d'entreprises...")
        
        benefits_data = [
            # TechCorp Solutions
            {'company_name': 'TechCorp Solutions', 'benefits': [
                {'name': 'Télétravail flexible', 'description': 'Possibilité de télétravailler 3 jours par semaine', 'category': 'work_life'},
                {'name': 'Formation continue', 'description': 'Budget de 2000€ par an pour la formation', 'category': 'professional'},
                {'name': 'Assurance santé premium', 'description': 'Couverture santé étendue pour toute la famille', 'category': 'health'},
                {'name': 'Stock options', 'description': 'Participation aux bénéfices de l\'entreprise', 'category': 'financial'},
                {'name': 'Salle de sport', 'description': 'Accès gratuit à la salle de sport de l\'entreprise', 'category': 'wellness'}
            ]},
            # GreenEnergy France
            {'company_name': 'GreenEnergy France', 'benefits': [
                {'name': 'Véhicule électrique', 'description': 'Véhicule de fonction électrique', 'category': 'financial'},
                {'name': 'Prime écologique', 'description': 'Prime de 500€ par an pour les actions écologiques', 'category': 'financial'},
                {'name': 'Formation environnementale', 'description': 'Formations sur les enjeux environnementaux', 'category': 'professional'},
                {'name': 'Horaires flexibles', 'description': 'Horaires de travail adaptables', 'category': 'work_life'}
            ]},
            # FinancePro Consulting
            {'company_name': 'FinancePro Consulting', 'benefits': [
                {'name': 'Prime de performance', 'description': 'Prime variable basée sur les résultats', 'category': 'financial'},
                {'name': 'Formation financière', 'description': 'Formations continues en finance et investissement', 'category': 'professional'},
                {'name': 'Tickets restaurant', 'description': 'Tickets restaurant de 9€ par jour', 'category': 'financial'},
                {'name': 'Mutuelle d\'entreprise', 'description': 'Mutuelle santé prise en charge à 80%', 'category': 'health'}
            ]},
            # HealthCare Plus
            {'company_name': 'HealthCare Plus', 'benefits': [
                {'name': 'Soins gratuits', 'description': 'Accès gratuit aux soins dans nos cliniques', 'category': 'health'},
                {'name': 'Formation médicale', 'description': 'Formations continues en médecine', 'category': 'professional'},
                {'name': 'Garde d\'enfants', 'description': 'Service de garde d\'enfants sur site', 'category': 'family'},
                {'name': 'Prime de service', 'description': 'Prime pour les services de nuit et week-end', 'category': 'financial'}
            ]},
            # EduTech Academy
            {'company_name': 'EduTech Academy', 'benefits': [
                {'name': 'Formation gratuite', 'description': 'Accès gratuit à tous nos cours en ligne', 'category': 'professional'},
                {'name': 'Matériel informatique', 'description': 'Ordinateur portable et équipements fournis', 'category': 'financial'},
                {'name': 'Télétravail total', 'description': 'Possibilité de télétravailler à 100%', 'category': 'work_life'},
                {'name': 'Prime d\'innovation', 'description': 'Prime pour les idées innovantes', 'category': 'financial'}
            ]},
            # RetailMax
            {'company_name': 'RetailMax', 'benefits': [
                {'name': 'Réduction employé', 'description': 'Réduction de 20% sur tous les produits', 'category': 'financial'},
                {'name': 'Prime de vente', 'description': 'Commission sur les ventes réalisées', 'category': 'financial'},
                {'name': 'Formation commerciale', 'description': 'Formations en techniques de vente', 'category': 'professional'},
                {'name': 'Horaires variables', 'description': 'Horaires adaptés aux besoins personnels', 'category': 'work_life'}
            ]}
        ]
        
        new_count = 0
        for company_data in benefits_data:
            try:
                company = Company.objects.get(name=company_data['company_name'])
                for benefit_data in company_data['benefits']:
                    benefit, created = CompanyBenefit.objects.get_or_create(
                        company=company,
                        name=benefit_data['name'],
                        defaults={
                            'description': benefit_data['description'],
                            'category': benefit_data['category'],
                            'is_available': True
                        }
                    )
                    if created:
                        new_count += 1
            except Company.DoesNotExist:
                self.stdout.write(f"  ⚠️  Entreprise non trouvée: {company_data['company_name']}")
        
        self.stdout.write(f"📊 {new_count} nouveaux avantages créés")

    def create_reviews(self):
        """Créer des avis d'exemple"""
        self.stdout.write("\n⭐ Création des avis d'entreprises...")
        
        companies = Company.objects.all()
        users = User.objects.filter(user_type='candidate')[:10]
        
        if not companies.exists() or not users.exists():
            self.stdout.write("  ⚠️  Pas assez de données pour créer des avis")
            return 0
        
        review_templates = [
            {
                'pros': 'Excellente culture d\'entreprise, équipe très motivée et projets innovants. L\'environnement de travail est stimulant et les collègues sont très compétents.',
                'cons': 'Parfois des délais serrés qui peuvent créer du stress. La communication entre les départements pourrait être améliorée.',
                'advice': 'Continuer à investir dans la formation des employés et améliorer la communication interne.'
            },
            {
                'pros': 'Très bonne ambiance de travail, management à l\'écoute et possibilités d\'évolution intéressantes. Les projets sont variés et passionnants.',
                'cons': 'Salaire légèrement en dessous du marché. Quelques processus internes un peu lourds.',
                'advice': 'Revoir la politique salariale pour rester compétitif sur le marché.'
            },
            {
                'pros': 'Entreprise en pleine croissance avec de nombreuses opportunités. L\'équipe est jeune et dynamique, l\'innovation est encouragée.',
                'cons': 'Structure encore en développement, certains processus ne sont pas encore bien définis. Charge de travail parfois importante.',
                'advice': 'Structurer davantage les processus et recruter pour alléger la charge de travail.'
            }
        ]
        
        new_count = 0
        for company in companies:
            for user in users:
                # Vérifier si l'utilisateur a déjà un avis pour cette entreprise
                if not CompanyReview.objects.filter(company=company, user=user).exists():
                    template = random.choice(review_templates)
                    
                    # Dates d'emploi aléatoires
                    start_date = timezone.now().date() - timedelta(days=random.randint(30, 1000))
                    end_date = None
                    is_current = random.choice([True, False])
                    
                    if not is_current:
                        end_date = start_date + timedelta(days=random.randint(30, 500))
                    
                    review = CompanyReview.objects.create(
                        company=company,
                        user=user,
                        job_title=random.choice(['Développeur', 'Chef de projet', 'Analyste', 'Consultant', 'Manager', 'Spécialiste']),
                        employment_status=random.choice(['current', 'former']),
                        employment_start_date=start_date,
                        employment_end_date=end_date,
                        is_current_employee=is_current,
                        overall_rating=random.randint(3, 5),
                        work_life_balance=random.randint(3, 5),
                        salary_benefits=random.randint(2, 5),
                        job_security=random.randint(3, 5),
                        management=random.randint(3, 5),
                        culture=random.randint(3, 5),
                        career_opportunities=random.randint(3, 5),
                        pros=template['pros'],
                        cons=template['cons'],
                        advice_to_management=template['advice'],
                        would_recommend=random.choice([True, False]),
                        is_approved=True,
                        is_anonymous=random.choice([True, False])
                    )
                    
                    self.stdout.write(f"  ✅ Avis créé pour {user.username} - {company.name}")
                    new_count += 1
        
        self.stdout.write(f"📊 {new_count} nouveaux avis créés")

    def create_salaries(self):
        """Créer des informations salariales"""
        self.stdout.write("\n💰 Création des informations salariales...")
        
        companies = Company.objects.all()
        users = User.objects.filter(user_type='candidate')[:5]
        
        if not companies.exists() or not users.exists():
            self.stdout.write("  ⚠️  Pas assez de données pour créer des salaires")
            return 0
        
        salary_ranges = [
            {'min': 30000, 'max': 45000, 'level': 'entry'},
            {'min': 45000, 'max': 65000, 'level': 'junior'},
            {'min': 65000, 'max': 85000, 'level': 'mid'},
            {'min': 85000, 'max': 120000, 'level': 'senior'},
            {'min': 120000, 'max': 200000, 'level': 'lead'}
        ]
        
        new_count = 0
        for company in companies:
            for user in users:
                if not CompanySalary.objects.filter(company=company, user=user).exists():
                    salary_range = random.choice(salary_ranges)
                    base_salary = random.randint(salary_range['min'], salary_range['max'])
                    bonus = random.randint(0, base_salary // 10)
                    total_compensation = base_salary + bonus
                    
                    salary = CompanySalary.objects.create(
                        company=company,
                        user=user,
                        job_title=random.choice(['Développeur', 'Chef de projet', 'Analyste', 'Consultant', 'Manager']),
                        department=random.choice(['IT', 'Marketing', 'Finance', 'RH', 'Ventes']),
                        location=company.headquarters,
                        base_salary=base_salary,
                        bonus=bonus,
                        total_compensation=total_compensation,
                        currency='EUR',
                        employment_type=random.choice(['full_time', 'contract']),
                        experience_level=salary_range['level'],
                        years_at_company=random.randint(1, 5),
                        is_approved=True,
                        is_anonymous=random.choice([True, False])
                    )
                    
                    self.stdout.write(f"  ✅ Salaire créé pour {user.username} - {company.name}")
                    new_count += 1
        
        self.stdout.write(f"📊 {new_count} nouvelles informations salariales créées")

    def create_interviews(self):
        """Créer des expériences d'entretien"""
        self.stdout.write("\n🎯 Création des expériences d'entretien...")
        
        companies = Company.objects.all()
        users = User.objects.filter(user_type='candidate')[:5]
        
        if not companies.exists() or not users.exists():
            self.stdout.write("  ⚠️  Pas assez de données pour créer des entretiens")
            return 0
        
        interview_templates = [
            {
                'questions': 'Questions techniques sur les compétences, cas pratiques, questions sur l\'expérience passée et motivations.',
                'process': 'Entretien téléphonique initial, puis entretien technique avec l\'équipe, enfin entretien avec le manager.',
                'pros': 'Processus bien structuré, équipe accueillante, questions pertinentes.',
                'cons': 'Processus un peu long, délais de réponse parfois lents.',
                'advice': 'Préparer bien les cas pratiques et être prêt à discuter de projets concrets.'
            },
            {
                'questions': 'Questions sur la culture d\'entreprise, compétences techniques, projets réalisés et objectifs de carrière.',
                'process': 'Entretien vidéo avec le RH, puis entretien technique, enfin entretien avec la direction.',
                'pros': 'Équipe très professionnelle, questions équilibrées entre technique et culture.',
                'cons': 'Entretien technique assez difficile, délais de réponse longs.',
                'advice': 'Bien connaître l\'entreprise et ses valeurs, préparer des exemples concrets.'
            }
        ]
        
        new_count = 0
        for company in companies:
            for user in users:
                if not CompanyInterview.objects.filter(company=company, user=user).exists():
                    template = random.choice(interview_templates)
                    
                    interview = CompanyInterview.objects.create(
                        company=company,
                        user=user,
                        job_title=random.choice(['Développeur', 'Chef de projet', 'Analyste', 'Consultant']),
                        department=random.choice(['IT', 'Marketing', 'Finance', 'RH']),
                        interview_date=timezone.now().date() - timedelta(days=random.randint(1, 100)),
                        interview_type=random.choice(['Entretien téléphonique', 'Entretien vidéo', 'Entretien sur site']),
                        difficulty=random.choice(['easy', 'average', 'difficult']),
                        duration=random.randint(30, 120),
                        interview_questions=template['questions'],
                        interview_process=template['process'],
                        outcome=random.choice(['accepted', 'rejected', 'no_response']),
                        offer_made=random.choice([True, False]),
                        offer_amount=random.randint(35000, 80000) if random.choice([True, False]) else None,
                        overall_experience=random.randint(3, 5),
                        pros=template['pros'],
                        cons=template['cons'],
                        advice=template['advice'],
                        is_approved=True,
                        is_anonymous=random.choice([True, False])
                    )
                    
                    self.stdout.write(f"  ✅ Entretien créé pour {user.username} - {company.name}")
                    new_count += 1
        
        self.stdout.write(f"📊 {new_count} nouvelles expériences d'entretien créées")

    def create_follows(self):
        """Créer des suivis d'entreprises"""
        self.stdout.write("\n❤️ Création des suivis d'entreprises...")
        
        companies = Company.objects.all()
        users = User.objects.filter(user_type='candidate')[:5]
        
        if not companies.exists() or not users.exists():
            self.stdout.write("  ⚠️  Pas assez de données pour créer des suivis")
            return 0
        
        new_count = 0
        for user in users:
            # Chaque utilisateur suit 2-3 entreprises aléatoires
            companies_to_follow = random.sample(list(companies), random.randint(2, min(3, companies.count())))
            
            for company in companies_to_follow:
                if not CompanyFollow.objects.filter(user=user, company=company).exists():
                    CompanyFollow.objects.create(
                        user=user,
                        company=company
                    )
                    self.stdout.write(f"  ✅ {user.username} suit maintenant {company.name}")
                    new_count += 1
        
        self.stdout.write(f"📊 {new_count} nouveaux suivis créés")
