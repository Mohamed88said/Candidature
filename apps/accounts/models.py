from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from PIL import Image


class User(AbstractUser):
    """Modèle utilisateur personnalisé"""
    USER_TYPES = (
        ('candidate', 'Candidat'),
        ('admin', 'Administrateur'),
        ('hr', 'Ressources Humaines'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='candidate')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class CandidateProfile(models.Model):
    """Profil détaillé du candidat"""
    GENDER_CHOICES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('O', 'Autre'),
    )
    
    MARITAL_STATUS_CHOICES = (
        ('single', 'Célibataire'),
        ('married', 'Marié(e)'),
        ('divorced', 'Divorcé(e)'),
        ('widowed', 'Veuf/Veuve'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    
    # Informations personnelles
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    
    # Adresse
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Contact
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
    mobile_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    linkedin_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    
    # Informations professionnelles
    current_position = models.CharField(max_length=200, blank=True)
    current_company = models.CharField(max_length=200, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0, help_text="Calculé automatiquement")
    years_of_relevant_experience = models.PositiveIntegerField(default=0, help_text="Expérience pertinente calculée")
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    availability_date = models.DateField(blank=True, null=True)
    
    # Documents
    cv_file = models.FileField(upload_to='cvs/', blank=True, null=True)
    cover_letter = models.FileField(upload_to='cover_letters/', blank=True, null=True)
    
    # Préférences
    willing_to_relocate = models.BooleanField(default=False)
    preferred_work_type = models.CharField(max_length=50, choices=[
        ('full_time', 'Temps plein'),
        ('part_time', 'Temps partiel'),
        ('contract', 'Contrat'),
        ('freelance', 'Freelance'),
        ('internship', 'Stage'),
    ], blank=True)
    
    # Métadonnées
    profile_completion = models.PositiveIntegerField(default=0)  # Pourcentage de completion
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profil Candidat'
        verbose_name_plural = 'Profils Candidats'

    def __str__(self):
        return f"Profil de {self.user.full_name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Redimensionner l'image de profil
        if self.profile_picture:
            img = Image.open(self.profile_picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_picture.path)

    def calculate_profile_completion(self):
        """Calcule le pourcentage de completion du profil"""
        fields = [
            self.profile_picture, self.date_of_birth, self.gender, self.nationality,
            self.address, self.city, self.country, self.mobile_phone,
            self.current_position, self.years_of_experience, self.cv_file
        ]
        completed_fields = sum(1 for field in fields if field)
        completion = (completed_fields / len(fields)) * 100
        self.profile_completion = int(completion)
        self.save(update_fields=['profile_completion'])
        return self.profile_completion

    def calculate_experience_years(self, target_position=None):
        """Calcule les années d'expérience totales et pertinentes"""
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        experiences = self.experiences.all().order_by('start_date')
        if not experiences:
            return 0, 0
        
        # Fusionner les périodes qui se chevauchent
        periods = []
        relevant_periods = []
        
        for exp in experiences:
            end_date = exp.end_date if exp.end_date else date.today()
            periods.append((exp.start_date, end_date))
            
            # Vérifier si l'expérience est pertinente
            if target_position and self._is_relevant_experience(exp.position, target_position):
                relevant_periods.append((exp.start_date, end_date))
        
        # Calculer les années totales sans chevauchement
        total_years = self._calculate_non_overlapping_years(periods)
        relevant_years = self._calculate_non_overlapping_years(relevant_periods) if target_position else 0
        
        # Mettre à jour les champs
        self.years_of_experience = total_years
        if target_position:
            self.years_of_relevant_experience = relevant_years
        self.save(update_fields=['years_of_experience', 'years_of_relevant_experience'])
        
        return total_years, relevant_years
    
    def _calculate_non_overlapping_years(self, periods):
        """Calcule les années sans chevauchement"""
        if not periods:
            return 0
        
        # Trier par date de début
        periods = sorted(periods, key=lambda x: x[0])
        
        # Fusionner les périodes qui se chevauchent
        merged = [periods[0]]
        for current in periods[1:]:
            last = merged[-1]
            if current[0] <= last[1]:  # Chevauchement
                merged[-1] = (last[0], max(last[1], current[1]))
            else:
                merged.append(current)
        
        # Calculer le total en années
        total_days = sum((end - start).days for start, end in merged)
        return round(total_days / 365.25, 1)
    
    def _is_relevant_experience(self, position, target_position):
        """Vérifie si une expérience est pertinente pour un poste cible"""
        position_words = set(position.lower().split())
        target_words = set(target_position.lower().split())
        
        # Mots-clés techniques communs
        common_words = position_words.intersection(target_words)
        
        # Seuil de pertinence (au moins 1 mot-clé en commun)
        return len(common_words) > 0


class Education(models.Model):
    """Formation et parcours scolaire"""
    DEGREE_LEVELS = (
        ('high_school', 'Lycée'),
        ('bachelor', 'Licence/Bachelor'),
        ('master', 'Master'),
        ('phd', 'Doctorat'),
        ('certificate', 'Certificat'),
        ('diploma', 'Diplôme'),
        ('other', 'Autre'),
    )

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    degree_level = models.CharField(max_length=20, choices=DEGREE_LEVELS)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    grade = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Formation'
        verbose_name_plural = 'Formations'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Experience(models.Model):
    """Expérience professionnelle"""
    EMPLOYMENT_TYPES = (
        ('full_time', 'Temps plein'),
        ('part_time', 'Temps partiel'),
        ('contract', 'Contrat'),
        ('freelance', 'Freelance'),
        ('internship', 'Stage'),
        ('volunteer', 'Bénévolat'),
        ('apprenticeship', 'Apprentissage'),
    )
    
    COMPANY_SIZES = (
        ('startup', 'Startup (1-10)'),
        ('small', 'Petite (11-50)'),
        ('medium', 'Moyenne (51-200)'),
        ('large', 'Grande (201-1000)'),
        ('enterprise', 'Entreprise (1000+)'),
    )

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='full_time')
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZES, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    remote_work = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_currency = models.CharField(max_length=3, default='EUR')
    description = models.TextField()
    achievements = models.TextField(blank=True)
    technologies_used = models.TextField(blank=True, help_text='Technologies, outils, logiciels utilisés')
    team_size = models.PositiveIntegerField(blank=True, null=True, help_text='Taille de l\'équipe managée')
    budget_managed = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Expérience'
        verbose_name_plural = 'Expériences'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.position} chez {self.company}"
    
    @property
    def duration_in_years(self):
        """Calcule la durée en années"""
        from datetime import date
        end_date = self.end_date if self.end_date else date.today()
        duration = end_date - self.start_date
        return round(duration.days / 365.25, 1)
    
    @property
    def is_relevant_for_position(self, target_position):
        """Vérifie si cette expérience est pertinente pour un poste"""
        if not target_position:
            return False
        
        position_words = set(self.position.lower().split())
        target_words = set(target_position.lower().split())
        tech_words = set(self.technologies_used.lower().split()) if self.technologies_used else set()
        
        # Mots-clés communs
        common_words = position_words.intersection(target_words)
        tech_match = tech_words.intersection(target_words)
        
        return len(common_words) > 0 or len(tech_match) > 0


