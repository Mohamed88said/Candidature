from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

def send_template_email(subject, template_name, context, to_emails, from_email=None):
    """
    Envoie un email basé sur un template HTML
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    # Rendre le template HTML
    html_content = render_to_string(f'emails/{template_name}', context)
    text_content = strip_tags(html_content)  # Version texte pour les clients email simples
    
    # Créer l'email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=to_emails if isinstance(to_emails, list) else [to_emails]
    )
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi d'email: {e}")
        return False

def send_bulk_emails(subject, template_name, context_list, recipients_list):
    """
    Envoie des emails en masse avec des contextes personnalisés
    """
    emails = []
    for context, recipient in zip(context_list, recipients_list):
        html_content = render_to_string(f'emails/{template_name}', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient]
        )
        email.attach_alternative(html_content, "text/html")
        emails.append(email)
    
    try:
        # Utiliser send_mass_mail pour les envois groupés
        from django.core.mail import send_mass_mail
        messages = [
            (email.subject, email.body, email.from_email, email.to)
            for email in emails
        ]
        send_mass_mail(messages, fail_silently=False)
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi groupé d'emails: {e}")
        return False

def send_email_with_attachment(subject, message, to_emails, attachment_path=None, attachment_name=None):
    """
    Envoie un email avec pièce jointe
    """
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to_emails if isinstance(to_emails, list) else [to_emails]
    )
    
    if attachment_path:
        email.attach_file(attachment_path)
    
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi d'email avec pièce jointe: {e}")
        return False