from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import json

User = get_user_model()


class CVTemplate(models.Model):
    """Modèle pour les modèles de CV"""
    TEMPLATE_CATEGORY_CHOICES = [
        ('modern', 'Moderne'),
        ('classic', 'Classique'),
        ('creative', 'Créatif'),
        ('minimalist', 'Minimaliste'),
        ('professional', 'Professionnel'),
        ('academic', 'Académique'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nom du modèle')
    description = models.TextField(blank=True, verbose_name='Description')
    category = models.CharField(max_length=20, choices=TEMPLATE_CATEGORY_CHOICES, verbose_name='Catégorie')
    preview_image = models.ImageField(upload_to='cv_templates/previews/', verbose_name='Image de prévisualisation')
    template_file = models.FileField(upload_to='cv_templates/files/', verbose_name='Fichier de modèle')
    css_file = models.FileField(upload_to='cv_templates/css/', verbose_name='Fichier CSS')
    
    # Configuration du modèle
    sections = models.JSONField(default=list, verbose_name='Sections disponibles')  # ['personal_info', 'experience', 'education', 'skills', 'projects', 'languages', 'certifications', 'references']
    layout_config = models.JSONField(default=dict, verbose_name='Configuration de mise en page')
    color_scheme = models.JSONField(default=dict, verbose_name='Schéma de couleurs')
    
    # Métadonnées
    is_premium = models.BooleanField(default=False, verbose_name='Modèle premium')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Modèle de CV'
        verbose_name_plural = 'Modèles de CV'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CV(models.Model):
    """Modèle pour les CV créés par les utilisateurs"""
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('archived', 'Archivé'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cvs', verbose_name='Utilisateur')
    template = models.ForeignKey(CVTemplate, on_delete=models.CASCADE, related_name='cvs', verbose_name='Modèle')
    
    # Informations de base
    title = models.CharField(max_length=200, verbose_name='Titre du CV')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Statut')
    
    # Contenu du CV
    personal_info = models.JSONField(default=dict, verbose_name='Informations personnelles')
    professional_summary = models.TextField(blank=True, verbose_name='Résumé professionnel')
    experience = models.JSONField(default=list, verbose_name='Expériences professionnelles')
    education = models.JSONField(default=list, verbose_name='Formation')
    skills = models.JSONField(default=list, verbose_name='Compétences')
    projects = models.JSONField(default=list, verbose_name='Projets')
    languages = models.JSONField(default=list, verbose_name='Langues')
    certifications = models.JSONField(default=list, verbose_name='Certifications')
    references = models.JSONField(default=list, verbose_name='Références')
    additional_sections = models.JSONField(default=list, verbose_name='Sections supplémentaires')
    
    # Personnalisation
    custom_colors = models.JSONField(default=dict, verbose_name='Couleurs personnalisées')
    custom_fonts = models.JSONField(default=dict, verbose_name='Polices personnalisées')
    layout_settings = models.JSONField(default=dict, verbose_name='Paramètres de mise en page')
    
    # Métadonnées
    is_public = models.BooleanField(default=False, verbose_name='Public')
    view_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de vues')
    download_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de téléchargements')
    last_modified = models.DateTimeField(auto_now=True, verbose_name='Dernière modification')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'CV'
        verbose_name_plural = 'CVs'
        ordering = ['-last_modified']
    
    def __str__(self):
        return f"{self.title} - {self.user.full_name}"
    
    def get_absolute_url(self):
        return f"/cv-builder/cv/{self.id}/"
    
    def get_preview_url(self):
        return f"/cv-builder/cv/{self.id}/preview/"
    
    def get_download_url(self):
        return f"/cv-builder/cv/{self.id}/download/"


class CVSection(models.Model):
    """Modèle pour les sections personnalisées de CV"""
    SECTION_TYPE_CHOICES = [
        ('custom', 'Personnalisée'),
        ('achievements', 'Réalisations'),
        ('publications', 'Publications'),
        ('volunteer', 'Bénévolat'),
        ('interests', 'Centres d\'intérêt'),
        ('awards', 'Prix et distinctions'),
    ]
    
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='custom_sections', verbose_name='CV')
    section_type = models.CharField(max_length=20, choices=SECTION_TYPE_CHOICES, default='custom', verbose_name='Type de section')
    title = models.CharField(max_length=100, verbose_name='Titre de la section')
    content = models.JSONField(default=list, verbose_name='Contenu de la section')
    order = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')
    is_visible = models.BooleanField(default=True, verbose_name='Visible')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Section de CV'
        verbose_name_plural = 'Sections de CV'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.title} - {self.cv.title}"


class CVShare(models.Model):
    """Modèle pour le partage de CV"""
    SHARE_TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Privé'),
        ('password', 'Protégé par mot de passe'),
        ('expiring', 'Expirant'),
    ]
    
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='shares', verbose_name='CV')
    share_type = models.CharField(max_length=20, choices=SHARE_TYPE_CHOICES, default='private', verbose_name='Type de partage')
    share_url = models.CharField(max_length=255, unique=True, verbose_name='URL de partage')
    password = models.CharField(max_length=100, blank=True, verbose_name='Mot de passe')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Expire le')
    
    # Statistiques
    view_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de vues')
    download_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de téléchargements')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Partage de CV'
        verbose_name_plural = 'Partages de CV'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Partage de {self.cv.title}"
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class CVExport(models.Model):
    """Modèle pour les exports de CV"""
    EXPORT_FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'Word (DOCX)'),
        ('html', 'HTML'),
        ('txt', 'Texte'),
    ]
    
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='exports', verbose_name='CV')
    export_format = models.CharField(max_length=10, choices=EXPORT_FORMAT_CHOICES, verbose_name='Format d\'export')
    file_path = models.CharField(max_length=500, verbose_name='Chemin du fichier')
    file_size = models.PositiveIntegerField(verbose_name='Taille du fichier (bytes)')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Export de CV'
        verbose_name_plural = 'Exports de CV'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Export {self.export_format} de {self.cv.title}"


