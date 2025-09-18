from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML
from crispy_forms.bootstrap import Field
from .models import (
    User, CandidateProfile, Education, Experience, 
    Skill, Language, Certification, Reference
)


class CustomUserCreationForm(UserCreationForm):
    """Formulaire d'inscription personnalisé"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    user_type = forms.ChoiceField(choices=User.USER_TYPES, initial='candidate')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'user_type', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'username',
            'email',
            'user_type',
            'password1',
            'password2',
            Submit('submit', 'S\'inscrire', css_class='btn btn-primary btn-lg w-100')
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Un utilisateur avec cet email existe déjà.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Formulaire de connexion personnalisé"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            Submit('submit', 'Se connecter', css_class='btn btn-primary btn-lg w-100')
        )


class CandidateProfileForm(forms.ModelForm):
    """Formulaire de profil candidat"""
    class Meta:
        model = CandidateProfile
        fields = [
            'profile_picture', 'date_of_birth', 'gender', 'marital_status', 'nationality',
            'address', 'city', 'postal_code', 'country', 'mobile_phone', 'linkedin_url', 'website_url',
            'current_position', 'current_company', 'years_of_experience', 'expected_salary', 'availability_date',
            'cv_file', 'cover_letter', 'willing_to_relocate', 'preferred_work_type'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'availability_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'expected_salary': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4>Informations personnelles</h4>'),
            Row(
                Column('profile_picture', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('date_of_birth', css_class='form-group col-md-4 mb-0'),
                Column('gender', css_class='form-group col-md-4 mb-0'),
                Column('marital_status', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            'nationality',
            
            HTML('<h4 class="mt-4">Adresse</h4>'),
            'address',
            Row(
                Column('city', css_class='form-group col-md-6 mb-0'),
                Column('postal_code', css_class='form-group col-md-3 mb-0'),
                Column('country', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h4 class="mt-4">Contact</h4>'),
            Row(
                Column('mobile_phone', css_class='form-group col-md-4 mb-0'),
                Column('linkedin_url', css_class='form-group col-md-4 mb-0'),
                Column('website_url', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h4 class="mt-4">Informations professionnelles</h4>'),
            Row(
                Column('current_position', css_class='form-group col-md-6 mb-0'),
                Column('current_company', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('years_of_experience', css_class='form-group col-md-4 mb-0'),
                Column('expected_salary', css_class='form-group col-md-4 mb-0'),
                Column('availability_date', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h4 class="mt-4">Documents</h4>'),
            Row(
                Column('cv_file', css_class='form-group col-md-6 mb-0'),
                Column('cover_letter', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h4 class="mt-4">Préférences</h4>'),
            Row(
                Column('willing_to_relocate', css_class='form-group col-md-6 mb-0'),
                Column('preferred_work_type', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            
            Submit('submit', 'Enregistrer le profil', css_class='btn btn-primary btn-lg mt-4')
        )


class EducationForm(forms.ModelForm):
    """Formulaire de formation"""
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'degree_level', 'start_date', 'end_date', 'is_current', 'grade', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'institution',
            Row(
                Column('degree', css_class='form-group col-md-8 mb-0'),
                Column('degree_level', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            'field_of_study',
            Row(
                Column('start_date', css_class='form-group col-md-4 mb-0'),
                Column('end_date', css_class='form-group col-md-4 mb-0'),
                Column('is_current', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            'grade',
            'description',
            Submit('submit', 'Enregistrer', css_class='btn btn-primary')
        )


class ExperienceForm(forms.ModelForm):
    """Formulaire d'expérience"""
    class Meta:
        model = Experience
        fields = [
            'company', 'position', 'employment_type', 'company_size', 'industry', 
            'department', 'location', 'remote_work', 'start_date', 'end_date', 
            'is_current', 'salary', 'salary_currency', 'description', 'achievements', 
            'technologies_used', 'team_size', 'budget_managed'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'achievements': forms.Textarea(attrs={'rows': 3}),
            'technologies_used': forms.Textarea(attrs={'rows': 2}),
            'salary': forms.NumberInput(attrs={'step': '0.01'}),
            'budget_managed': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5>Informations générales</h5>'),
            Row(
                Column('company', css_class='form-group col-md-6 mb-0'),
                Column('position', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('employment_type', css_class='form-group col-md-4 mb-0'),
                Column('company_size', css_class='form-group col-md-4 mb-0'),
                Column('industry', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('department', css_class='form-group col-md-6 mb-0'),
                Column('location', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'remote_work',
            
            HTML('<h5 class="mt-4">Période</h5>'),
            Row(
                Column('start_date', css_class='form-group col-md-4 mb-0'),
                Column('end_date', css_class='form-group col-md-4 mb-0'),
                Column('is_current', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h5 class="mt-4">Rémunération (optionnel)</h5>'),
            Row(
                Column('salary', css_class='form-group col-md-8 mb-0'),
                Column('salary_currency', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h5 class="mt-4">Description</h5>'),
            'description',
            'achievements',
            'technologies_used',
            
            HTML('<h5 class="mt-4">Management (si applicable)</h5>'),
            Row(
                Column('team_size', css_class='form-group col-md-6 mb-0'),
                Column('budget_managed', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            
            Submit('submit', 'Enregistrer', css_class='btn btn-primary')
        )


class SkillForm(forms.ModelForm):
    """Formulaire de compétence"""
    class Meta:
        model = Skill
        fields = ['name', 'level', 'category', 'years_of_experience']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            Row(
                Column('level', css_class='form-group col-md-4 mb-0'),
                Column('category', css_class='form-group col-md-4 mb-0'),
                Column('years_of_experience', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Ajouter', css_class='btn btn-primary')
        )


class LanguageForm(forms.ModelForm):
    """Formulaire de langue"""
    class Meta:
        model = Language
        fields = ['language', 'proficiency']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('language', css_class='form-group col-md-6 mb-0'),
                Column('proficiency', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Ajouter', css_class='btn btn-primary')
        )


class CertificationForm(forms.ModelForm):
    """Formulaire de certification"""
    class Meta:
        model = Certification
        fields = ['name', 'issuing_organization', 'issue_date', 'expiration_date', 'credential_id', 'credential_url']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'issuing_organization',
            Row(
                Column('issue_date', css_class='form-group col-md-6 mb-0'),
                Column('expiration_date', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('credential_id', css_class='form-group col-md-6 mb-0'),
                Column('credential_url', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Ajouter', css_class='btn btn-primary')
        )


class ReferenceForm(forms.ModelForm):
    """Formulaire de référence"""
    class Meta:
        model = Reference
        fields = ['name', 'position', 'company', 'email', 'phone', 'relationship']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('position', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'company',
            Row(
                Column('email', css_class='form-group col-md-6 mb-0'),
                Column('phone', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'relationship',
            Submit('submit', 'Ajouter', css_class='btn btn-primary')
        )