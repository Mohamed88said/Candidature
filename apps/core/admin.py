from django.contrib import admin
from .models import ContactMessage, FAQ, SiteSettings, Newsletter, BlogPost, PageContent, ThemeSettings


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'created_at', 'assigned_to')
    list_filter = ('subject', 'status', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Message', {
            'fields': ('name', 'email', 'phone', 'subject', 'message')
        }),
        ('Gestion', {
            'fields': ('status', 'assigned_to', 'response', 'responded_at')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('question', 'answer')
    list_editable = ('order', 'is_active')
    ordering = ['category', 'order']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Informations générales', {
            'fields': ('site_name', 'site_description', 'contact_email', 'contact_phone', 'address')
        }),
        ('Réseaux sociaux', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url')
        }),
        ('Paramètres de candidature', {
            'fields': ('max_applications_per_day', 'application_deadline_days')
        }),
        ('Paramètres d\'email', {
            'fields': ('email_notifications_enabled', 'admin_notification_email')
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
    )
    
    def has_add_permission(self, request):
        # Empêcher la création de multiples instances
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression
        return False


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'subscribed_at', 'unsubscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at', 'unsubscribed_at')
    date_hierarchy = 'subscribed_at'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'published_at', 'views_count')
    list_filter = ('status', 'author', 'created_at', 'published_at')
    search_fields = ('title', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'views_count')
    date_hierarchy = 'published_at'
    
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image')
        }),
        ('Métadonnées', {
            'fields': ('status', 'author', 'tags', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est un nouvel article
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ('page_type', 'title', 'is_active', 'show_in_menu', 'order', 'updated_at')
    list_filter = ('page_type', 'is_active', 'show_in_menu')
    search_fields = ('title', 'content')
    list_editable = ('is_active', 'show_in_menu', 'order')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Page', {
            'fields': ('page_type', 'title', 'slug', 'content')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords')
        }),
        ('Affichage', {
            'fields': ('is_active', 'show_in_menu', 'order')
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Utiliser un widget de texte riche pour le contenu
        form.base_fields['content'].widget = forms.Textarea(attrs={'rows': 20, 'cols': 80})
        return form
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ThemeSettings)
class ThemeSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'primary_color', 'updated_at')
    list_filter = ('is_active',)
    
    fieldsets = (
        ('Thème', {
            'fields': ('name', 'is_active')
        }),
        ('Couleurs principales', {
            'fields': ('primary_color', 'secondary_color', 'success_color', 'info_color')
        }),
        ('Couleurs d\'état', {
            'fields': ('warning_color', 'danger_color', 'light_color', 'dark_color')
        }),
        ('Typographie', {
            'fields': ('font_family', 'font_size_base')
        }),
        ('Layout', {
            'fields': ('border_radius', 'container_max_width')
        }),
        ('CSS personnalisé', {
            'fields': ('custom_css',),
            'classes': ('collapse',)
        }),
    )