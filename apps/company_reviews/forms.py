from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    Company, CompanyReview, ReviewHelpful, ReviewResponse,
    CompanySalary, CompanyInterview, CompanyBenefit, CompanyPhoto
)


class CompanyForm(forms.ModelForm):
    """Formulaire pour créer/modifier une entreprise"""
    
    class Meta:
        model = Company
        fields = [
            'name', 'description', 'website', 'industry', 'size',
            'founded_year', 'headquarters', 'email', 'phone',
            'logo', 'cover_image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de l\'entreprise'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description de l\'entreprise'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.example.com'
            }),
            'industry': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Secteur d\'activité'
            }),
            'size': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('', 'Sélectionner la taille'),
                ('1-10', '1-10 employés'),
                ('11-50', '11-50 employés'),
                ('51-200', '51-200 employés'),
                ('201-500', '201-500 employés'),
                ('501-1000', '501-1000 employés'),
                ('1000+', '1000+ employés'),
            ]),
            'founded_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1800',
                'max': '2024'
            }),
            'headquarters': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ville, Pays'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@entreprise.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+33 1 23 45 67 89'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }


class CompanyReviewForm(forms.ModelForm):
    """Formulaire pour créer/modifier un avis sur une entreprise"""
    
    class Meta:
        model = CompanyReview
        fields = [
            'job_title', 'employment_status', 'employment_start_date', 'employment_end_date',
            'is_current_employee', 'overall_rating', 'work_life_balance', 'salary_benefits',
            'job_security', 'management', 'culture', 'career_opportunities',
            'pros', 'cons', 'advice_to_management', 'would_recommend', 'is_anonymous'
        ]
        widgets = {
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre poste'
            }),
            'employment_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'employment_start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'employment_end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_current_employee': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'overall_rating': forms.Select(attrs={
                'class': 'form-control'
            }),
            'work_life_balance': forms.Select(attrs={
                'class': 'form-control'
            }),
            'salary_benefits': forms.Select(attrs={
                'class': 'form-control'
            }),
            'job_security': forms.Select(attrs={
                'class': 'form-control'
            }),
            'management': forms.Select(attrs={
                'class': 'form-control'
            }),
            'culture': forms.Select(attrs={
                'class': 'form-control'
            }),
            'career_opportunities': forms.Select(attrs={
                'class': 'form-control'
            }),
            'pros': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez les points positifs de votre expérience...'
            }),
            'cons': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez les points négatifs de votre expérience...'
            }),
            'advice_to_management': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Conseils que vous donneriez à la direction...'
            }),
            'would_recommend': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        employment_start_date = cleaned_data.get('employment_start_date')
        employment_end_date = cleaned_data.get('employment_end_date')
        is_current_employee = cleaned_data.get('is_current_employee')
        
        if not is_current_employee and not employment_end_date:
            raise ValidationError('La date de fin est requise si vous n\'êtes plus employé.')
        
        if employment_end_date and employment_start_date and employment_end_date < employment_start_date:
            raise ValidationError('La date de fin ne peut pas être antérieure à la date de début.')
        
        return cleaned_data


class ReviewHelpfulForm(forms.ModelForm):
    """Formulaire pour voter sur l'utilité d'un avis"""
    
    class Meta:
        model = ReviewHelpful
        fields = ['is_helpful']
        widgets = {
            'is_helpful': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class ReviewResponseForm(forms.ModelForm):
    """Formulaire pour répondre à un avis (entreprise)"""
    
    class Meta:
        model = ReviewResponse
        fields = ['response_text']
        widgets = {
            'response_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Votre réponse à cet avis...'
            })
        }


