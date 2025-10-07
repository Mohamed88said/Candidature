from django import forms
from django.core.exceptions import ValidationError
from apps.matching.models import CandidatePreference, MatchingAlgorithm
from apps.jobs.models import JobCategory


class CandidatePreferenceForm(forms.ModelForm):
    """Formulaire pour les préférences de matching du candidat"""
    
    class Meta:
        model = CandidatePreference
        fields = [
            'preferred_locations', 'max_commute_time', 'willing_to_relocate',
            'remote_work_preference', 'min_salary', 'max_salary', 'salary_negotiable',
            'preferred_company_sizes', 'preferred_industries', 'preferred_company_cultures',
            'preferred_job_types', 'preferred_experience_levels', 'career_goals',
            'excluded_companies', 'excluded_locations', 'excluded_industries',
            'alert_frequency', 'min_match_score', 'only_high_matches'
        ]
        widgets = {
            'preferred_locations': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ex: Paris, Lyon, Marseille (une par ligne)',
                'class': 'form-control'
            }),
            'max_commute_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 300
            }),
            'min_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 100
            }),
            'max_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 100
            }),
            'preferred_company_sizes': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'preferred_industries': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ex: Technologie, Finance, Santé (une par ligne)',
                'class': 'form-control'
            }),
            'preferred_company_cultures': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ex: Startup, International, Familiale (une par ligne)',
                'class': 'form-control'
            }),
            'preferred_job_types': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'preferred_experience_levels': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'career_goals': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Décrivez vos objectifs de carrière...',
                'class': 'form-control'
            }),
            'excluded_companies': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Entreprises à exclure (une par ligne)',
                'class': 'form-control'
            }),
            'excluded_locations': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Localisations à exclure (une par ligne)',
                'class': 'form-control'
            }),
            'excluded_industries': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Secteurs à exclure (une par ligne)',
                'class': 'form-control'
            }),
            'alert_frequency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'min_match_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'remote_work_preference': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Ajouter des choix pour les champs
        self.fields['preferred_company_sizes'].choices = [
            ('startup', 'Startup (1-10)'),
            ('small', 'Petite (11-50)'),
            ('medium', 'Moyenne (51-200)'),
            ('large', 'Grande (201-1000)'),
            ('enterprise', 'Entreprise (1000+)'),
        ]
        
        self.fields['preferred_job_types'].choices = [
            ('full_time', 'Temps plein'),
            ('part_time', 'Temps partiel'),
            ('contract', 'Contrat'),
            ('cdd', 'CDD'),
            ('cdi', 'CDI'),
            ('freelance', 'Freelance'),
            ('internship', 'Stage'),
            ('temporary', 'Temporaire'),
            ('apprenticeship', 'Apprentissage'),
        ]
        
        self.fields['preferred_experience_levels'].choices = [
            ('entry', 'Débutant (0-2 ans)'),
            ('junior', 'Junior (2-5 ans)'),
            ('mid', 'Intermédiaire (5-8 ans)'),
            ('senior', 'Senior (8+ ans)'),
            ('lead', 'Lead/Manager'),
            ('principal', 'Principal'),
            ('director', 'Directeur'),
            ('executive', 'Exécutif'),
            ('c_level', 'C-Level'),
        ]
    
    def clean_max_salary(self):
        """Validation du salaire maximum"""
        min_salary = self.cleaned_data.get('min_salary')
        max_salary = self.cleaned_data.get('max_salary')
        
        if min_salary and max_salary and max_salary < min_salary:
            raise ValidationError("Le salaire maximum doit être supérieur au salaire minimum.")
        
        return max_salary
    
    def clean_preferred_locations(self):
        """Nettoyer et valider les localisations préférées"""
        locations = self.cleaned_data.get('preferred_locations')
        if locations:
            # Nettoyer et valider chaque localisation
            cleaned_locations = []
            for location in locations:
                location = location.strip()
                if location and len(location) > 2:
                    cleaned_locations.append(location)
            
            if len(cleaned_locations) > 20:
                raise ValidationError("Maximum 20 localisations autorisées.")
            
            return cleaned_locations
        return locations
    
    def clean_preferred_industries(self):
        """Nettoyer et valider les industries préférées"""
        industries = self.cleaned_data.get('preferred_industries')
        if industries:
            cleaned_industries = []
            for industry in industries:
                industry = industry.strip()
                if industry and len(industry) > 2:
                    cleaned_industries.append(industry)
            
            if len(cleaned_industries) > 15:
                raise ValidationError("Maximum 15 industries autorisées.")
            
            return cleaned_industries
        return industries