class Skill(models.Model):
    """Compétences"""
    SKILL_LEVELS = (
        ('beginner', 'Débutant'),
        ('basic', 'Basique'),
        ('intermediate', 'Intermédiaire'),
        ('advanced', 'Avancé'),
        ('expert', 'Expert'),
        ('master', 'Maître'),
    )
    
    SKILL_CATEGORIES = (
        ('technical', 'Technique'),
        ('programming', 'Programmation'),
        ('framework', 'Framework'),
        ('database', 'Base de données'),
        ('cloud', 'Cloud'),
        ('devops', 'DevOps'),
        ('design', 'Design'),
        ('marketing', 'Marketing'),
        ('sales', 'Vente'),
        ('management', 'Management'),
        ('finance', 'Finance'),
        ('legal', 'Juridique'),
        ('soft', 'Soft Skills'),
        ('communication', 'Communication'),
        ('leadership', 'Leadership'),
        ('tool', 'Outil'),
        ('certification', 'Certification'),
        ('other', 'Autre'),
    )

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=SKILL_LEVELS)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORIES)
    years_of_experience = models.PositiveIntegerField(default=0)
    is_certified = models.BooleanField(default=False)
    certification_name = models.CharField(max_length=200, blank=True)
    last_used = models.DateField(blank=True, null=True)
    proficiency_score = models.PositiveIntegerField(default=50, help_text='Score de 0 à 100')
    
    class Meta:
        verbose_name = 'Compétence'
        verbose_name_plural = 'Compétences'
        unique_together = ['candidate', 'name']

    def __str__(self):
        return f"{self.name} ({self.level})"


