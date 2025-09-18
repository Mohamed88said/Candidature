from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML
from .models import Job, JobCategory, JobSkill, JobAlert


class JobForm(forms.ModelForm):
    """Formulaire de création/édition d'offre d'emploi"""
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'category', 'job_type', 'experience_level',
            'location', 'remote_work', 'description', 'requirements', 
            'responsibilities', 'benefits', 'salary_min', 'salary_max',
            'salary_currency', 'salary_period', 'application_deadline',
            'start_date', 'featured', 'urgent'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'responsibilities': forms.Textarea(attrs={'rows': 4}),
            'benefits': forms.Textarea(attrs={'rows': 3}),
            'application_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'salary_min': forms.NumberInput(attrs={'step': '0.01'}),
            'salary_max': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4>Informations générales</h4>'),
            Row(
                Column('title', css_class='form-group col-md-8 mb-0'),
                Column('company', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('category', css_class='form-group col-md-4 mb-0'),
                Column('job_type', css_class='form-group col-md-4 mb-0'),
                Column('experience_level', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h4 class="mt-4">Localisation</h4>'),
            Row(
                Column('location', css_class='form-group col-md-8 mb-0'),
                Column('remote_work', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h4 class="mt-4">Description du poste</h4>'),
            'description',
            'requirements',
            'responsibilities',
            'benefits',
            
            HTML('<h4 class="mt-4">Rémunération</h4>'),
            Row(
                Column('salary_min', css_class='form-group col-md-3 mb-0'),
                Column('salary_max', css_class='form-group col-md-3 mb-0'),
                Column('salary_currency', css_class='form-group col-md-3 mb-0'),
                Column('salary_period', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h4 class="mt-4">Dates importantes</h4>'),
            Row(
                Column('application_deadline', css_class='form-group col-md-6 mb-0'),
                Column('start_date', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h4 class="mt-4">Options</h4>'),
            Row(
                Column('featured', css_class='form-group col-md-6 mb-0'),
                Column('urgent', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            
            Submit('submit', 'Enregistrer l\'offre', css_class='btn btn-primary btn-lg mt-4')
        )

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise ValidationError("Le salaire minimum ne peut pas être supérieur au salaire maximum.")
        
        return cleaned_data


class JobSkillForm(forms.ModelForm):
    """Formulaire pour ajouter des compétences à une offre"""
    class Meta:
        model = JobSkill
        fields = ['skill_name', 'level', 'years_required']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('skill_name', css_class='form-group col-md-6 mb-0'),
                Column('level', css_class='form-group col-md-3 mb-0'),
                Column('years_required', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Ajouter', css_class='btn btn-primary')
        )


class JobSearchForm(forms.Form):
    """Formulaire de recherche d'emplois"""
    keywords = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Mots-clés, titre du poste...'})
    )
    location = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ville, région...'})
    )
    category = forms.ModelChoiceField(
        queryset=JobCategory.objects.filter(is_active=True),
        required=False,
        empty_label="Toutes les catégories"
    )
    job_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Tous les types')] + list(Job.JOB_TYPES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    experience_level = forms.ChoiceField(
        required=False,
        choices=[('', 'Tous les niveaux')] + list(Job.EXPERIENCE_LEVELS)
    )
    remote_work = forms.BooleanField(required=False, label='Télétravail possible')
    salary_min = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Salaire minimum'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('keywords', css_class='form-group col-md-4 mb-0'),
                Column('location', css_class='form-group col-md-4 mb-0'),
                Column('category', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('job_type', css_class='form-group col-md-3 mb-0'),
                Column('experience_level', css_class='form-group col-md-3 mb-0'),
                Column('salary_min', css_class='form-group col-md-3 mb-0'),
                Column('remote_work', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Rechercher', css_class='btn btn-primary')
        )


class JobAlertForm(forms.ModelForm):
    """Formulaire pour créer une alerte emploi"""
    class Meta:
        model = JobAlert
        fields = [
            'title', 'keywords', 'location', 'category', 'job_type',
            'experience_level', 'salary_min', 'remote_work', 'email_frequency'
        ]
        widgets = {
            'keywords': forms.TextInput(attrs={'placeholder': 'Mots-clés séparés par des virgules'}),
            'location': forms.TextInput(attrs={'placeholder': 'Ville, région...'}),
            'salary_min': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            Row(
                Column('keywords', css_class='form-group col-md-6 mb-0'),
                Column('location', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('category', css_class='form-group col-md-4 mb-0'),
                Column('job_type', css_class='form-group col-md-4 mb-0'),
                Column('experience_level', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('salary_min', css_class='form-group col-md-4 mb-0'),
                Column('remote_work', css_class='form-group col-md-4 mb-0'),
                Column('email_frequency', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Créer l\'alerte', css_class='btn btn-primary')
        )