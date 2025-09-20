from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ContactMessage(models.Model):
    """Messages de contact"""
    SUBJECT_CHOICES = (
        ('general', 'Question générale'),
        ('technical', 'Problème technique'),
        ('account', 'Problème de compte'),
        ('job', 'Question sur une offre'),
        ('application', 'Question sur une candidature'),
        ('other', 'Autre'),
    )
    
    STATUS_CHOICES = (
        ('new', 'Nouveau'),
        ('in_progress', 'En cours'),
        ('resolved', 'Résolu'),
        ('closed', 'Fermé'),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField()
    
    # Gestion
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_messages')
    response = models.TextField(blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Message de contact'
        verbose_name_plural = 'Messages de contact'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_subject_display()}"


class FAQ(models.Model):
    """Questions fréquemment posées"""
    CATEGORIES = (
        ('general', 'Général'),
        ('account', 'Compte utilisateur'),
        ('jobs', 'Offres d\'emploi'),
        ('applications', 'Candidatures'),
        ('technical', 'Technique'),
    )

    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORIES)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['category', 'order', 'question']

    def __str__(self):
        return self.question


class SiteSettings(models.Model):
    """Paramètres du site"""
    site_name = models.CharField(max_length=100, default='Plateforme de Recrutement')
    site_description = models.TextField(default='Plateforme complète de gestion de recrutement')
    site_logo = models.ImageField(upload_to='site/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)
    contact_email = models.EmailField(default='contact@recruitment-platform.com')
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # Pages dynamiques
    about_title = models.CharField(max_length=200, default='À propos de nous')
    about_content = models.TextField(blank=True)
    about_mission = models.TextField(blank=True)
    about_vision = models.TextField(blank=True)
    about_values = models.TextField(blank=True)
    
    # Page d'accueil
    hero_title = models.CharField(max_length=200, default='Trouvez votre emploi idéal')
    hero_subtitle = models.TextField(default='Découvrez des milliers d\'opportunités')
    hero_image = models.ImageField(upload_to='site/', blank=True, null=True)
    
    # Personnalisation visuelle
    primary_color = models.CharField(max_length=7, default='#007bff', help_text='Couleur principale (hex)')
    secondary_color = models.CharField(max_length=7, default='#6c757d', help_text='Couleur secondaire (hex)')
    success_color = models.CharField(max_length=7, default='#28a745', help_text='Couleur de succès (hex)')
    warning_color = models.CharField(max_length=7, default='#ffc107', help_text='Couleur d\'avertissement (hex)')
    danger_color = models.CharField(max_length=7, default='#dc3545', help_text='Couleur de danger (hex)')
    
    # Thème
    theme_style = models.CharField(max_length=20, choices=[
        ('light', 'Clair'),
        ('dark', 'Sombre'),
        ('auto', 'Automatique'),
    ], default='light')
    
    # Footer
    footer_text = models.TextField(blank=True)
    show_social_links = models.BooleanField(default=True)
    
    # Réseaux sociaux
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    
    # Paramètres de candidature
    max_applications_per_day = models.PositiveIntegerField(default=5)
    application_deadline_days = models.PositiveIntegerField(default=30)
    auto_reject_after_days = models.PositiveIntegerField(default=90, help_text='Rejet automatique après X jours')
    enable_auto_matching = models.BooleanField(default=True)
    matching_threshold = models.PositiveIntegerField(default=70, help_text='Seuil de matching en %')
    
    # Paramètres d'email
    email_notifications_enabled = models.BooleanField(default=True)
    admin_notification_email = models.EmailField(blank=True)
    email_signature = models.TextField(blank=True)
    
    # Maintenance
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)
    
    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True)
    enable_tracking = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paramètres du site'
        verbose_name_plural = 'Paramètres du site'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule instance
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('Il ne peut y avoir qu\'une seule instance de SiteSettings')
        super().save(*args, **kwargs)


class Newsletter(models.Model):
    """Abonnements à la newsletter"""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Abonnement Newsletter'
        verbose_name_plural = 'Abonnements Newsletter'
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


