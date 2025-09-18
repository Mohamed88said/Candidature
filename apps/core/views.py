from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import ContactMessage, FAQ, SiteSettings, Newsletter, BlogPost
from .forms import ContactForm, NewsletterForm, SearchForm
from apps.jobs.models import Job, JobCategory
from apps.accounts.models import CandidateProfile


def home(request):
    """Page d'accueil"""
    # Offres en vedette
    featured_jobs = Job.objects.filter(
        status='published', 
        featured=True
    ).select_related('category')[:6]
    
    # Offres récentes
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
    
    # Catégories populaires
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
    """Page à propos"""
    try:
        page_content = PageContent.objects.get(page_type='about', is_active=True)
    except SiteSettings.DoesNotExist:
        page_content = None
    
    try:
        site_settings = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        site_settings = None
    
    # Statistiques pour la page à propos
    stats = {
        'jobs_posted': Job.objects.count(),
        'candidates_registered': CandidateProfile.objects.count(),
        'successful_placements': Job.objects.filter(status='filled').count(),
        'companies_served': Job.objects.values('company').distinct().count(),
    }
    
    context = {
        'page_content': page_content,
        'site_settings': site_settings,
        'stats': stats,
    }
    
    return render(request, 'core/about.html', context)


def contact(request):
    """Page de contact"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            messages.success(request, 'Votre message a été envoyé avec succès! Nous vous répondrons dans les plus brefs délais.')
            return redirect('core:contact')
    else:
        form = ContactForm()
    
    try:
        site_settings = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        site_settings = None
    
    context = {
        'form': form,
        'site_settings': site_settings,
    }
    
    return render(request, 'core/contact.html', context)


def faq(request):
    """Page FAQ"""
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order')
    
    # Grouper par catégorie
    faq_by_category = {}
    for faq in faqs:
        category = faq.get_category_display()
        if category not in faq_by_category:
            faq_by_category[category] = []
        faq_by_category[category].append(faq)
    
    return render(request, 'core/faq.html', {'faq_by_category': faq_by_category})


def terms(request):
    """Conditions d'utilisation"""
    return render(request, 'core/terms.html')


def privacy(request):
    """Politique de confidentialité"""
    return render(request, 'core/privacy.html')


@require_http_methods(["POST"])
def newsletter_subscribe(request):
    """Abonnement à la newsletter (AJAX)"""
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
    """Désabonnement de la newsletter"""
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
    """Détail d'un article de blog"""
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Incrémenter le nombre de vues
    post.views_count += 1
    post.save(update_fields=['views_count'])
    
    # Articles similaires
    similar_posts = BlogPost.objects.filter(
        status='published'
    ).exclude(id=post.id).order_by('-published_at')[:3]
    
    # Articles récents pour la sidebar
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
    
    # Catégories d'emploi
    categories = JobCategory.objects.filter(is_active=True)
    
    # Articles de blog récents
    recent_posts = BlogPost.objects.filter(status='published').order_by('-published_at')[:10]
    
    context = {
        'main_urls': main_urls,
        'categories': categories,
        'recent_posts': recent_posts,
    }
    
    return render(request, 'core/sitemap.html', context)


def handler404(request, exception):
    """Page d'erreur 404 personnalisée"""
    return render(request, 'core/404.html', status=404)


def handler500(request):
    """Page d'erreur 500 personnalisée"""
    return render(request, 'core/500.html', status=500)