class CVAnalytics(models.Model):
    """Modèle pour les analytics des CV"""
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='analytics', verbose_name='CV')
    date = models.DateField(verbose_name='Date')
    
    # Statistiques
    views = models.PositiveIntegerField(default=0, verbose_name='Vues')
    downloads = models.PositiveIntegerField(default=0, verbose_name='Téléchargements')
    shares = models.PositiveIntegerField(default=0, verbose_name='Partages')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Analytics de CV'
        verbose_name_plural = 'Analytics de CV'
        unique_together = ['cv', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics de {self.cv.title} - {self.date}"


class CVFeedback(models.Model):
    """Modèle pour les commentaires sur les CV"""
    RATING_CHOICES = [
        (1, '1 étoile'),
        (2, '2 étoiles'),
        (3, '3 étoiles'),
        (4, '4 étoiles'),
        (5, '5 étoiles'),
    ]
    
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='feedbacks', verbose_name='CV')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cv_feedbacks', verbose_name='Évaluateur')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, verbose_name='Note')
    comment = models.TextField(blank=True, verbose_name='Commentaire')
    
    # Métadonnées
    is_public = models.BooleanField(default=False, verbose_name='Public')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Commentaire de CV'
        verbose_name_plural = 'Commentaires de CV'
        unique_together = ['cv', 'reviewer']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Commentaire de {self.reviewer.full_name} sur {self.cv.title}"


class CVTemplateCategory(models.Model):
    """Modèle pour les catégories de modèles de CV"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Nom de la catégorie')
    description = models.TextField(blank=True, verbose_name='Description')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Icône')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Couleur')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Catégorie de modèle de CV'
        verbose_name_plural = 'Catégories de modèles de CV'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CVBuilderSettings(models.Model):
    """Modèle pour les paramètres du constructeur de CV"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cv_builder_settings', verbose_name='Utilisateur')
    
    # Paramètres d'interface
    default_template = models.ForeignKey(CVTemplate, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Modèle par défaut')
    auto_save = models.BooleanField(default=True, verbose_name='Sauvegarde automatique')
    auto_save_interval = models.PositiveIntegerField(default=30, verbose_name='Intervalle de sauvegarde (secondes)')
    
    # Paramètres d'export
    default_export_format = models.CharField(max_length=10, choices=CVExport.EXPORT_FORMAT_CHOICES, default='pdf', verbose_name='Format d\'export par défaut')
    include_contact_info = models.BooleanField(default=True, verbose_name='Inclure les informations de contact')
    include_photo = models.BooleanField(default=True, verbose_name='Inclure la photo')
    
    # Paramètres de partage
    default_share_type = models.CharField(max_length=20, choices=CVShare.SHARE_TYPE_CHOICES, default='private', verbose_name='Type de partage par défaut')
    share_expiry_days = models.PositiveIntegerField(default=30, verbose_name='Durée de partage (jours)')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Paramètres du constructeur de CV'
        verbose_name_plural = 'Paramètres du constructeur de CV'
    
    def __str__(self):
        return f"Paramètres CV de {self.user.full_name}"