class CompanySalaryForm(forms.ModelForm):
    """Formulaire pour ajouter des informations salariales"""
    
    class Meta:
        model = CompanySalary
        fields = [
            'job_title', 'department', 'location', 'base_salary', 'bonus',
            'total_compensation', 'currency', 'employment_type', 'experience_level',
            'years_at_company', 'is_anonymous'
        ]
        widgets = {
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre poste'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Département'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ville, Pays'
            }),
            'base_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Salaire de base'
            }),
            'bonus': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Prime (optionnel)'
            }),
            'total_compensation': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Rémunération totale'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('EUR', 'EUR'),
                ('USD', 'USD'),
                ('GBP', 'GBP'),
                ('CHF', 'CHF'),
            ]),
            'employment_type': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('', 'Sélectionner le type'),
                ('full_time', 'Temps plein'),
                ('part_time', 'Temps partiel'),
                ('contract', 'Contrat'),
                ('internship', 'Stage'),
                ('freelance', 'Freelance'),
            ]),
            'experience_level': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('', 'Sélectionner le niveau'),
                ('entry', 'Débutant'),
                ('junior', 'Junior'),
                ('mid', 'Intermédiaire'),
                ('senior', 'Senior'),
                ('lead', 'Lead'),
                ('executive', 'Direction'),
            ]),
            'years_at_company': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '50'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class CompanyInterviewForm(forms.ModelForm):
    """Formulaire pour ajouter une expérience d'entretien"""
    
    class Meta:
        model = CompanyInterview
        fields = [
            'job_title', 'department', 'interview_date', 'interview_type',
            'difficulty', 'duration', 'interview_questions', 'interview_process',
            'outcome', 'offer_made', 'offer_amount', 'overall_experience',
            'pros', 'cons', 'advice', 'is_anonymous'
        ]
        widgets = {
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Poste pour lequel vous avez postulé'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Département'
            }),
            'interview_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'interview_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Entretien téléphonique, Vidéo, Sur site'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-control'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Durée en minutes'
            }),
            'interview_questions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez les questions qui vous ont été posées...'
            }),
            'interview_process': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Décrivez le processus d\'entretien...'
            }),
            'outcome': forms.Select(attrs={
                'class': 'form-control'
            }),
            'offer_made': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'offer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Montant de l\'offre (optionnel)'
            }),
            'overall_experience': forms.Select(attrs={
                'class': 'form-control'
            }),
            'pros': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Points positifs de l\'entretien...'
            }),
            'cons': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Points négatifs de l\'entretien...'
            }),
            'advice': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Conseils pour les futurs candidats...'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class CompanyBenefitForm(forms.ModelForm):
    """Formulaire pour ajouter des avantages d'entreprise"""
    
    class Meta:
        model = CompanyBenefit
        fields = ['name', 'description', 'category', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de l\'avantage'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description de l\'avantage'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('', 'Sélectionner la catégorie'),
                ('health', 'Santé'),
                ('retirement', 'Retraite'),
                ('vacation', 'Vacances'),
                ('professional', 'Développement professionnel'),
                ('family', 'Famille'),
                ('wellness', 'Bien-être'),
                ('financial', 'Financier'),
                ('other', 'Autre'),
            ]),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class CompanyPhotoForm(forms.ModelForm):
    """Formulaire pour ajouter des photos d'entreprise"""
    
    class Meta:
        model = CompanyPhoto
        fields = ['photo', 'caption']
        widgets = {
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Légende de la photo'
            })
        }


class CompanySearchForm(forms.Form):
    """Formulaire de recherche d'entreprises"""
    
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher une entreprise...'
        })
    )
    
    industry = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Secteur d\'activité'
        })
    )
    
    size = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Toutes les tailles'),
            ('1-10', '1-10 employés'),
            ('11-50', '11-50 employés'),
            ('51-200', '51-200 employés'),
            ('201-500', '201-500 employés'),
            ('501-1000', '501-1000 employés'),
            ('1000+', '1000+ employés'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Localisation'
        })
    )
    
    min_rating = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Toutes les notes'),
            ('1', '1 étoile et plus'),
            ('2', '2 étoiles et plus'),
            ('3', '3 étoiles et plus'),
            ('4', '4 étoiles et plus'),
            ('5', '5 étoiles'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class ReviewSearchForm(forms.Form):
    """Formulaire de recherche d'avis"""
    
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher dans les avis...'
        })
    )
    
    rating = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Toutes les notes'),
            ('1', '1 étoile'),
            ('2', '2 étoiles'),
            ('3', '3 étoiles'),
            ('4', '4 étoiles'),
            ('5', '5 étoiles'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    employment_status = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Tous les statuts'),
            ('current', 'Employé actuel'),
            ('former', 'Ancien employé'),
            ('contractor', 'Prestataire'),
            ('intern', 'Stagiaire'),
            ('other', 'Autre'),
        ],
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


