from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    ReferralProgram, ReferralCode, Referral, ReferralReward,
    ReferralInvitation, ReferralLeaderboard, ReferralAnalytics
)


class ReferralInvitationForm(forms.Form):
    """Formulaire pour inviter des amis"""
    
    # Informations de l'invitation
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email de votre ami'
        })
    )
    name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom de votre ami (optionnel)'
        })
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Message personnalisé (optionnel)'
        })
    )
    
    # Options d'invitation
    send_email = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    send_sms = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    send_whatsapp = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Vérifier si l'email existe déjà dans le système
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            raise ValidationError('Cette personne est déjà inscrite sur la plateforme.')
        return email


class BulkInvitationForm(forms.Form):
    """Formulaire pour inviter plusieurs amis en masse"""
    
    emails = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Entrez les emails séparés par des virgules ou des retours à la ligne'
        }),
        help_text='Séparez les emails par des virgules ou des retours à la ligne'
    )
    
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Message personnalisé pour tous'
        })
    )
    
    def clean_emails(self):
        emails_text = self.cleaned_data.get('emails')
        emails = []
        
        # Parser les emails
        for line in emails_text.split('\n'):
            for email in line.split(','):
                email = email.strip()
                if email and '@' in email:
                    emails.append(email)
        
        if not emails:
            raise ValidationError('Aucun email valide trouvé.')
        
        if len(emails) > 50:
            raise ValidationError('Vous ne pouvez pas inviter plus de 50 personnes à la fois.')
        
        # Vérifier les doublons
        if len(emails) != len(set(emails)):
            raise ValidationError('Des emails en double ont été détectés.')
        
        return emails


class ReferralCodeForm(forms.ModelForm):
    """Formulaire pour créer un code de recommandation personnalisé"""
    
    class Meta:
        model = ReferralCode
        fields = ['code']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre code personnalisé',
                'maxlength': 20
            })
        }
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            # Vérifier que le code est unique
            if ReferralCode.objects.filter(code=code).exists():
                raise ValidationError('Ce code est déjà utilisé.')
            
            # Vérifier le format
            if not code.replace('_', '').replace('-', '').isalnum():
                raise ValidationError('Le code ne peut contenir que des lettres, chiffres, tirets et underscores.')
        
        return code


class ReferralProgramForm(forms.ModelForm):
    """Formulaire pour créer/modifier un programme de recommandation (admin)"""
    
    class Meta:
        model = ReferralProgram
        fields = [
            'name', 'description', 'referrer_reward', 'referee_reward',
            'min_referrals_for_bonus', 'bonus_reward', 'max_referrals_per_user',
            'max_rewards_per_user', 'is_active', 'start_date', 'end_date'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'referrer_reward': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '{"type": "points", "amount": 100}'
            }),
            'referee_reward': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '{"type": "points", "amount": 50}'
            }),
            'bonus_reward': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '{"type": "points", "amount": 500}'
            }),
            'min_referrals_for_bonus': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'max_referrals_per_user': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'max_rewards_per_user': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date <= start_date:
            raise ValidationError('La date de fin doit être postérieure à la date de début.')
        
        return cleaned_data


class ReferralRewardForm(forms.ModelForm):
    """Formulaire pour gérer les récompenses"""
    
    class Meta:
        model = ReferralReward
        fields = ['reward_type', 'amount', 'description']
        widgets = {
            'reward_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }


class ReferralSearchForm(forms.Form):
    """Formulaire de recherche pour les recommandations"""
    
    STATUS_CHOICES = [
        ('', 'Tous les statuts'),
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('cancelled', 'Annulé'),
        ('expired', 'Expiré'),
    ]
    
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par nom, email...'
        })
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
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


class ReferralSettingsForm(forms.Form):
    """Formulaire pour les paramètres de recommandation de l'utilisateur"""
    
    # Paramètres de notification
    email_notifications = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    push_notifications = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    # Paramètres de partage
    auto_share_on_social = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    default_invitation_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Message par défaut pour vos invitations'
        })
    )
    
    # Paramètres de confidentialité
    show_in_leaderboard = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    allow_public_referral_code = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class ReferralFeedbackForm(forms.Form):
    """Formulaire pour le feedback sur le programme de recommandation"""
    
    RATING_CHOICES = [
        (1, '1 étoile'),
        (2, '2 étoiles'),
        (3, '3 étoiles'),
        (4, '4 étoiles'),
        (5, '5 étoiles'),
    ]
    
    SATISFACTION_CHOICES = [
        ('very_satisfied', 'Très satisfait'),
        ('satisfied', 'Satisfait'),
        ('neutral', 'Neutre'),
        ('dissatisfied', 'Mécontent'),
        ('very_dissatisfied', 'Très mécontent'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    satisfaction = forms.ChoiceField(
        choices=SATISFACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Votre avis sur le programme de recommandation...'
        })
    )
    
    suggestions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Suggestions d\'amélioration...'
        })
    )


class ReferralLeaderboardForm(forms.Form):
    """Formulaire pour filtrer le classement"""
    
    PERIOD_CHOICES = [
        ('all_time', 'Tous les temps'),
        ('this_month', 'Ce mois'),
        ('last_month', 'Le mois dernier'),
        ('this_year', 'Cette année'),
        ('last_year', 'L\'année dernière'),
    ]
    
    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        initial='all_time',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    program = forms.ModelChoiceField(
        queryset=ReferralProgram.objects.filter(is_active=True),
        required=False,
        empty_label='Tous les programmes',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class ReferralAnalyticsForm(forms.Form):
    """Formulaire pour les analytics de recommandation"""
    
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    program = forms.ModelChoiceField(
        queryset=ReferralProgram.objects.filter(is_active=True),
        required=False,
        empty_label='Tous les programmes',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_to < date_from:
            raise ValidationError('La date de fin doit être postérieure à la date de début.')
        
        return cleaned_data
