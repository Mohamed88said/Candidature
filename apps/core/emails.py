from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from apps.jobs.models import Job
from django.utils import timezone
from .models import BlogPost, PageContent  # IMPORT AJOUTÉ

def get_featured_jobs_for_newsletter(limit=3):
    """Récupère les offres vedettes pour la newsletter"""
    return Job.objects.filter(
        status='published',
        featured=True,
        application_deadline__gte=timezone.now()
    ).select_related('category').order_by('-created_at')[:limit]

def get_recent_jobs_for_alert(limit=5):
    """Récupère les offres récentes pour les alertes"""
    return Job.objects.filter(
        status='published',
        application_deadline__gte=timezone.now()
    ).select_related('category').order_by('-created_at')[:limit]

def get_career_tips():
    """Récupère les conseils de carrière dynamiques"""
    try:
        # Essayez de récupérer un contenu de page dédié
        tips_content = PageContent.objects.get(
            page_type='career_tips', 
            is_active=True
        )
        return tips_content.content
    except PageContent.DoesNotExist:
        # Fallback vers des conseils génériques
        return "Personnalisez votre lettre de motivation pour chaque candidature. Les recruteurs apprécient les efforts de personnalisation !"

def get_upcoming_events():
    """Récupère les événements à venir dynamiques"""
    try:
        # Récupérer les événements depuis le blog ou une page dédiée
        events = BlogPost.objects.filter(
            status='published',
            tags__icontains='événement',
            published_at__gte=timezone.now()
        ).order_by('published_at')[:3]
        
        event_list = []
        for event in events:
            event_list.append({
                'date': event.published_at.strftime('%d %B'),
                'title': event.title
            })
        return event_list
    except:
        # Fallback vers des événements génériques
        return [
            {'date': '15 ' + timezone.now().strftime('%B'), 'title': 'Webinar "Comment réussir son entretien technique"'},
            {'date': '22 ' + timezone.now().strftime('%B'), 'title': 'Job Fair Virtuel - Rencontrez 50+ entreprises'}
        ]

def get_promotional_content():
    """Récupère le contenu promotionnel dynamique"""
    try:
        promo_content = PageContent.objects.get(
            page_type='promotional', 
            is_active=True
        )
        return {
            'title': promo_content.title,
            'content': promo_content.content,
            'discount': '20%',  # Récupérer depuis la base si possible
            'code': 'PREMIUM20'  # Récupérer depuis la base si possible
        }
    except PageContent.DoesNotExist:
        # Contenu promotionnel par défaut
        return {
            'title': 'Boostez votre carrière',
            'content': 'Sur nos services premium de coaching et de préparation aux entretiens',
            'discount': '20%',
            'code': 'PREMIUM20'
        }

def send_newsletter(newsletter_id, subject, template_name, context):
    """
    Fonction pour envoyer des newsletters avec des offres réelles
    """
    # Récupérer les données dynamiques selon le template
    if template_name == 'newsletter.html':
        context['featured_jobs'] = get_featured_jobs_for_newsletter()
        context['career_tip'] = get_career_tips()
        context['upcoming_events'] = get_upcoming_events()
        
    elif template_name == 'new_job_alert.html':
        context['recent_jobs'] = get_recent_jobs_for_alert()
        
    elif template_name == 'promotional.html':
        context['promo_content'] = get_promotional_content()
        context['upcoming_events'] = get_upcoming_events()
    
    context['current_date'] = timezone.now()
    
    # Validation du nom de template
    valid_templates = ['newsletter.html', 'new_job_alert.html', 'promotional.html']
    if template_name not in valid_templates:
        template_name = 'newsletter.html'
    
    try:
        html_content = render_to_string(f'emails/{template_name}', context)
        text_content = strip_tags(html_content)
        
        recipient_email = context.get('email', settings.DEFAULT_FROM_EMAIL)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
            reply_to=[settings.DEFAULT_FROM_EMAIL]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        print(f"✅ Email ENVOYÉ à: {recipient_email}")
        return 1, 1
        
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email: {e}")
        return 0, 1

def send_bulk_newsletter(subject, template_name, context_list, recipient_list):
    """
    Fonction pour envoyer des newsletters en masse avec offres réelles
    """
    success_count = 0
    total_count = len(recipient_list)
    
    # Récupérer les données une seule fois pour tous les destinataires
    if template_name == 'newsletter.html':
        featured_jobs = get_featured_jobs_for_newsletter()
        career_tip = get_career_tips()
        upcoming_events = get_upcoming_events()
        
    elif template_name == 'new_job_alert.html':
        recent_jobs = get_recent_jobs_for_alert()
        
    elif template_name == 'promotional.html':
        promo_content = get_promotional_content()
        upcoming_events = get_upcoming_events()
    
    for i, email in enumerate(recipient_list):
        try:
            # Préparer le contexte pour chaque destinataire
            context = context_list[i] if i < len(context_list) else {}
            context['email'] = email
            context['current_date'] = timezone.now()
            
            # Ajouter les données dynamiques au contexte
            if template_name == 'newsletter.html':
                context['featured_jobs'] = featured_jobs
                context['career_tip'] = career_tip
                context['upcoming_events'] = upcoming_events
                
            elif template_name == 'new_job_alert.html':
                context['recent_jobs'] = recent_jobs
                
            elif template_name == 'promotional.html':
                context['promo_content'] = promo_content
                context['upcoming_events'] = upcoming_events
            
            # Utiliser la fonction principale
            success, _ = send_newsletter(None, subject, template_name, context)
            success_count += success
            
        except Exception as e:
            print(f"❌ Erreur pour {email}: {e}")
    
    return success_count, total_count
