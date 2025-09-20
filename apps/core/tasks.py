from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .utils.email_utils import send_template_email
from .emails import send_bulk_newsletter  # IMPORT AJOUTÉ

@shared_task
def send_email_task(subject, template_name, context, to_emails):
    """
    Tâche asynchrone pour l'envoi d'emails
    """
    return send_template_email(subject, template_name, context, to_emails)

@shared_task
def send_welcome_email(user_email, user_name):
    """
    Email de bienvenue pour les nouveaux utilisateurs
    """
    subject = "Bienvenue sur notre Plateforme de Recrutement"
    template_name = "welcome_email.html"
    context = {
        'user_name': user_name,
        'platform_name': 'Plateforme de Recrutement'
    }
    return send_template_email(subject, template_name, context, user_email)

@shared_task
def send_application_received_email(application_id):
    """
    Email de confirmation de réception de candidature
    """
    from apps.applications.models import Application
    try:
        application = Application.objects.get(id=application_id)
        subject = f"Confirmation de votre candidature - {application.job.title}"
        template_name = "application_received.html"
        context = {
            'candidate_name': application.candidate.user.full_name,
            'job_title': application.job.title,
            'company_name': application.job.company,
            'application_date': application.applied_at,
            'application_id': application.id
        }
        return send_template_email(subject, template_name, context, application.candidate.user.email)
    except Application.DoesNotExist:
        return False

@shared_task
def send_contact_confirmation_email(user_email, user_name, message_subject):
    """
    Email de confirmation de contact
    """
    subject = "Confirmation de réception de votre message"
    template_name = "contact_confirmation.html"
    context = {
        'user_name': user_name,
        'message_subject': message_subject,
        'support_email': settings.DEFAULT_FROM_EMAIL
    }
    return send_template_email(subject, template_name, context, user_email)

@shared_task
def send_newsletter_task(subject, template_name, context_list, recipient_list):
    """
    Tâche pour l'envoi de newsletter avec offres réelles
    """
    return send_bulk_newsletter(subject, template_name, context_list, recipient_list)

@shared_task
def send_password_reset_email(user_email, reset_url, user_name):
    """
    Email de réinitialisation de mot de passe
    """
    subject = "Réinitialisation de votre mot de passe"
    template_name = "password_reset.html"
    context = {
        'user_name': user_name,
        'reset_url': reset_url,
        'support_email': settings.DEFAULT_FROM_EMAIL
    }
    return send_template_email(subject, template_name, context, user_email)

@shared_task
def send_interview_invitation_email(interview_id):
    """
    Email d'invitation à un entretien
    """
    from apps.applications.models import Interview
    try:
        interview = Interview.objects.get(id=interview_id)
        subject = f"Invitation à un entretien - {interview.application.job.title}"
        template_name = "interview_invitation.html"
        context = {
            'candidate_name': interview.application.candidate.user.full_name,
            'job_title': interview.application.job.title,
            'company_name': interview.application.job.company,
            'interview_date': interview.scheduled_date,
            'interview_type': interview.get_interview_type_display(),
            'duration': interview.duration_minutes,
            'location': interview.location or "Lien de visioconférence à venir",
            'preparation_notes': interview.notes or "Aucune note particulière"
        }
        return send_template_email(subject, template_name, context, interview.application.candidate.user.email)
    except Interview.DoesNotExist:
        return False