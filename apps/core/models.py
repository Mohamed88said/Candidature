from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class ContactMessage(models.Model):
    """Messages de contact"""
    SUBJECT_CHOICES = (
        ('general', _('Question générale')),
        ('technical', _('Problème technique')),
        ('account', _('Problème de compte')),
        ('job', _('Question sur une offre')),
        ('application', _('Question sur une candidature')),
        ('other', _('Autre')),
    )
    
    STATUS_CHOICES = (
        ('new', _('Nouveau')),
        ('in_progress', _('En cours')),
        ('resolved', _('Résolu')),
        ('closed', _('Fermé')),
    )

    name = models.CharField(max_length=100, verbose_name=_('nom'))
    email = models.EmailField(verbose_name=_('email'))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('téléphone'))
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, verbose_name=_('sujet'))
    message = models.TextField(verbose_name=_('message'))
    
    # Gestion
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name=_('statut'))
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='assigned_messages', verbose_name=_('assigné à'))
    response = models.TextField(blank=True, verbose_name=_('réponse'))
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('créé le'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('modifié le'))
    responded_at = models.DateTimeField(null=True, blank=True, verbose_name=_('répondu le'))

    class Meta:
        verbose_name = _('Message de contact')
        verbose_name_plural = _('Messages de contact')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_subject_display()}"


class FAQ(models.Model):
    """Questions fréquemment posées"""
    CATEGORIES = (
        ('general', _('Général')),
        ('account', _('Compte utilisateur')),
        ('jobs', _('Offres d\'emploi')),
        ('applications', _('Candidatures')),
        ('technical', _('Technique')),
    )

    question = models.CharField(max_length=300, verbose_name=_('question'))
    answer = models.TextField(verbose_name=_('réponse'))
    category = models.CharField(max_length=20, choices=CATEGORIES, verbose_name=_('catégorie'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('ordre'))
    is_active = models.BooleanField(default=True, verbose_name=_('actif'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('créé le'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('modifié le'))

    class Meta:
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        ordering = ['category', 'order', 'question']

    def __str__(self):
        return self.question


class SiteSettings(models.Model):
    """Paramètres du site"""
    site_name = models.CharField(max_length=100, default='Plateforme de Recrutement Expert', 
                               verbose_name=_('nom du site'))
    site_description = models.TextField(default='Plateforme complète de gestion de recrutement et de mise en relation talents-entreprises', 
                                      verbose_name=_('description du site'))
    site_logo = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name=_('logo'))
    favicon = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name=_('favicon'))
    contact_email = models.EmailField(default='contact@recruitment-expert.com', verbose_name=_('email de contact'))
    contact_phone = models.CharField(max_length=20, default='+33 1 23 45 67 89', verbose_name=_('téléphone'))
    address = models.TextField(default='123 Avenue des Entreprises\n75001 Paris, France', verbose_name=_('adresse'))
    
    # Informations entreprise
    company_name = models.CharField(max_length=200, default='Recruitment Expert SAS', verbose_name=_('nom de l\'entreprise'))
    siret = models.CharField(max_length=14, blank=True, verbose_name=_('SIRET'))
    rcs = models.CharField(max_length=50, blank=True, verbose_name=_('RCS'))
    vat_number = models.CharField(max_length=20, blank=True, verbose_name=_('numéro de TVA'))
    
    # Pages dynamiques
    about_title = models.CharField(max_length=200, default='À propos de Recruitment Expert', verbose_name=_('titre à propos'))
    about_content = models.TextField(default='Recruitment Expert est une plateforme innovante de recrutement qui connecte les talents aux meilleures opportunités professionnelles. Fondée en 2020, notre mission est de révolutionner le marché de l\'emploi grâce à une approche technologique et humaine.', 
                                   verbose_name=_('contenu à propos'))
    about_mission = models.TextField(default='Notre mission est de simplifier et optimiser le processus de recrutement en offrant une plateforme intuitive qui met en relation les meilleurs talents avec les entreprises qui partagent leurs valeurs et ambitions.', 
                                   verbose_name=_('mission'))
    about_vision = models.TextField(default='Devenir la référence en matière de plateforme de recrutement en Europe, en créant des connexions durables entre talents et entreprises.', 
                                  verbose_name=_('vision'))
    about_values = models.TextField(default='Innovation, Transparence, Excellence, Collaboration, Diversité', 
                                  verbose_name=_('valeurs'))
    
    # Page d'accueil
    hero_title = models.CharField(max_length=200, default='Trouvez votre emploi idéal', verbose_name=_('titre hero'))
    hero_subtitle = models.TextField(default='Découvrez des milliers d\'opportunités d\'emploi et connectez-vous avec les meilleures entreprises. Votre carrière commence ici.', 
                                   verbose_name=_('sous-titre hero'))
    hero_image = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name=_('image hero'))
    
    # Personnalisation visuelle
    primary_color = models.CharField(max_length=7, default='#007bff', help_text=_('Couleur principale (hex)'))
    secondary_color = models.CharField(max_length=7, default='#6c757d', help_text=_('Couleur secondaire (hex)'))
    success_color = models.CharField(max_length=7, default='#28a745', help_text=_('Couleur de succès (hex)'))
    warning_color = models.CharField(max_length=7, default='#ffc107', help_text=_('Couleur d\'avertissement (hex)'))
    danger_color = models.CharField(max_length=7, default='#dc3545', help_text=_('Couleur de danger (hex)'))
    
    # Thème
    theme_style = models.CharField(max_length=20, choices=[
        ('light', _('Clair')),
        ('dark', _('Sombre')),
        ('auto', _('Automatique')),
    ], default='light', verbose_name=_('style de thème'))
    
    # Footer
    footer_text = models.TextField(default='© 2024 Recruitment Expert. Tous droits réservés.', verbose_name=_('texte du footer'))
    show_social_links = models.BooleanField(default=True, verbose_name=_('afficher liens sociaux'))
    
    # Réseaux sociaux
    facebook_url = models.URLField(blank=True, verbose_name=_('Facebook'))
    twitter_url = models.URLField(blank=True, verbose_name=_('Twitter'))
    linkedin_url = models.URLField(blank=True, verbose_name=_('LinkedIn'))
    instagram_url = models.URLField(blank=True, verbose_name=_('Instagram'))
    youtube_url = models.URLField(blank=True, verbose_name=_('YouTube'))
    
    # Paramètres de candidature
    max_applications_per_day = models.PositiveIntegerField(default=5, verbose_name=_('max candidatures/jour'))
    application_deadline_days = models.PositiveIntegerField(default=30, verbose_name=_('délai candidature (jours)'))
    auto_reject_after_days = models.PositiveIntegerField(default=90, help_text=_('Rejet automatique après X jours'), 
                                                       verbose_name=_('rejet auto (jours)'))
    enable_auto_matching = models.BooleanField(default=True, verbose_name=_('matching automatique'))
    matching_threshold = models.PositiveIntegerField(default=70, help_text=_('Seuil de matching en %'), 
                                                   verbose_name=_('seuil matching'))
    
    # Paramètres d'email
    email_notifications_enabled = models.BooleanField(default=True, verbose_name=_('notifications email'))
    admin_notification_email = models.EmailField(blank=True, verbose_name=_('email admin'))
    email_signature = models.TextField(default='L\'équipe Recruitment Expert\ncontact@recruitment-expert.com\n+33 1 23 45 67 89', 
                                     verbose_name=_('signature email'))
    
    # Maintenance
    maintenance_mode = models.BooleanField(default=False, verbose_name=_('mode maintenance'))
    maintenance_message = models.TextField(blank=True, verbose_name=_('message maintenance'))
    
    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True, verbose_name=_('ID Google Analytics'))
    enable_tracking = models.BooleanField(default=False, verbose_name=_('suivi analytics'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('créé le'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('modifié le'))

    class Meta:
        verbose_name = _('Paramètres du site')
        verbose_name_plural = _('Paramètres du site')

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule instance
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError(_('Il ne peut y avoir qu\'une seule instance de SiteSettings'))
        super().save(*args, **kwargs)


class Newsletter(models.Model):
    """Abonnements à la newsletter"""
    email = models.EmailField(unique=True, verbose_name=_('email'))
    is_active = models.BooleanField(default=True, verbose_name=_('actif'))
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name=_('inscrit le'))
    unsubscribed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('désinscrit le'))

    class Meta:
        verbose_name = _('Abonnement Newsletter')
        verbose_name_plural = _('Abonnements Newsletter')
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


