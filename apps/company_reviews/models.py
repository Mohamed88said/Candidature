from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import json

User = get_user_model()


class Company(models.Model):
    """Modèle pour les entreprises"""
    name = models.CharField(max_length=200, verbose_name='Nom de l\'entreprise')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    description = models.TextField(blank=True, verbose_name='Description')
    website = models.URLField(blank=True, verbose_name='Site web')
    industry = models.CharField(max_length=100, blank=True, verbose_name='Secteur d\'activité')
    size = models.CharField(max_length=50, blank=True, verbose_name='Taille de l\'entreprise')
    founded_year = models.PositiveIntegerField(null=True, blank=True, verbose_name='Année de fondation')
    headquarters = models.CharField(max_length=200, blank=True, verbose_name='Siège social')
    
    # Informations de contact
    email = models.EmailField(blank=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    
    # Logo et images
    logo = models.ImageField(upload_to='companies/logos/', blank=True, verbose_name='Logo')
    cover_image = models.ImageField(upload_to='companies/covers/', blank=True, verbose_name='Image de couverture')
    
    # Métadonnées
    is_verified = models.BooleanField(default=False, verbose_name='Vérifiée')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Entreprise'
        verbose_name_plural = 'Entreprises'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return f"/companies/{self.slug}/"
    
    def get_average_rating(self):
        """Calculer la note moyenne"""
        from django.db.models import Avg
        return self.reviews.filter(is_approved=True).aggregate(
            avg_rating=Avg('overall_rating')
        )['avg_rating'] or 0
    
    def get_review_count(self):
        """Compter le nombre d'avis approuvés"""
        return self.reviews.filter(is_approved=True).count()
    
    def get_rating_distribution(self):
        """Obtenir la distribution des notes"""
        from django.db.models import Count
        distribution = self.reviews.filter(is_approved=True).values('overall_rating').annotate(
            count=Count('id')
        ).order_by('overall_rating')
        
        result = {i: 0 for i in range(1, 6)}
        for item in distribution:
            result[item['overall_rating']] = item['count']
        
        return result


class CompanyReview(models.Model):
    """Modèle pour les avis sur les entreprises"""
    RATING_CHOICES = [
        (1, '1 étoile'),
        (2, '2 étoiles'),
        (3, '3 étoiles'),
        (4, '4 étoiles'),
        (5, '5 étoiles'),
    ]
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('current', 'Employé actuel'),
        ('former', 'Ancien employé'),
        ('contractor', 'Prestataire'),
        ('intern', 'Stagiaire'),
        ('other', 'Autre'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='reviews', verbose_name='Entreprise')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_reviews', verbose_name='Utilisateur')
    
    # Informations sur l'emploi
    job_title = models.CharField(max_length=200, verbose_name='Poste occupé')
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, verbose_name='Statut d\'emploi')
    employment_start_date = models.DateField(verbose_name='Date de début')
    employment_end_date = models.DateField(null=True, blank=True, verbose_name='Date de fin')
    is_current_employee = models.BooleanField(default=False, verbose_name='Employé actuel')
    
    # Notes détaillées
    overall_rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Note globale'
    )
    work_life_balance = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Équilibre vie professionnelle/personnelle'
    )
    salary_benefits = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Salaire et avantages'
    )
    job_security = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Sécurité de l\'emploi'
    )
    management = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Management'
    )
    culture = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Culture d\'entreprise'
    )
    career_opportunities = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Opportunités de carrière'
    )
    
    # Contenu de l'avis
    pros = models.TextField(verbose_name='Points positifs')
    cons = models.TextField(verbose_name='Points négatifs')
    advice_to_management = models.TextField(blank=True, verbose_name='Conseils à la direction')
    
    # Recommandation
    would_recommend = models.BooleanField(verbose_name='Recommanderait cette entreprise')
    
    # Statut
    is_approved = models.BooleanField(default=False, verbose_name='Approuvé')
    is_anonymous = models.BooleanField(default=False, verbose_name='Anonyme')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Avis sur l\'entreprise'
        verbose_name_plural = 'Avis sur les entreprises'
        ordering = ['-created_at']
        unique_together = ['company', 'user']
    
    def __str__(self):
        return f"Avis de {self.user.full_name} sur {self.company.name}"
    
    def get_average_detailed_rating(self):
        """Calculer la moyenne des notes détaillées"""
        ratings = [
            self.work_life_balance,
            self.salary_benefits,
            self.job_security,
            self.management,
            self.culture,
            self.career_opportunities
        ]
        return sum(ratings) / len(ratings)
    
    def clean(self):
        super().clean()
        if self.employment_end_date and self.employment_start_date and self.employment_end_date < self.employment_start_date:
            raise ValidationError('La date de fin ne peut pas être antérieure à la date de début.')


class ReviewHelpful(models.Model):
    """Modèle pour les votes "utile" sur les avis"""
    review = models.ForeignKey(CompanyReview, on_delete=models.CASCADE, related_name='helpful_votes', verbose_name='Avis')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_helpful_votes', verbose_name='Utilisateur')
    is_helpful = models.BooleanField(verbose_name='Utile')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Vote utile'
        verbose_name_plural = 'Votes utiles'
        unique_together = ['review', 'user']
    
    def __str__(self):
        return f"Vote de {self.user.full_name} sur l'avis de {self.review.user.full_name}"


