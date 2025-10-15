from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    CV, CVTemplate, CVSection, CVShare, CVExport, 
    CVFeedback, CVBuilderSettings
)


class CVForm(forms.ModelForm):
    """Formulaire pour créer/modifier un CV"""
    
    class Meta:
        model = CV
        fields = [
            'title', 'template', 'status', 'professional_summary',
            'is_public'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de votre CV'
            }),
            'template': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'professional_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Résumé professionnel...'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class PersonalInfoForm(forms.Form):
    """Formulaire pour les informations personnelles"""
    
    # Informations de base
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Téléphone'
        })
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Site web'
        })
    )
    linkedin = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'LinkedIn'
        })
    )
    github = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'GitHub'
        })
    )
    
    # Adresse
    address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adresse'
        })
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ville'
        })
    )
    postal_code = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Code postal'
        })
    )
    country = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pays'
        })
    )
    
    # Photo
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    # Date de naissance
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    # Nationalité
    nationality = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nationalité'
        })
    )


class ExperienceForm(forms.Form):
    """Formulaire pour une expérience professionnelle"""
    
    job_title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Titre du poste'
        })
    )
    company = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entreprise'
        })
    )
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Localisation'
        })
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    is_current = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Description des responsabilités et réalisations...'
        })
    )
    achievements = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Réalisations principales...'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        is_current = cleaned_data.get('is_current')
        
        if not is_current and end_date and start_date and end_date < start_date:
            raise ValidationError('La date de fin ne peut pas être antérieure à la date de début.')
        
        return cleaned_data


class EducationForm(forms.Form):
    """Formulaire pour une formation"""
    
    degree = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Diplôme'
        })
    )
    institution = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Établissement'
        })
    )
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Localisation'
        })
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    is_current = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    gpa = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Moyenne',
            'step': '0.01',
            'min': '0',
            'max': '4'
        })
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Description de la formation...'
        })
    )


class SkillForm(forms.Form):
    """Formulaire pour une compétence"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom de la compétence'
        })
    )
    category = forms.ChoiceField(
        choices=[
            ('technical', 'Technique'),
            ('soft', 'Soft skills'),
            ('language', 'Langue'),
            ('certification', 'Certification'),
            ('other', 'Autre'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    level = forms.ChoiceField(
        choices=[
            ('beginner', 'Débutant'),
            ('intermediate', 'Intermédiaire'),
            ('advanced', 'Avancé'),
            ('expert', 'Expert'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    years_experience = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=50,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Années d\'expérience'
        })
    )


class ProjectForm(forms.Form):
    """Formulaire pour un projet"""
    
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom du projet'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Description du projet...'
        })
    )
    technologies = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Technologies utilisées (séparer par des virgules)'
        })
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'URL du projet'
        })
    )
    github_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'URL GitHub'
        })
    )


class LanguageForm(forms.Form):
    """Formulaire pour une langue"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom de la langue'
        })
    )
    proficiency = forms.ChoiceField(
        choices=[
            ('native', 'Langue maternelle'),
            ('fluent', 'Courant'),
            ('advanced', 'Avancé'),
            ('intermediate', 'Intermédiaire'),
            ('basic', 'Notions'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    certification = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Certification (ex: TOEFL, DELF)'
        })
    )


class CertificationForm(forms.Form):
    """Formulaire pour une certification"""
    
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom de la certification'
        })
    )
    issuer = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Organisme émetteur'
        })
    )
    issue_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    expiry_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    credential_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ID de la certification'
        })
    )
    credential_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'URL de vérification'
        })
    )


class ReferenceForm(forms.Form):
    """Formulaire pour une référence"""
    
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom complet'
        })
    )
    position = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Poste'
        })
    )
    company = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entreprise'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Téléphone'
        })
    )
    relationship = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Relation professionnelle'
        })
    )


class CVShareForm(forms.ModelForm):
    """Formulaire pour partager un CV"""
    
    class Meta:
        model = CVShare
        fields = ['share_type', 'password', 'expires_at']
        widgets = {
            'share_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mot de passe (optionnel)'
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }


class CVFeedbackForm(forms.ModelForm):
    """Formulaire pour commenter un CV"""
    
    class Meta:
        model = CVFeedback
        fields = ['rating', 'comment', 'is_public']
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'form-control'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Votre commentaire...'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class CVBuilderSettingsForm(forms.ModelForm):
    """Formulaire pour les paramètres du constructeur de CV"""
    
    class Meta:
        model = CVBuilderSettings
        fields = [
            'default_template', 'auto_save', 'auto_save_interval',
            'default_export_format', 'include_contact_info', 'include_photo',
            'default_share_type', 'share_expiry_days'
        ]
        widgets = {
            'default_template': forms.Select(attrs={
                'class': 'form-control'
            }),
            'auto_save': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'auto_save_interval': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 10,
                'max': 300
            }),
            'default_export_format': forms.Select(attrs={
                'class': 'form-control'
            }),
            'include_contact_info': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'include_photo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'default_share_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'share_expiry_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 365
            })
        }


class CVTemplateForm(forms.ModelForm):
    """Formulaire pour créer/modifier un modèle de CV (admin)"""
    
    class Meta:
        model = CVTemplate
        fields = [
            'name', 'description', 'category', 'preview_image',
            'template_file', 'css_file', 'sections', 'layout_config',
            'color_scheme', 'is_premium', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'preview_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'template_file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'css_file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'sections': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'layout_config': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'color_scheme': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'is_premium': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


