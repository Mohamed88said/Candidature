from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import ContactMessage, FAQ, SiteSettings, Newsletter, BlogPost, PageContent, TeamMember, Value, Statistic
from .forms import ContactForm, NewsletterForm, SearchForm
from apps.jobs.models import Job, JobCategory
from apps.accounts.models import CandidateProfile
# Ajout des imports pour les emails
from django.core.mail import send_mail
from django.conf import settings
from apps.core.tasks import send_contact_confirmation_email


def home(request):
    """Page d'accueil"""
    # Offres en vedette
    featured_jobs = Job.objects.filter(
        status='published', 
        featured=True
    ).select_related('category')[:6]
    
    # Offres rÃ©centes
    recent_jobs = Job.objects.filter(
        status='published'
    ).select_related('category').order_by('-created_at')[:8]
    
    # Statistiques
    stats = {
        'total_jobs': Job.objects.filter(status='published').count(),
        'total_companies': Job.objects.filter(status='published').values('company').distinct().count(),
        'total_candidates': CandidateProfile.objects.filter(is_active=True).count(),
        'total_categories': JobCategory.objects.filter(is_active=True).count(),
    }
    
    # CatÃ©gories populaires
    popular_categories = JobCategory.objects.filter(
        is_active=True
    ).annotate(
        job_count=Count('jobs', filter=Q(jobs__status='published'))
    ).order_by('-job_count')[:6]
    
    # Formulaire de newsletter
    newsletter_form = NewsletterForm()
    
    context = {
        'featured_jobs': featured_jobs,
        'recent_jobs': recent_jobs,
        'stats': stats,
        'popular_categories': popular_categories,
        'newsletter_form': newsletter_form,
    }
    
    return render(request, 'core/home.html', context)


def about(request):
    """Page Ã  propos"""
    try:
        about_content = PageContent.objects.get(page_type='about', is_active=True)
    except PageContent.DoesNotExist:
        about_content = None
    
    try:
        site_settings = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        site_settings = None
    
    # RÃ©cupÃ©rer les donnÃ©es dynamiques
    team_members = TeamMember.objects.filter(
        is_active=True, 
        show_in_team=True
    ).select_related('user').order_by('order')
    
    values = Value.objects.filter(is_active=True).order_by('order')
    
    statistics = Statistic.objects.filter(is_active=True).order_by('order')
    
    # Si pas de statistiques configurÃ©es, utiliser les valGNFs par dÃ©faut
    if not statistics.exists():
        stats = {
            'jobs_posted': Job.objects.count(),
            'candidates_registered': CandidateProfile.objects.count(),
            'successful_placements': Job.objects.filter(status='filled').count(),
            'companies_served': Job.objects.values('company').distinct().count(),
        }
    else:
        stats = {stat.title.lower().replace(' ', '_'): stat.value for stat in statistics}
    
    context = {
        'about_content': about_content,
        'site_settings': site_settings,
        'team_members': team_members,
        'values': values,
        'stats': stats,
    }
    
    return render(request, 'core/about.html', context)


def contact_view(request):
    """Page de contact avec gestion d'erreur Redis"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Sauvegarder le message de contact
            contact_message = form.save()
            
            # Gestion robuste de l'envoi d'email
            try:
                # Essayer d'envoyer en asynchrone (avec Celery)
                from apps.core.tasks import send_contact_confirmation_email
                
                # Vérifier si Redis est disponible
                if settings.DEBUG or 'localhost' in settings.CELERY_BROKER_URL:
                    # Mode développement - exécution synchrone
                    send_contact_confirmation_email(
                        form.cleaned_data['email'],
                        form.cleaned_data['name'],
                        form.cleaned_data['subject']
                    )
                    messages.success(request, 'Votre message a été envoyé avec succès!')
                else:
                    # Mode production - exécution asynchrone
                    send_contact_confirmation_email.delay(
                        form.cleaned_data['email'],
                        form.cleaned_data['name'],
                        form.cleaned_data['subject']
                    )
                    messages.success(request, 'Votre message a été envoyé avec succès! Vous recevrez une confirmation par email.')
                
            except Exception as e:
                # Fallback: envoyer l'email de façon synchrone
                from django.core.mail import send_mail
                from django.template.loader import render_to_string
                from django.utils.html import strip_tags
                
                # Email de confirmation au visiteur
                html_message = render_to_string('emails/contact_confirmation.html', {
                    'user_name': form.cleaned_data['name'],
                    'message_subject': form.cleaned_data['subject'],
                    'support_email': settings.SUPPORT_EMAIL
                })
                plain_message = strip_tags(html_message)
                
                send_mail(
                    "Confirmation de réception de votre message",
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [form.cleaned_data['email']],
                    html_message=html_message,
                    fail_silently=True,
                )
                
                # Email à l'équipe
                team_subject = f"Nouveau message de contact: {form.cleaned_data['subject']}"
                team_message = f"""
                Nom: {form.cleaned_data['name']}
                Email: {form.cleaned_data['email']}
                Sujet: {form.cleaned_data['subject']}
                Message:
                {form.cleaned_data['message']}
                """
                
                send_mail(
                    team_subject,
                    team_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.SUPPORT_EMAIL],
                    fail_silently=True,
                )
                
                messages.success(request, 'Votre message a été envoyé avec succès! (Mode secours)')
            
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {'form': form})


def faq(request):
    """Page FAQ"""
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order')
    
    # Grouper par catÃ©gorie
    faq_by_category = {}
    for faq in faqs:
        category = faq.get_category_display()
        if category not in faq_by_category:
            faq_by_category[category] = []
        faq_by_category[category].append(faq)
    
    return render(request, 'core/faq.html', {'faq_by_category': faq_by_category})


def terms(request):
    """Conditions d'utilisation"""
    try:
        terms_content = PageContent.objects.get(page_type='terms', is_active=True)
    except PageContent.DoesNotExist:
        terms_content = None
    
    context = {
        'terms_content': terms_content,
        'last_updated': '1er janvier 2024'
    }
    
    return render(request, 'core/terms.html', context)


