from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import CandidateProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_candidate_profile(sender, instance, created, **kwargs):
    """Créer automatiquement un profil candidat lors de la création d'un utilisateur candidat"""
    if created and instance.user_type == 'candidate':
        CandidateProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_candidate_profile(sender, instance, **kwargs):
    """Sauvegarder le profil candidat lors de la sauvegarde de l'utilisateur"""
    if instance.user_type == 'candidate' and hasattr(instance, 'candidate_profile'):
        instance.candidate_profile.save()
