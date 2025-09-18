from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML
from .models import ContactMessage, Newsletter


class ContactForm(forms.ModelForm):
    """Formulaire de contact"""
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-6 mb-0'),
                Column('subject', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'message',
            Submit('submit', 'Envoyer le message', css_class='btn btn-primary btn-lg')
        )


class NewsletterForm(forms.ModelForm):
    """Formulaire d'abonnement à la newsletter"""
    class Meta:
        model = Newsletter
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Votre adresse email'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            'email',
            Submit('submit', 'S\'abonner', css_class='btn btn-primary ml-2')
        )


class SearchForm(forms.Form):
    """Formulaire de recherche globale"""
    query = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Rechercher des offres, entreprises...',
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            'query',
            Submit('submit', 'Rechercher', css_class='btn btn-primary ml-2')
        )