def privacy(request):
    """Politique de confidentialitÃ©"""
    try:
        privacy_content = PageContent.objects.get(page_type='privacy', is_active=True)
    except PageContent.DoesNotExist:
        privacy_content = None
    
    context = {
        'privacy_content': privacy_content,
        'last_updated': '1er janvier 2024'
    }
    
    return render(request, 'core/privacy.html', context)


@require_http_methods(["POST"])
def newsletter_subscribe(request):
    """Abonnement Ã  la newsletter (AJAX)"""
    form = NewsletterForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        newsletter, created = Newsletter.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        
        if created:
            message = "Merci pour votre abonnement à notre newsletter!"
            success = True
        else:
            if newsletter.is_active:
                message = "Vous êtes déjà abonné à notre newsletter."
                success = False
            else:
                newsletter.is_active = True
                newsletter.unsubscribed_at = None
                newsletter.save()
                message = "Votre abonnement a été réactivé!"
                success = True
        
        return JsonResponse({
            'success': success,
            'message': message
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Adresse email invalide.'
        })


def newsletter_unsubscribe(request, email):
    """DÃ©sabonnement de la newsletter"""
    try:
        newsletter = Newsletter.objects.get(email=email, is_active=True)
        newsletter.is_active = False
        newsletter.unsubscribed_at = timezone.now()
        newsletter.save()
        messages.success(request, 'Vous avez été désabonné de notre newsletter.')
    except Newsletter.DoesNotExist:
        messages.error(request, 'Adresse email non trouvée.')
    
    return redirect('core:home')


def search(request):
    """Recherche globale"""
    form = SearchForm(request.GET)
    results = {
        'jobs': [],
        'companies': [],
        'total': 0
    }
    
    if form.is_valid():
        query = form.cleaned_data['query']
        
        # Recherche dans les offres d'emploi
        jobs = Job.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(company__icontains=query) |
            Q(location__icontains=query),
            status='published'
        ).select_related('category')[:20]
        
        # Recherche des entreprises
        companies = Job.objects.filter(
            company__icontains=query,
            status='published'
        ).values('company').distinct()[:10]
        
        results = {
            'jobs': jobs,
            'companies': companies,
            'total': jobs.count() + companies.count(),
            'query': query
        }
    
    context = {
        'form': form,
        'results': results,
    }
    
    return render(request, 'core/search.html', context)


def blog(request):
    """Liste des articles de blog"""
    posts = BlogPost.objects.filter(status='published').order_by('-published_at')
    
    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Articles récents pour la sidebar
    recent_posts = BlogPost.objects.filter(status='published').order_by('-published_at')[:5]
    
    # Tags populaires
    all_posts = BlogPost.objects.filter(status='published')
    all_tags = []
    for post in all_posts:
        if post.tags:
            all_tags.extend([tag.strip() for tag in post.tags.split(',')])
    
    from collections import Counter
    popular_tags = Counter(all_tags).most_common(10)
    
    context = {
        'page_obj': page_obj,
        'recent_posts': recent_posts,
        'popular_tags': popular_tags,
    }
    
    return render(request, 'core/blog.html', context)


def blog_detail(request, slug):
    """DÃ©tail d'un article de blog"""
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # IncrÃ©menter le nombre de vues
    post.views_count += 1
    post.save(update_fields=['views_count'])
    
    # Articles similaires
    similar_posts = BlogPost.objects.filter(
        status='published'
    ).exclude(id=post.id).order_by('-published_at')[:3]
    
    # Articles rÃ©cents pour la sidebar
    recent_posts = BlogPost.objects.filter(status='published').order_by('-published_at')[:5]
    
    context = {
        'post': post,
        'similar_posts': similar_posts,
        'recent_posts': recent_posts,
    }
    
    return render(request, 'core/blog_detail.html', context)


