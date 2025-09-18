from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class JobCategory(models.Model):
    """Catégorie d'emploi"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Catégorie d\'emploi'
        verbose_name_plural = 'Catégories d\'emploi'
        ordering = ['name']

    def __str__(self):
        return self.name


class Job(models.Model):
    """Offre d'emploi"""
    JOB_TYPES = (
        ('full_time', 'Temps plein'),
        ('part_time', 'Temps partiel'),
        ('contract', 'Contrat'),
        ('cdd', 'CDD'),
        ('cdi', 'CDI'),
        ('freelance', 'Freelance'),
        ('internship', 'Stage'),
        ('temporary', 'Temporaire'),
        ('apprenticeship', 'Apprentissage'),
        ('volunteer', 'Bénévolat'),
        ('seasonal', 'Saisonnier'),
    )
    
    EXPERIENCE_LEVELS = (
        ('entry', 'Débutant (0-2 ans)'),
        ('junior', 'Junior (2-5 ans)'),
        ('mid', 'Intermédiaire (5-8 ans)'),
        ('senior', 'Senior (8+ ans)'),
        ('lead', 'Lead/Manager'),
        ('principal', 'Principal'),
        ('director', 'Directeur'),
        ('executive', 'Exécutif'),
        ('c_level', 'C-Level'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('paused', 'En pause'),
        ('closed', 'Fermé'),
        ('filled', 'Pourvu'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé'),
    )
    
    COMPANY_SIZES = (
        ('startup', 'Startup (1-10)'),
        ('small', 'Petite (11-50)'),
        ('medium', 'Moyenne (51-200)'),
        ('large', 'Grande (201-1000)'),
        ('enterprise', 'Entreprise (1000+)'),
    )
    
    WORK_ENVIRONMENTS = (
        ('office', 'Bureau'),
        ('remote', 'Télétravail'),
        ('hybrid', 'Hybride'),
        ('field', 'Terrain'),
        ('travel', 'Déplacements'),
    )

    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZES, blank=True)
    company_description = models.TextField(blank=True)
    company_website = models.URLField(blank=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='jobs')
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS)
    work_environment = models.CharField(max_length=20, choices=WORK_ENVIRONMENTS, default='office')
    
    # Localisation
    location = models.CharField(max_length=200)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    remote_work = models.BooleanField(default=False)
    travel_required = models.BooleanField(default=False)
    travel_percentage = models.PositiveIntegerField(blank=True, null=True, help_text='% de déplacements')
    
    # Description
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField()
    benefits = models.TextField(blank=True)
    company_culture = models.TextField(blank=True)
    growth_opportunities = models.TextField(blank=True)
    
    # Équipe et environnement
    team_size = models.PositiveIntegerField(blank=True, null=True)
    reports_to = models.CharField(max_length=200, blank=True)
    manages_team = models.BooleanField(default=False)
    department = models.CharField(max_length=100, blank=True)
    
    # Salaire
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_currency = models.CharField(max_length=3, default='EUR')
    salary_period = models.CharField(max_length=20, choices=[
        ('hour', 'Par heure'),
        ('day', 'Par jour'),
        ('week', 'Par semaine'),
        ('month', 'Par mois'),
        ('year', 'Par an'),
    ], default='year')
    salary_negotiable = models.BooleanField(default=True)
    bonus_structure = models.TextField(blank=True)
    equity_offered = models.BooleanField(default=False)
    
    # Métadonnées
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False)
    urgent = models.BooleanField(default=False)
    confidential = models.BooleanField(default=False, help_text='Masquer le nom de l\'entreprise')
    
    # Processus de recrutement
    interview_process = models.TextField(blank=True, help_text='Description du processus d\'entretien')
    number_of_positions = models.PositiveIntegerField(default=1)
    application_questions = models.JSONField(default=list, blank=True, help_text='Questions personnalisées')
    
    # Dates
    application_deadline = models.DateTimeField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    posted_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Gestion
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_jobs')
    assigned_recruiters = models.ManyToManyField(User, blank=True, related_name='assigned_jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SEO
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    
    # Statistiques
    views_count = models.PositiveIntegerField(default=0)
    applications_count = models.PositiveIntegerField(default=0)
    saves_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Offre d\'emploi'
        verbose_name_plural = 'Offres d\'emploi'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.company}"

    def get_absolute_url(self):
        return reverse('jobs:job_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            self.slug = f"{slugify(self.title)}-{str(uuid.uuid4())[:8]}"
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Vérifie si l'offre est encore active"""
        if self.status != 'published':
            return False
        if self.application_deadline and self.application_deadline < timezone.now():
            return False
        return True

    @property
    def salary_range(self):
        """Retourne la fourchette de salaire formatée"""
        if self.salary_min and self.salary_max:
            return f"{self.salary_min} - {self.salary_max} {self.salary_currency}"
        elif self.salary_min:
            return f"À partir de {self.salary_min} {self.salary_currency}"
        elif self.salary_max:
            return f"Jusqu'à {self.salary_max} {self.salary_currency}"
        return "Salaire à négocier"

    def increment_views(self):
        """Incrémenter le nombre de vues"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def increment_applications(self):
        """Incrémenter le nombre de candidatures"""
        self.applications_count += 1
        self.save(update_fields=['applications_count'])


class JobSkill(models.Model):
    """Compétences requises pour un emploi"""
    SKILL_LEVELS = (
        ('required', 'Requis'),
        ('preferred', 'Souhaité'),
        ('nice_to_have', 'Un plus'),
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='required_skills')
    skill_name = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=SKILL_LEVELS, default='required')
    years_required = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Compétence requise'
        verbose_name_plural = 'Compétences requises'
        unique_together = ['job', 'skill_name']

    def __str__(self):
        return f"{self.skill_name} ({self.get_level_display()})"


class SavedJob(models.Model):
    """Emplois sauvegardés par les candidats"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Emploi sauvegardé'
        verbose_name_plural = 'Emplois sauvegardés'
        unique_together = ['user', 'job']

    def __str__(self):
        return f"{self.user.full_name} - {self.job.title}"


class JobAlert(models.Model):
    """Alertes emploi pour les candidats"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_alerts')
    title = models.CharField(max_length=200)
    keywords = models.CharField(max_length=500, blank=True)
    location = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, blank=True, null=True)
    job_type = models.CharField(max_length=20, choices=Job.JOB_TYPES, blank=True)
    experience_level = models.CharField(max_length=20, choices=Job.EXPERIENCE_LEVELS, blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    remote_work = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    email_frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
    ], default='weekly')
    created_at = models.DateTimeField(auto_now_add=True)
    last_sent = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Alerte emploi'
        verbose_name_plural = 'Alertes emploi'
        ordering = ['-created_at']

    def __str__(self):
        return f"Alerte: {self.title} - {self.user.full_name}"