class MatchingAlgorithmForm(forms.ModelForm):
    """Formulaire pour configurer l'algorithme de matching"""
    
    class Meta:
        model = MatchingAlgorithm
        fields = [
            'name', 'description', 'is_active',
            'experience_weight', 'skills_weight', 'location_weight',
            'salary_weight', 'education_weight', 'company_culture_weight',
            'minimum_match_score', 'high_match_threshold',
            'use_ai_analysis', 'consider_soft_skills', 'location_radius_km'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de l\'algorithme'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description de l\'algorithme'
            }),
            'experience_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'skills_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'location_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'salary_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'education_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'company_culture_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'minimum_match_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'high_match_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'location_radius_km': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 500
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'use_ai_analysis': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'consider_soft_skills': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean(self):
        """Validation globale du formulaire"""
        cleaned_data = super().clean()
        
        # Vérifier que la somme des poids ne dépasse pas 100
        weights = [
            cleaned_data.get('experience_weight', 0),
            cleaned_data.get('skills_weight', 0),
            cleaned_data.get('location_weight', 0),
            cleaned_data.get('salary_weight', 0),
            cleaned_data.get('education_weight', 0),
            cleaned_data.get('company_culture_weight', 0),
        ]
        
        total_weight = sum(weights)
        if total_weight > 100:
            raise ValidationError("La somme des poids ne doit pas dépasser 100%.")
        
        # Vérifier que le seuil minimum est inférieur au seuil élevé
        min_score = cleaned_data.get('minimum_match_score', 0)
        high_threshold = cleaned_data.get('high_match_threshold', 0)
        
        if min_score >= high_threshold:
            raise ValidationError("Le seuil minimum doit être inférieur au seuil élevé.")
        
        return cleaned_data


class JobMatchFilterForm(forms.Form):
    """Formulaire de filtrage pour les matches d'emploi"""
    
    SEARCH_CHOICES = [
        ('', 'Tous les matches'),
        ('excellent', 'Excellent (90%+)'),
        ('very_good', 'Très bon (80-89%)'),
        ('good', 'Bon (70-79%)'),
        ('correct', 'Correct (60-69%)'),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par titre, entreprise, localisation...'
        })
    )
    
    min_score = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Score minimum'
        })
    )
    
    match_level = forms.ChoiceField(
        required=False,
        choices=SEARCH_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    job_type = forms.MultipleChoiceField(
        required=False,
        choices=[
            ('full_time', 'Temps plein'),
            ('part_time', 'Temps partiel'),
            ('contract', 'Contrat'),
            ('freelance', 'Freelance'),
            ('internship', 'Stage'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Localisation'
        })
    )
    
    remote_work = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class MatchingPreferencesQuickForm(forms.Form):
    """Formulaire rapide pour les préférences de matching"""
    
    alert_frequency = forms.ChoiceField(
        choices=[
            ('immediate', 'Immédiat'),
            ('daily', 'Quotidien'),
            ('weekly', 'Hebdomadaire'),
            ('monthly', 'Mensuel'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    min_match_score = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=70,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
    
    only_high_matches = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    remote_work_preference = forms.ChoiceField(
        choices=[
            ('office_only', 'Bureau uniquement'),
            ('remote_only', 'Télétravail uniquement'),
            ('hybrid', 'Hybride'),
            ('flexible', 'Flexible'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

