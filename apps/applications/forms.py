from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML, Field
from .models import Application, ApplicationComment, Interview, ApplicationRating
from apps.jobs.models import Job


class ApplicationForm(forms.ModelForm):
    """Formulaire de candidature"""
    class Meta:
        model = Application
        fields = [
            'cover_letter', 'resume_file', 'additional_documents',
            'expected_salary', 'availability_date', 'willing_to_relocate'
        ]
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 8, 'placeholder': 'Expliquez pourquoi vous êtes le candidat idéal pour ce poste...'}),
            'availability_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_salary': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Salaire souhaité'}),
        }

    def __init__(self, *args, **kwargs):
        self.job = kwargs.pop('job', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4>Lettre de motivation</h4>'),
            'cover_letter',
            
            HTML('<h4 class="mt-4">Documents</h4>'),
            Row(
                Column('resume_file', css_class='form-group col-md-6 mb-0'),
                Column('additional_documents', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h4 class="mt-4">Informations supplémentaires</h4>'),
            Row(
                Column('expected_salary', css_class='form-group col-md-4 mb-0'),
                Column('availability_date', css_class='form-group col-md-4 mb-0'),
                Column('willing_to_relocate', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            
            Submit('submit', 'Envoyer ma candidature', css_class='btn btn-primary btn-lg mt-4')
        )

    def clean_cover_letter(self):
        cover_letter = self.cleaned_data.get('cover_letter')
        if len(cover_letter) < 100:
            raise ValidationError("La lettre de motivation doit contenir au moins 100 caractères.")
        return cover_letter

    def clean_resume_file(self):
        resume_file = self.cleaned_data.get('resume_file')
        if resume_file:
            # Vérifier la taille du fichier (5MB max)
            if resume_file.size > 5 * 1024 * 1024:
                raise ValidationError("Le fichier CV ne peut pas dépasser 5MB.")
            
            # Vérifier l'extension
            allowed_extensions = ['.pdf', '.doc', '.docx']
            file_extension = resume_file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError("Seuls les fichiers PDF, DOC et DOCX sont autorisés pour le CV.")
        
        return resume_file


class ApplicationStatusForm(forms.ModelForm):
    """Formulaire pour changer le statut d'une candidature"""
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Raison du changement de statut (optionnel)"
    )

    class Meta:
        model = Application
        fields = ['status', 'priority']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('status', css_class='form-group col-md-6 mb-0'),
                Column('priority', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'reason',
            Submit('submit', 'Mettre à jour', css_class='btn btn-primary')
        )


class ApplicationCommentForm(forms.ModelForm):
    """Formulaire pour ajouter un commentaire"""
    class Meta:
        model = ApplicationComment
        fields = ['comment_type', 'content', 'is_internal']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('comment_type', css_class='form-group col-md-6 mb-0'),
                Column('is_internal', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'content',
            Submit('submit', 'Ajouter le commentaire', css_class='btn btn-primary')
        )


class InterviewForm(forms.ModelForm):
    """Formulaire pour programmer un entretien"""
    class Meta:
        model = Interview
        fields = [
            'interview_type', 'scheduled_date', 'duration_minutes',
            'location', 'interviewers'
        ]
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'interviewers': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrer les interviewers (admin et HR seulement)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields['interviewers'].queryset = User.objects.filter(
            user_type__in=['admin', 'hr']
        )
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('interview_type', css_class='form-group col-md-6 mb-0'),
                Column('scheduled_date', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('duration_minutes', css_class='form-group col-md-6 mb-0'),
                Column('location', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Field('interviewers', template='crispy/checkbox_select_multiple.html'),
            Submit('submit', 'Programmer l\'entretien', css_class='btn btn-primary')
        )


class InterviewFeedbackForm(forms.ModelForm):
    """Formulaire pour le feedback d'entretien"""
    class Meta:
        model = Interview
        fields = ['notes', 'overall_rating', 'recommendation', 'status']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 6}),
            'overall_rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'notes',
            Row(
                Column('overall_rating', css_class='form-group col-md-4 mb-0'),
                Column('recommendation', css_class='form-group col-md-4 mb-0'),
                Column('status', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enregistrer le feedback', css_class='btn btn-primary')
        )


class ApplicationRatingForm(forms.ModelForm):
    """Formulaire pour évaluer une candidature"""
    class Meta:
        model = ApplicationRating
        fields = ['criteria', 'score', 'max_score', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),
            'score': forms.NumberInput(attrs={'min': 1}),
            'max_score': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('criteria', css_class='form-group col-md-4 mb-0'),
                Column('score', css_class='form-group col-md-4 mb-0'),
                Column('max_score', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            'comments',
            Submit('submit', 'Enregistrer l\'évaluation', css_class='btn btn-primary')
        )

    def clean(self):
        cleaned_data = super().clean()
        score = cleaned_data.get('score')
        max_score = cleaned_data.get('max_score')
        
        if score and max_score and score > max_score:
            raise ValidationError("Le score ne peut pas être supérieur au score maximum.")
        
        return cleaned_data


class ApplicationSearchForm(forms.Form):
    """Formulaire de recherche de candidatures"""
    keywords = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nom, email, poste...'})
    )
    job = forms.ModelChoiceField(
        queryset=Job.objects.filter(status='published'),
        required=False,
        empty_label="Toutes les offres"
    )
    status = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + list(Application.STATUS_CHOICES),
        required=False
    )
    priority = forms.ChoiceField(
        choices=[('', 'Toutes les priorités')] + list(Application.PRIORITY_CHOICES),
        required=False
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('keywords', css_class='form-group col-md-4 mb-0'),
                Column('job', css_class='form-group col-md-4 mb-0'),
                Column('status', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('priority', css_class='form-group col-md-4 mb-0'),
                Column('date_from', css_class='form-group col-md-4 mb-0'),
                Column('date_to', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Rechercher', css_class='btn btn-primary')
        )
