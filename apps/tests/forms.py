from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
import json

from .models import (
    Test, TestCategory, JobTest, TestAttempt, TestResult, 
    TestCertificate, TestAnalytics
)


class TestCategoryForm(forms.ModelForm):
    """Formulaire pour créer/modifier une catégorie de test"""
    
    class Meta:
        model = TestCategory
        fields = ['name', 'description', 'icon', 'color', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la catégorie'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description de la catégorie'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'fas fa-clipboard-check'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class TestForm(forms.ModelForm):
    """Formulaire pour créer/modifier un test"""
    
    class Meta:
        model = Test
        fields = [
            'title', 'description', 'category', 'difficulty', 'status',
            'time_limit', 'max_attempts', 'passing_score'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du test'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description du test'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'time_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Durée en minutes (0 = illimité)'
            }),
            'max_attempts': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Nombre maximum de tentatives'
            }),
            'passing_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'placeholder': 'Score de réussite (%)'
            })
        }


class QuestionForm(forms.Form):
    """Formulaire pour créer une question"""
    
    QUESTION_TYPES = [
        ('multiple_choice', 'Choix multiple'),
        ('multiple_select', 'Sélection multiple'),
        ('true_false', 'Vrai/Faux'),
        ('text', 'Texte libre'),
        ('code', 'Code'),
        ('essay', 'Rédaction'),
    ]
    
    question_type = forms.ChoiceField(
        choices=QUESTION_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    question_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Texte de la question'
        })
    )
    points = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Points'
        })
    )
    explanation = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Explication de la réponse'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get('question_type')
        
        # Validation spécifique selon le type de question
        if question_type == 'multiple_choice':
            # Vérifier qu'il y a au moins 2 options
            pass
        elif question_type == 'multiple_select':
            # Vérifier qu'il y a au moins 2 options
            pass
        elif question_type == 'true_false':
            # Pas d'options nécessaires
            pass
        
        return cleaned_data


class TestAttemptForm(forms.ModelForm):
    """Formulaire pour une tentative de test"""
    
    class Meta:
        model = TestAttempt
        fields = ['answers']
        widgets = {
            'answers': forms.HiddenInput()
        }
    
    def __init__(self, *args, **kwargs):
        self.test = kwargs.pop('test', None)
        self.candidate = kwargs.pop('candidate', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        
        if not self.test:
            raise ValidationError('Test non spécifié')
        
        if not self.candidate:
            raise ValidationError('Candidat non spécifié')
        
        # Vérifier si le candidat a déjà atteint le nombre maximum de tentatives
        existing_attempts = TestAttempt.objects.filter(
            candidate=self.candidate,
            test=self.test
        ).count()
        
        if existing_attempts >= self.test.max_attempts:
            raise ValidationError(f'Nombre maximum de tentatives atteint ({self.test.max_attempts})')
        
        return cleaned_data


class JobTestForm(forms.ModelForm):
    """Formulaire pour associer un test à une offre d'emploi"""
    
    class Meta:
        model = JobTest
        fields = ['test', 'is_required', 'order']
        widgets = {
            'test': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Ordre d\'affichage'
            })
        }


class TestSearchForm(forms.Form):
    """Formulaire de recherche de tests"""
    
    SEARCH_CHOICES = [
        ('', 'Tous les tests'),
        ('my_tests', 'Mes tests'),
        ('available_tests', 'Tests disponibles'),
        ('completed_tests', 'Tests terminés'),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher un test...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=TestCategory.objects.filter(is_active=True),
        required=False,
        empty_label="Toutes les catégories",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    difficulty = forms.ChoiceField(
        choices=[('', 'Toutes les difficultés')] + Test.DIFFICULTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    test_type = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class TestAnalyticsForm(forms.ModelForm):
    """Formulaire pour les analytics de test"""
    
    class Meta:
        model = TestAnalytics
        fields = ['test', 'date']
        widgets = {
            'test': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }


class TestCertificateForm(forms.ModelForm):
    """Formulaire pour générer un certificat"""
    
    class Meta:
        model = TestCertificate
        fields = ['expires_at']
        widgets = {
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }


class TestSettingsForm(forms.Form):
    """Formulaire pour les paramètres de test"""
    
    # Paramètres généraux
    auto_save = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    show_correct_answers = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    allow_review = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    # Paramètres d'affichage
    questions_per_page = forms.ChoiceField(
        choices=[
            (1, '1 question par page'),
            (5, '5 questions par page'),
            (10, '10 questions par page'),
            (0, 'Toutes les questions')
        ],
        initial=1,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    # Paramètres de sécurité
    prevent_copy_paste = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    fullscreen_mode = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class TestFeedbackForm(forms.Form):
    """Formulaire pour les commentaires sur un test"""
    
    RATING_CHOICES = [
        (1, 'Très difficile'),
        (2, 'Difficile'),
        (3, 'Moyen'),
        (4, 'Facile'),
        (5, 'Très facile'),
    ]
    
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
            'rows': 4,
            'placeholder': 'Vos commentaires sur ce test...'
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