class Language(models.Model):
    """Langues parlées"""
    PROFICIENCY_LEVELS = (
        ('A1', 'A1 - Débutant'),
        ('A2', 'A2 - Élémentaire'),
        ('B1', 'B1 - Intermédiaire'),
        ('B2', 'B2 - Intermédiaire avancé'),
        ('C1', 'C1 - Avancé'),
        ('C2', 'C2 - Maîtrise'),
        ('native', 'Langue maternelle'),
    )

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='languages')
    language = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=10, choices=PROFICIENCY_LEVELS)
    
    class Meta:
        verbose_name = 'Langue'
        verbose_name_plural = 'Langues'
        unique_together = ['candidate', 'language']

    def __str__(self):
        return f"{self.language} ({self.proficiency})"


class Certification(models.Model):
    """Certifications et diplômes"""
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiration_date = models.DateField(blank=True, null=True)
    credential_id = models.CharField(max_length=100, blank=True)
    credential_url = models.URLField(blank=True)
    
    class Meta:
        verbose_name = 'Certification'
        verbose_name_plural = 'Certifications'
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.name} - {self.issuing_organization}"


class Reference(models.Model):
    """Références professionnelles"""
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='references')
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    relationship = models.CharField(max_length=100)  # Ex: "Ancien manager", "Collègue"
    
    class Meta:
        verbose_name = 'Référence'
        verbose_name_plural = 'Références'

    def __str__(self):
        return f"{self.name} - {self.position}"


class Project(models.Model):
    """Projets et réalisations"""
    PROJECT_TYPES = (
        ('professional', 'Professionnel'),
        ('personal', 'Personnel'),
        ('academic', 'Académique'),
        ('open_source', 'Open Source'),
        ('freelance', 'Freelance'),
    )
    
    STATUS_CHOICES = (
        ('completed', 'Terminé'),
        ('in_progress', 'En cours'),
        ('paused', 'En pause'),
        ('cancelled', 'Annulé'),
    )

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_ongoing = models.BooleanField(default=False)
    
    # Détails techniques
    technologies_used = models.TextField(blank=True)
    role = models.CharField(max_length=200, blank=True)
    team_size = models.PositiveIntegerField(blank=True, null=True)
    
    # Liens
    project_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    
    # Résultats
    achievements = models.TextField(blank=True)
    impact = models.TextField(blank=True, help_text='Impact business ou technique')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Projet'
        verbose_name_plural = 'Projets'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} ({self.get_project_type_display()})"


class SocialProfile(models.Model):
    """Profils sur les réseaux sociaux et plateformes professionnelles"""
    PLATFORM_CHOICES = (
        ('linkedin', 'LinkedIn'),
        ('github', 'GitHub'),
        ('stackoverflow', 'Stack Overflow'),
        ('behance', 'Behance'),
        ('dribbble', 'Dribbble'),
        ('medium', 'Medium'),
        ('twitter', 'Twitter'),
        ('personal_website', 'Site personnel'),
        ('portfolio', 'Portfolio'),
        ('other', 'Autre'),
    )

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='social_profiles')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    username = models.CharField(max_length=100, blank=True)
    url = models.URLField()
    is_public = models.BooleanField(default=True)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Profil Social'
        verbose_name_plural = 'Profils Sociaux'
        unique_together = ['candidate', 'platform']

    def __str__(self):
        return f"{self.get_platform_display()} - {self.candidate.user.full_name}"


class Award(models.Model):
    """Prix et reconnaissances"""
    AWARD_TYPES = (
        ('professional', 'Professionnel'),
        ('academic', 'Académique'),
        ('industry', 'Industrie'),
        ('community', 'Communauté'),
        ('innovation', 'Innovation'),
        ('leadership', 'Leadership'),
        ('other', 'Autre'),
    )

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='awards')
    title = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    award_type = models.CharField(max_length=20, choices=AWARD_TYPES)
    date_received = models.DateField()
    description = models.TextField(blank=True)
    certificate_url = models.URLField(blank=True)
    
    class Meta:
        verbose_name = 'Prix/Reconnaissance'
        verbose_name_plural = 'Prix/Reconnaissances'
        ordering = ['-date_received']

    def __str__(self):
        return f"{self.title} - {self.issuing_organization}"