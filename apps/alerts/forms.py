from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    AlertPreference, AlertType, AlertNotification, AlertTemplate, 
    AlertCampaign, AlertSubscription
)


class AlertPreferenceForm(forms.ModelForm):
    """Formulaire pour les préférences d'alertes"""
    
    class Meta:
        model = AlertPreference
        fields = [
            'email_alerts', 'push_notifications', 'sms_alerts', 'frequency',
            'max_alerts_per_day', 'include_salary', 'include_remote_jobs',
            'include_part_time', 'include_internships', 'max_distance',
            'preferred_locations', 'min_salary', 'max_salary',
            'min_experience', 'max_experience', 'preferred_job_types',
            'preferred_industries', 'preferred_skills', 'enabled_alert_types'
        ]
        widgets = {
            'email_alerts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'push_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_alerts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'max_alerts_per_day': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 50
            }),
            'include_salary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_remote_jobs': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_part_time': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_internships': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_distance': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 500
            }),
            'preferred_locations': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Séparer par des virgules'
            }),
            'min_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Salaire minimum'
            }),
            'max_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Salaire maximum'
            }),
            'min_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50
            }),
            'max_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50
            }),
            'preferred_job_types': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Séparer par des virgules'
            }),
            'preferred_industries': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Séparer par des virgules'
            }),
            'preferred_skills': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Séparer par des virgules'
            }),
            'enabled_alert_types': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        min_salary = cleaned_data.get('min_salary')
        max_salary = cleaned_data.get('max_salary')
        min_experience = cleaned_data.get('min_experience')
        max_experience = cleaned_data.get('max_experience')
        
        if min_salary and max_salary and min_salary > max_salary:
            raise ValidationError('Le salaire minimum ne peut pas être supérieur au salaire maximum.')
        
        if min_experience and max_experience and min_experience > max_experience:
            raise ValidationError('L\'expérience minimum ne peut pas être supérieure à l\'expérience maximum.')
        
        return cleaned_data


class AlertTypeForm(forms.ModelForm):
    """Formulaire pour créer/modifier un type d'alerte"""
    
    class Meta:
        model = AlertType
        fields = ['name', 'description', 'icon', 'color', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du type d\'alerte'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description du type d\'alerte'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'fas fa-bell'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class AlertTemplateForm(forms.ModelForm):
    """Formulaire pour créer/modifier un modèle d'alerte"""
    
    class Meta:
        model = AlertTemplate
        fields = [
            'name', 'alert_type', 'subject_template', 'message_template',
            'html_template', 'available_variables', 'is_active', 'is_default'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du modèle'
            }),
            'alert_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'subject_template': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modèle de sujet'
            }),
            'message_template': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Modèle de message'
            }),
            'html_template': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Modèle HTML'
            }),
            'available_variables': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Variables disponibles (une par ligne)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class AlertCampaignForm(forms.ModelForm):
    """Formulaire pour créer/modifier une campagne d'alertes"""
    
    class Meta:
        model = AlertCampaign
        fields = [
            'name', 'description', 'alert_type', 'subject', 'message',
            'html_content', 'scheduled_at', 'target_criteria'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la campagne'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description de la campagne'
            }),
            'alert_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sujet de l\'alerte'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Message de l\'alerte'
            }),
            'html_content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Contenu HTML'
            }),
            'scheduled_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'target_criteria': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Critères de ciblage (JSON)'
            })
        }
    
    def clean_scheduled_at(self):
        scheduled_at = self.cleaned_data.get('scheduled_at')
        if scheduled_at and scheduled_at <= timezone.now():
            raise ValidationError('La date de programmation doit être dans le futur.')
        return scheduled_at


class AlertSubscriptionForm(forms.ModelForm):
    """Formulaire pour créer/modifier un abonnement d'alerte"""
    
    class Meta:
        model = AlertSubscription
        fields = [
            'alert_type', 'keywords', 'locations', 'job_types',
            'industries', 'salary_range', 'frequency', 'is_active'
        ]
        widgets = {
            'alert_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mots-clés (séparer par des virgules)'
            }),
            'locations': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Localisations (séparer par des virgules)'
            }),
            'job_types': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Types d\'emploi (séparer par des virgules)'
            }),
            'industries': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Secteurs (séparer par des virgules)'
            }),
            'frequency': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class AlertSearchForm(forms.Form):
    """Formulaire de recherche d'alertes"""
    
    SEARCH_CHOICES = [
        ('', 'Toutes les alertes'),
        ('unread', 'Non lues'),
        ('read', 'Lues'),
        ('clicked', 'Cliquées'),
        ('today', 'Aujourd\'hui'),
        ('week', 'Cette semaine'),
        ('month', 'Ce mois'),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher dans les alertes...'
        })
    )
    alert_type = forms.ModelChoiceField(
        queryset=AlertType.objects.filter(is_active=True),
        required=False,
        empty_label="Tous les types",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    status = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class AlertSettingsForm(forms.Form):
    """Formulaire pour les paramètres d'alertes"""
    
    # Paramètres de notification
    enable_notifications = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    notification_sound = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    # Paramètres d'affichage
    alerts_per_page = forms.ChoiceField(
        choices=[
            (10, '10 alertes par page'),
            (25, '25 alertes par page'),
            (50, '50 alertes par page'),
            (100, '100 alertes par page')
        ],
        initial=25,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    # Paramètres de tri
    sort_by = forms.ChoiceField(
        choices=[
            ('-created_at', 'Plus récentes'),
            ('created_at', 'Plus anciennes'),
            ('match_score', 'Score de correspondance'),
            ('job__title', 'Titre de l\'offre'),
            ('alert_type__name', 'Type d\'alerte')
        ],
        initial='-created_at',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    # Paramètres de filtrage automatique
    auto_mark_read = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    hide_low_score_alerts = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    min_match_score = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        initial=50,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Score minimum de correspondance'
        })
    )


class AlertFeedbackForm(forms.Form):
    """Formulaire pour les commentaires sur les alertes"""
    
    RATING_CHOICES = [
        (1, 'Très peu pertinent'),
        (2, 'Peu pertinent'),
        (3, 'Moyennement pertinent'),
        (4, 'Pertinent'),
        (5, 'Très pertinent'),
    ]
    
    alert_id = forms.IntegerField(widget=forms.HiddenInput())
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Vos commentaires sur cette alerte...'
        })
    )
    reason = forms.ChoiceField(
        choices=[
            ('', 'Sélectionner une raison'),
            ('not_relevant', 'Pas pertinent pour mon profil'),
            ('wrong_location', 'Mauvaise localisation'),
            ('wrong_salary', 'Salaire inapproprié'),
            ('wrong_experience', 'Niveau d\'expérience incorrect'),
            ('already_applied', 'J\'ai déjà postulé'),
            ('not_interested', 'Pas intéressé par ce type d\'emploi'),
            ('other', 'Autre')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class BulkAlertActionForm(forms.Form):
    """Formulaire pour les actions en lot sur les alertes"""
    
    ACTION_CHOICES = [
        ('', 'Sélectionner une action'),
        ('mark_read', 'Marquer comme lues'),
        ('mark_unread', 'Marquer comme non lues'),
        ('delete', 'Supprimer'),
        ('archive', 'Archiver'),
        ('unsubscribe', 'Se désabonner de ce type')
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    alert_ids = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    def clean_alert_ids(self):
        alert_ids = self.cleaned_data.get('alert_ids')
        if alert_ids:
            try:
                return [int(id) for id in alert_ids.split(',')]
            except ValueError:
                raise ValidationError('IDs d\'alertes invalides.')
        return []