class BlogPost(models.Model):
    """Articles de blog"""
    STATUS_CHOICES = (
        ('draft', _('Brouillon')),
        ('published', _('Publié')),
        ('archived', _('Archivé')),
    )

    title = models.CharField(max_length=200, verbose_name=_('titre'))
    slug = models.SlugField(max_length=250, unique=True, verbose_name=_('slug'))
    content = models.TextField(verbose_name=_('contenu'))
    excerpt = models.TextField(max_length=500, blank=True, verbose_name=_('extrait'))
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True, verbose_name=_('image principale'))
    
    # Métadonnées
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_('statut'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', verbose_name=_('auteur'))
    tags = models.CharField(max_length=200, blank=True, help_text=_('Tags séparés par des virgules'), 
                          verbose_name=_('tags'))
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True, verbose_name=_('meta description'))
    meta_keywords = models.CharField(max_length=200, blank=True, verbose_name=_('meta keywords'))
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('créé le'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('modifié le'))
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_('publié le'))
    
    # Statistiques
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('nombre de vues'))

    class Meta:
        verbose_name = _('Article de blog')
        verbose_name_plural = _('Articles de blog')
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
        ('about', _('À propos')),
        ('privacy', _('Politique de confidentialité')),
        ('terms', _('Conditions d\'utilisation')),
        ('faq', _('FAQ')),
        ('contact', _('Contact')),
        ('home', _('Accueil')),
        ('hero_section', _('Section héro')),
        ('footer_content', _('Contenu du footer')),
        ('career_tips', _('Conseils de carrière')),
        ('promotional', _('Contenu promotionnel')),
        ('custom', _('Page personnalisée')),
    )

    page_type = models.CharField(max_length=20, choices=PAGE_TYPES, verbose_name=_('type de page'))
    title = models.CharField(max_length=200, verbose_name=_('titre'))
    content = models.TextField(verbose_name=_('contenu'))
    meta_description = models.CharField(max_length=160, blank=True, verbose_name=_('meta description'))
    meta_keywords = models.CharField(max_length=200, blank=True, verbose_name=_('meta keywords'))
    is_active = models.BooleanField(default=True, verbose_name=_('actif'))
    show_in_menu = models.BooleanField(default=True, verbose_name=_('afficher dans le menu'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('ordre'))
    
    # SEO
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name=_('slug'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('créé le'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('modifié le'))
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('modifié par'))

    class Meta:
        verbose_name = _('Contenu de page')
        verbose_name_plural = _('Contenus de pages')
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
    name = models.CharField(max_length=100, unique=True, verbose_name=_('nom'))
    is_active = models.BooleanField(default=False, verbose_name=_('actif'))
    
    # Couleurs principales
    primary_color = models.CharField(max_length=7, default='#007bff', verbose_name=_('couleur primaire'))
    secondary_color = models.CharField(max_length=7, default='#6c757d', verbose_name=_('couleur secondaire'))
    success_color = models.CharField(max_length=7, default='#28a745', verbose_name=_('couleur succès'))
    info_color = models.CharField(max_length=7, default='#17a2b8', verbose_name=_('couleur info'))
    warning_color = models.CharField(max_length=7, default='#ffc107', verbose_name=_('couleur avertissement'))
    danger_color = models.CharField(max_length=7, default='#dc3545', verbose_name=_('couleur danger'))
    light_color = models.CharField(max_length=7, default='#f8f9fa', verbose_name=_('couleur claire'))
    dark_color = models.CharField(max_length=7, default='#343a40', verbose_name=_('couleur sombre'))
    
    # Typographie
    font_family = models.CharField(max_length=100, default='Segoe UI, system-ui, sans-serif', verbose_name=_('police'))
    font_size_base = models.PositiveIntegerField(default=16, help_text=_('Taille de police de base en px'), 
                                               verbose_name=_('taille police base'))
    
    # Layout
    border_radius = models.PositiveIntegerField(default=6, help_text=_('Rayon des bordures en px'), 
                                              verbose_name=_('rayon bordures'))
    container_max_width = models.PositiveIntegerField(default=1200, help_text=_('Largeur max du container en px'), 
                                                    verbose_name=_('largeur max container'))
    
    # CSS personnalisé
    custom_css = models.TextField(blank=True, help_text=_('CSS personnalisé'), verbose_name=_('CSS personnalisé'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('créé le'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('modifié le'))

    class Meta:
        verbose_name = _('Thème')
        verbose_name_plural = _('Thèmes')

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
        ('management', _('Direction')),
        ('technical', _('Technique')),
        ('hr', _('Ressources Humaines')),
        ('marketing', _('Marketing')),
        ('sales', _('Commercial')),
        ('support', _('Support')),
        ('other', _('Autre')),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='team_member', verbose_name=_('utilisateur'))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name=_('rôle'))
    bio = models.TextField(blank=True, verbose_name=_('biographie'))
    photo = models.ImageField(upload_to='team/', blank=True, null=True, verbose_name=_('photo'))
    linkedin_url = models.URLField(blank=True, verbose_name=_('LinkedIn'))
    twitter_url = models.URLField(blank=True, verbose_name=_('Twitter'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('ordre'))
    is_active = models.BooleanField(default=True, verbose_name=_('actif'))
    show_in_team = models.BooleanField(default=True, verbose_name=_('afficher dans l\'équipe'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('créé le'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('modifié le'))

    class Meta:
        verbose_name = _('Membre d\'équipe')
        verbose_name_plural = _('Membres d\'équipe')
        ordering = ['order', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"


class Value(models.Model):
    """Valeurs de l'entreprise"""
    title = models.CharField(max_length=100, verbose_name=_('titre'))
    description = models.TextField(verbose_name=_('description'))
    icon = models.CharField(max_length=50, help_text=_('Classe FontAwesome (ex: fas fa-heart)'), 
                          verbose_name=_('icône'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('ordre'))
    is_active = models.BooleanField(default=True, verbose_name=_('actif'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('créé le'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('modifié le'))

    class Meta:
        verbose_name = _('Valeur')
        verbose_name_plural = _('Valeurs')
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class Statistic(models.Model):
    """Statistiques pour la page about"""
    title = models.CharField(max_length=100, verbose_name=_('titre'))
    value = models.PositiveIntegerField(default=0, verbose_name=_('valeur'))
    icon = models.CharField(max_length=50, help_text=_('Classe FontAwesome (ex: fas fa-users)'), 
                          verbose_name=_('icône'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('ordre'))
    is_active = models.BooleanField(default=True, verbose_name=_('actif'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('créé le'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('modifié le'))

    class Meta:
        verbose_name = _('Statistique')
        verbose_name_plural = _('Statistiques')
        ordering = ['order', 'title']

    def __str__(self):
        return f"{self.title}: {self.value}"