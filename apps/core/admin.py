from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html
from .models import (
    ContactMessage, FAQ, SiteSettings, Newsletter, 
    BlogPost, PageContent, ThemeSettings, TeamMember, Value, Statistic
)
from .forms import NewsletterAdminForm, ComposeNewsletterForm
from .emails import send_newsletter, send_bulk_newsletter  # IMPORT MODIFIÉ ICI
from django.urls import reverse
from django import forms

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
    list_display = ('site_name', 'contact_email', 'contact_phone')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('site_name', 'site_description', 'contact_email', 'contact_phone', 'address')
        }),
        ('Réseaux sociaux', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url', 'youtube_url')
        }),
        ('Paramètres de candidature', {
            'fields': ('max_applications_per_day', 'application_deadline_days', 'auto_reject_after_days')
        }),
        ('Paramètres d\'email', {
            'fields': ('email_notifications_enabled', 'admin_notification_email', 'email_signature')
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
        ('Analytics', {
            'fields': ('google_analytics_id', 'enable_tracking'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'subscribed_at', 'unsubscribed_at', 'send_email_action')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at', 'unsubscribed_at')
    date_hierarchy = 'subscribed_at'
    actions = ['export_emails', 'send_test_newsletter', 'send_selected_newsletter']
    form = NewsletterAdminForm

    def send_email_action(self, obj):
        return format_html(
            '<a class="button" href="{}">Envoyer un email</a>',
            reverse('admin:core_newsletter_send_email', args=[obj.pk])
        )
    send_email_action.short_description = 'Action'
    send_email_action.allow_tags = True

    def send_selected_newsletter(self, request, queryset):
        """Action pour envoyer une newsletter aux abonnés sélectionnés"""
        request.session['newsletter_recipients'] = list(queryset.values_list('id', flat=True))
        return HttpResponseRedirect(reverse('admin:core_newsletter_compose_newsletter'))
    send_selected_newsletter.short_description = "Envoyer une newsletter aux abonnés sélectionnés"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('compose-newsletter/', self.admin_site.admin_view(self.compose_newsletter_view), name='core_newsletter_compose_newsletter'),
            path('<path:object_id>/send-email/', self.admin_site.admin_view(self.send_newsletter_email_view), name='core_newsletter_send_email'),
        ]
        return custom_urls + urls

    def compose_newsletter_view(self, request):
        """Vue pour composer une newsletter"""
        if request.method == 'POST':
            form = ComposeNewsletterForm(request.POST)
            if form.is_valid():
                subject = form.cleaned_data['subject']
                template_name = form.cleaned_data['template_name']
                preview = form.cleaned_data['preview']
                
                # Récupérer les destinataires depuis la session
                recipient_ids = request.session.get('newsletter_recipients', [])
                if not recipient_ids:
                    recipients = Newsletter.objects.filter(is_active=True)
                    recipient_ids = list(recipients.values_list('id', flat=True))
                
                if preview:
                    # Mode preview : envoyer seulement à l'admin
                    from django.conf import settings
                    recipient_emails = [settings.DEFAULT_FROM_EMAIL]
                    messages.info(request, "Email de test envoyé à l'administrateur.")
                else:
                    # Envoi réel
                    recipients = Newsletter.objects.filter(id__in=recipient_ids, is_active=True)
                    recipient_emails = list(recipients.values_list('email', flat=True))
                    messages.success(request, f"Newsletter envoyée à {len(recipient_emails)} destinataires.")
                
                # Préparer le contexte
                context_list = []
                for email in recipient_emails:
                    context = {
                        'email': email,
                        'subject': subject,
                        'unsubscribe_url': f"{request.scheme}://{request.get_host()}/newsletter/unsubscribe/{email}/",
                        'SITE_URL': f"{request.scheme}://{request.get_host()}",
                    }
                    context_list.append(context)
                
                # MODIFICATION IMPORTANTE ICI - Utilisation de send_bulk_newsletter
                success_count, total_count = send_bulk_newsletter(
                    subject,
                    template_name,
                    context_list,
                    recipient_emails
                )
                
                # Nettoyer la session
                if 'newsletter_recipients' in request.session:
                    del request.session['newsletter_recipients']
                
                return HttpResponseRedirect(reverse('admin:core_newsletter_changelist'))
        else:
            form = ComposeNewsletterForm()
        
        return render(request, 'admin/compose_newsletter.html', {
            'form': form,
            'title': 'Composer une newsletter'
        })

    def send_newsletter_email_view(self, request, object_id):
        """Envoyer un email à un seul abonné"""
        newsletter = Newsletter.objects.get(pk=object_id)
        
        subject = f"Message personnalisé pour {newsletter.email}"
        template_name = "newsletter.html"
        
        # Envoyer la newsletter
        success_count, total_count = send_newsletter(
            None,
            subject,
            template_name,
            {
                'email': newsletter.email,
                'subject': subject,
                'unsubscribe_url': f"{request.scheme}://{request.get_host()}/newsletter/unsubscribe/{newsletter.email}/",
                'SITE_URL': f"{request.scheme}://{request.get_host()}",
            }
        )
        
        messages.success(request, f"Email envoyé à {newsletter.email}")
        return HttpResponseRedirect(reverse('admin:core_newsletter_changelist'))
    
    def export_emails(self, request, queryset):
        """Exporter les emails des abonnés"""
        emails = queryset.values_list('email', flat=True)
        response = HttpResponse('\n'.join(emails), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="abonnes_newsletter.txt"'
        return response
    export_emails.short_description = "Exporter les emails sélectionnés"
    
    def send_test_newsletter(self, request, queryset):
        """Envoyer un test aux abonnés sélectionnés"""
        for newsletter in queryset:
            # Implémentez l'envoi de test ici
            subject = "Test Newsletter"
            template_name = "newsletter.html"
            send_newsletter(
                None,
                subject,
                template_name,
                {
                    'email': newsletter.email,
                    'subject': subject,
                    'unsubscribe_url': f"http://{request.get_host()}/newsletter/unsubscribe/{newsletter.email}/",
                    'SITE_URL': f"http://{request.get_host()}",
                }
            )
        self.message_user(request, f"Test envoyé à {queryset.count()} abonnés")
    send_test_newsletter.short_description = "Envoyer un email test"


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
        if not change:
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


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'order', 'is_active', 'show_in_team')
    list_filter = ('role', 'is_active', 'show_in_team')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    list_editable = ('order', 'is_active', 'show_in_team')
    ordering = ['order', 'user__first_name']
    
    fieldsets = (
        ('Membre', {
            'fields': ('user', 'role', 'bio', 'photo')
        }),
        ('Réseaux sociaux', {
            'fields': ('linkedin_url', 'twitter_url'),
            'classes': ('collapse',)
        }),
        ('Affichage', {
            'fields': ('order', 'is_active', 'show_in_team')
        }),
    )


@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    list_editable = ('order', 'is_active', 'icon')
    ordering = ['order', 'title']
    
    fieldsets = (
        ('Valeur', {
            'fields': ('title', 'description', 'icon')
        }),
        ('Affichage', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('title', 'value', 'icon', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)
    list_editable = ('value', 'order', 'is_active', 'icon')
    ordering = ['order', 'title']
    
    fieldsets = (
        ('Statistique', {
            'fields': ('title', 'value', 'icon')
        }),
        ('Affichage', {
            'fields': ('order', 'is_active')
        }),
    )