def blog_by_tag(request, tag):
    """Articles par tag"""
    posts = BlogPost.objects.filter(
        status='published',
        tags__icontains=tag
    ).order_by('-published_at')
    
    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # RAFRAÃŽCHIR LES VUES DEPUIS LA BASE DE DONNÃ‰ES
    for post in page_obj:
        post.refresh_from_db()
    
    context = {
        'page_obj': page_obj,
        'tag': tag,
    }
    
    return render(request, 'core/blog_by_tag.html', context)


def sitemap(request):
    """Plan du site"""
    # URLs principales
    main_urls = [
        {'name': 'Accueil', 'url': 'core:home'},
        {'name': 'Offres d\'emploi', 'url': 'jobs:job_list'},
        {'name': 'À propos', 'url': 'core:about'},
        {'name': 'Contact', 'url': 'core:contact'},
        {'name': 'FAQ', 'url': 'core:faq'},
        {'name': 'Blog', 'url': 'core:blog'},
    ]
    
    # CatÃ©gories d'emploi
    categories = JobCategory.objects.filter(is_active=True)
    
    # Articles de blog rÃ©cents
    recent_posts = BlogPost.objects.filter(status='published').order_by('-published_at')[:10]
    
    context = {
        'main_urls': main_urls,
        'categories': categories,
        'recent_posts': recent_posts,
    }
    
    return render(request, 'core/sitemap.html', context)


def handler404(request, exception):
    """Page d'errGNF 404 personnalisÃ©e"""
    return render(request, 'core/404.html', status=404)


def handler500(request):
    """Page d'errGNF 500 personnalisÃ©e"""
    return render(request, 'core/500.html', status=500)


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import ComposeNewsletterForm
from .tasks import send_newsletter_task
from .models import Newsletter

@staff_member_required
def compose_newsletter(request):
    """Vue pour composer une newsletter depuis l'admin"""
    if request.method == 'POST':
        form = ComposeNewsletterForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            template_name = form.cleaned_data['template_name']
            preview = form.cleaned_data['preview']
            
            # RÃ©cupÃ©rer les destinataires depuis la session
            recipient_ids = request.session.get('newsletter_recipients', [])
            if not recipient_ids:
                # Si aucun destinataire spÃ©cifique, utiliser tous les abonnÃ©s actifs
                recipients = Newsletter.objects.filter(is_active=True)
                recipient_ids = list(recipients.values_list('id', flat=True))
            
            if preview:
                # Mode preview : envoyer seulement Ã  l'admin
                from django.conf import settings
                recipient_emails = [settings.DEFAULT_FROM_EMAIL]
                messages.info(request, "Email de test envoyé à l'administrateur.")
            else:
                # Envoi rÃ©el
                recipients = Newsletter.objects.filter(id__in=recipient_ids, is_active=True)
                recipient_emails = list(recipients.values_list('email', flat=True))
                messages.success(request, f"Newsletter envoyée à {len(recipient_emails)} destinataires.")
            
            # PrÃ©parer le contexte avec les offres rÃ©elles
            context_list = []
            for email in recipient_emails:
                context = {
                    'email': email,
                    'subject': subject,
                    'unsubscribe_url': f"{request.scheme}://{request.get_host()}/newsletter/unsubscribe/{email}/",
                    'SITE_URL': f"{request.scheme}://{request.get_host()}",
                    'current_date': timezone.now(),
                }
                context_list.append(context)
            
            # Lancer la tÃ¢che asynchrone
            send_newsletter_task.delay(subject, template_name, context_list, recipient_emails)
            
            # Nettoyer la session
            if 'newsletter_recipients' in request.session:
                del request.session['newsletter_recipients']
            
            return redirect('admin:core_newsletter_changelist')
    else:
        form = ComposeNewsletterForm()
    
    return render(request, 'admin/compose_newsletter.html', {
        'form': form,
        'title': 'Composer une newsletter'
    })

@staff_member_required
def send_newsletter_email(request, pk):
    """Envoyer un email Ã  un seul abonnÃ©"""
    from django.conf import settings
    from .tasks import send_newsletter_task
    
    newsletter = Newsletter.objects.get(pk=pk)
    
    subject = f"Message personnalisé pour {newsletter.email}"
    template_name = "newsletter.html"
    
    context = {
        'email': newsletter.email,
        'subject': subject,
        'unsubscribe_url': f"{request.scheme}://{request.get_host()}/newsletter/unsubscribe/{newsletter.email}/",
        'SITE_URL': f"{request.scheme}://{request.get_host()}",
        'current_date': timezone.now(),
    }
    
    send_newsletter_task.delay(subject, template_name, [context], [newsletter.email])
    
    messages.success(request, f"Email envoyé à {newsletter.email}")
    return redirect('admin:core_newsletter_changelist')