class BlogPost(models.Model):
    """Articles de blog"""
    STATUS_CHOICES = (
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('archived', 'Archivé'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=500, blank=True)
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    
    # Métadonnées
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    tags = models.CharField(max_length=200, blank=True, help_text='Tags séparés par des virgules')
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Statistiques
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Article de blog'
        verbose_name_plural = 'Articles de blog'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('core:blog_detail', kwargs={'slug': self.slug})


class PageContent(models.Model):
    """Contenu des pages dynamiques"""
    PAGE_TYPES = (
        ('about', 'À propos'),
        ('privacy', 'Politique de confidentialité'),
        ('terms', 'Conditions d\'utilisation'),
        ('faq', 'FAQ'),
        ('contact', 'Contact'),
        ('home', 'Accueil'),
        ('hero_section', 'Section héro'),
        ('footer_content', 'Contenu du footer'),
        ('career_tips', 'Conseils de carrière'),  # NOUVEAU
        ('promotional', 'Contenu promotionnel'),  # NOUVEAU
        ('custom', 'Page personnalisée'),
    )

    page_type = models.CharField(max_length=20, choices=PAGE_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    show_in_menu = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    # SEO
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Contenu de page'
        verbose_name_plural = 'Contenus de pages'
        ordering = ['order', 'title']
        unique_together = [['page_type', 'slug']]

    def __str__(self):
        return f"{self.get_page_type_display()} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            base_slug = slugify(self.title) or self.page_type
            self.slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        super().save(*args, **kwargs)


class ThemeSettings(models.Model):
    """Paramètres de thème et personnalisation"""
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=False)
    
    # Couleurs principales
    primary_color = models.CharField(max_length=7, default='#007bff')
    secondary_color = models.CharField(max_length=7, default='#6c757d')
    success_color = models.CharField(max_length=7, default='#28a745')
    info_color = models.CharField(max_length=7, default='#17a2b8')
    warning_color = models.CharField(max_length=7, default='#ffc107')
    danger_color = models.CharField(max_length=7, default='#dc3545')
    light_color = models.CharField(max_length=7, default='#f8f9fa')
    dark_color = models.CharField(max_length=7, default='#343a40')
    
    # Typographie
    font_family = models.CharField(max_length=100, default='Segoe UI, system-ui, sans-serif')
    font_size_base = models.PositiveIntegerField(default=16, help_text='Taille de police de base en px')
    
    # Layout
    border_radius = models.PositiveIntegerField(default=6, help_text='Rayon des bordures en px')
    container_max_width = models.PositiveIntegerField(default=1200, help_text='Largeur max du container en px')
    
    # CSS personnalisé
    custom_css = models.TextField(blank=True, help_text='CSS personnalisé')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Thème'
        verbose_name_plural = 'Thèmes'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            # Désactiver les autres thèmes
            ThemeSettings.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)




class TeamMember(models.Model):
    """Membres de l'équipe"""
    ROLE_CHOICES = (
        ('management', 'Direction'),
        ('technical', 'Technique'),
        ('hr', 'Ressources Humaines'),
        ('marketing', 'Marketing'),
        ('sales', 'Commercial'),
        ('support', 'Support'),
        ('other', 'Autre'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='team_member')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    show_in_team = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Membre d\'équipe'
        verbose_name_plural = 'Membres d\'équipe'
        ordering = ['order', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"


class Value(models.Model):
    """Vales de l'entreprise"""
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text='Classe FontAwesome (ex: fas fa-heart)')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Valeur'
        verbose_name_plural = 'Valeurs'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class Statistic(models.Model):
    """Statistiques pour la page about"""
    title = models.CharField(max_length=100)
    value = models.PositiveIntegerField(default=0)
    icon = models.CharField(max_length=50, help_text='Classe FontAwesome (ex: fas fa-users)')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Statistique'
        verbose_name_plural = 'Statistiques'
        ordering = ['order', 'title']

    def __str__(self):
        return f"{self.title}: {self.value}"