class ReviewResponse(models.Model):
    """Modèle pour les réponses des entreprises aux avis"""
    review = models.OneToOneField(CompanyReview, on_delete=models.CASCADE, related_name='company_response', verbose_name='Avis')
    company_representative = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_responses', verbose_name='Représentant de l\'entreprise')
    response_text = models.TextField(verbose_name='Réponse')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Réponse d\'entreprise'
        verbose_name_plural = 'Réponses d\'entreprises'
    
    def __str__(self):
        return f"Réponse de {self.company_representative.full_name} à l'avis de {self.review.user.full_name}"


class CompanySalary(models.Model):
    """Modèle pour les informations salariales"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='salaries', verbose_name='Entreprise')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salary_reports', verbose_name='Utilisateur')
    
    # Informations sur le poste
    job_title = models.CharField(max_length=200, verbose_name='Poste')
    department = models.CharField(max_length=100, blank=True, verbose_name='Département')
    location = models.CharField(max_length=200, blank=True, verbose_name='Localisation')
    
    # Informations salariales
    base_salary = models.PositiveIntegerField(verbose_name='Salaire de base')
    bonus = models.PositiveIntegerField(default=0, verbose_name='Prime')
    total_compensation = models.PositiveIntegerField(verbose_name='Rémunération totale')
    currency = models.CharField(max_length=3, default='EUR', verbose_name='Devise')
    
    # Informations sur l'emploi
    employment_type = models.CharField(max_length=50, verbose_name='Type d\'emploi')
    experience_level = models.CharField(max_length=50, verbose_name='Niveau d\'expérience')
    years_at_company = models.PositiveIntegerField(verbose_name='Années dans l\'entreprise')
    
    # Statut
    is_approved = models.BooleanField(default=False, verbose_name='Approuvé')
    is_anonymous = models.BooleanField(default=False, verbose_name='Anonyme')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Information salariale'
        verbose_name_plural = 'Informations salariales'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Salaire de {self.user.full_name} chez {self.company.name}"


class CompanyInterview(models.Model):
    """Modèle pour les expériences d'entretien"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Facile'),
        ('average', 'Moyen'),
        ('difficult', 'Difficile'),
        ('very_difficult', 'Très difficile'),
    ]
    
    OUTCOME_CHOICES = [
        ('accepted', 'Accepté'),
        ('rejected', 'Refusé'),
        ('no_response', 'Pas de réponse'),
        ('withdrew', 'Retiré'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='interviews', verbose_name='Entreprise')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_experiences', verbose_name='Utilisateur')
    
    # Informations sur le poste
    job_title = models.CharField(max_length=200, verbose_name='Poste')
    department = models.CharField(max_length=100, blank=True, verbose_name='Département')
    
    # Informations sur l'entretien
    interview_date = models.DateField(verbose_name='Date de l\'entretien')
    interview_type = models.CharField(max_length=100, verbose_name='Type d\'entretien')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, verbose_name='Difficulté')
    duration = models.PositiveIntegerField(verbose_name='Durée (minutes)')
    
    # Questions et processus
    interview_questions = models.TextField(verbose_name='Questions posées')
    interview_process = models.TextField(verbose_name='Processus d\'entretien')
    
    # Résultat
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, verbose_name='Résultat')
    offer_made = models.BooleanField(default=False, verbose_name='Offre faite')
    offer_amount = models.PositiveIntegerField(null=True, blank=True, verbose_name='Montant de l\'offre')
    
    # Avis
    overall_experience = models.PositiveIntegerField(
        choices=CompanyReview.RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Expérience globale'
    )
    pros = models.TextField(verbose_name='Points positifs')
    cons = models.TextField(verbose_name='Points négatifs')
    advice = models.TextField(blank=True, verbose_name='Conseils')
    
    # Statut
    is_approved = models.BooleanField(default=False, verbose_name='Approuvé')
    is_anonymous = models.BooleanField(default=False, verbose_name='Anonyme')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Expérience d\'entretien'
        verbose_name_plural = 'Expériences d\'entretien'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Entretien de {self.user.full_name} chez {self.company.name}"


class CompanyBenefit(models.Model):
    """Modèle pour les avantages des entreprises"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='benefits', verbose_name='Entreprise')
    name = models.CharField(max_length=200, verbose_name='Nom de l\'avantage')
    description = models.TextField(blank=True, verbose_name='Description')
    category = models.CharField(max_length=100, verbose_name='Catégorie')
    is_available = models.BooleanField(default=True, verbose_name='Disponible')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Avantage d\'entreprise'
        verbose_name_plural = 'Avantages d\'entreprises'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"


class CompanyPhoto(models.Model):
    """Modèle pour les photos des entreprises"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='photos', verbose_name='Entreprise')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_photos', verbose_name='Utilisateur')
    photo = models.ImageField(upload_to='companies/photos/', verbose_name='Photo')
    caption = models.CharField(max_length=200, blank=True, verbose_name='Légende')
    is_approved = models.BooleanField(default=False, verbose_name='Approuvée')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Photo d\'entreprise'
        verbose_name_plural = 'Photos d\'entreprises'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Photo de {self.company.name} par {self.user.full_name}"


class CompanyFollow(models.Model):
    """Modèle pour suivre les entreprises"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_companies', verbose_name='Utilisateur')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='followers', verbose_name='Entreprise')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Suivi d\'entreprise'
        verbose_name_plural = 'Suivis d\'entreprises'
        unique_together = ['user', 'company']
    
    def __str__(self):
        return f"{self.user.full_name} suit {self.company.name}"