from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Location, JobLocation, MapView, MapBookmark, MapSearch


class LocationForm(forms.ModelForm):
    """Formulaire pour créer/modifier une localisation"""
    
    class Meta:
        model = Location
        fields = [
            'name', 'address', 'city', 'region', 'country', 'postal_code',
            'latitude', 'longitude', 'is_remote', 'is_hybrid'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la localisation'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Adresse complète'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ville'
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Région'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pays'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Code postal'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Latitude'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Longitude'
            }),
            'is_remote': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_hybrid': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        if latitude and longitude:
            # Vérifier que les coordonnées sont dans des plages valides
            if not (-90 <= float(latitude) <= 90):
                raise ValidationError('La latitude doit être entre -90 et 90.')
            
            if not (-180 <= float(longitude) <= 180):
                raise ValidationError('La longitude doit être entre -180 et 180.')
        
        return cleaned_data


class JobLocationForm(forms.ModelForm):
    """Formulaire pour lier une offre à une localisation"""
    
    class Meta:
        model = JobLocation
        fields = [
            'location', 'location_type', 'is_primary', 'work_days_per_week'
        ]
        widgets = {
            'location': forms.Select(attrs={
                'class': 'form-control'
            }),
            'location_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'work_days_per_week': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 7
            })
        }


class MapViewForm(forms.ModelForm):
    """Formulaire pour sauvegarder une vue de carte"""
    
    class Meta:
        model = MapView
        fields = [
            'center_latitude', 'center_longitude', 'zoom_level', 'filters'
        ]
        widgets = {
            'center_latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'readonly': True
            }),
            'center_longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'readonly': True
            }),
            'zoom_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 20,
                'readonly': True
            }),
            'filters': forms.HiddenInput()
        }


class MapBookmarkForm(forms.ModelForm):
    """Formulaire pour créer un signet de carte"""
    
    class Meta:
        model = MapBookmark
        fields = [
            'name', 'description', 'center_latitude', 'center_longitude',
            'zoom_level', 'filters', 'is_public'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du signet'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description du signet'
            }),
            'center_latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'readonly': True
            }),
            'center_longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'readonly': True
            }),
            'zoom_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 20,
                'readonly': True
            }),
            'filters': forms.HiddenInput(),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class MapSearchForm(forms.Form):
    """Formulaire de recherche sur la carte"""
    
    SEARCH_TYPE_CHOICES = [
        ('jobs', 'Offres d\'emploi'),
        ('companies', 'Entreprises'),
        ('locations', 'Localisations'),
    ]
    
    JOB_TYPE_CHOICES = [
        ('', 'Tous les types'),
        ('CDI', 'CDI'),
        ('CDD', 'CDD'),
        ('stage', 'Stage'),
        ('freelance', 'Freelance'),
        ('temps_partiel', 'Temps partiel'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('', 'Tous les niveaux'),
        ('debutant', 'Débutant'),
        ('junior', 'Junior'),
        ('intermediaire', 'Intermédiaire'),
        ('senior', 'Senior'),
        ('expert', 'Expert'),
    ]
    
    # Recherche principale
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher des offres, entreprises, localisations...'
        })
    )
    
    location_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ville, région, pays...'
        })
    )
    
    # Type de recherche
    search_type = forms.ChoiceField(
        choices=SEARCH_TYPE_CHOICES,
        initial='jobs',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    # Filtres géographiques
    radius = forms.FloatField(
        initial=50,
        min_value=1,
        max_value=500,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rayon en km'
        })
    )
    
    # Filtres d'offres
    job_type = forms.ChoiceField(
        choices=JOB_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    experience_level = forms.ChoiceField(
        choices=EXPERIENCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    min_salary = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Salaire minimum'
        })
    )
    
    max_salary = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Salaire maximum'
        })
    )
    
    # Filtres de localisation
    is_remote = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    is_hybrid = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    # Filtres de date
    posted_within = forms.ChoiceField(
        choices=[
            ('', 'Toutes les dates'),
            ('1', 'Dernière heure'),
            ('24', 'Dernières 24h'),
            ('168', 'Dernière semaine'),
            ('720', 'Dernier mois'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        min_salary = cleaned_data.get('min_salary')
        max_salary = cleaned_data.get('max_salary')
        
        if min_salary and max_salary and min_salary > max_salary:
            raise ValidationError('Le salaire minimum ne peut pas être supérieur au salaire maximum.')
        
        return cleaned_data


class MapFilterForm(forms.Form):
    """Formulaire pour les filtres avancés de la carte"""
    
    # Filtres de catégorie
    categories = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    # Filtres de secteur
    industries = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    # Filtres de taille d'entreprise
    company_size = forms.MultipleChoiceField(
        choices=[
            ('startup', 'Startup (1-10 employés)'),
            ('small', 'Petite entreprise (11-50 employés)'),
            ('medium', 'Moyenne entreprise (51-200 employés)'),
            ('large', 'Grande entreprise (201-1000 employés)'),
            ('enterprise', 'Entreprise (1000+ employés)'),
        ],
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    # Filtres de compétences
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Compétences (séparer par des virgules)'
        })
    )
    
    # Filtres de langues
    languages = forms.MultipleChoiceField(
        choices=[
            ('french', 'Français'),
            ('english', 'Anglais'),
            ('spanish', 'Espagnol'),
            ('german', 'Allemand'),
            ('italian', 'Italien'),
            ('portuguese', 'Portugais'),
        ],
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    # Filtres de télétravail
    remote_options = forms.MultipleChoiceField(
        choices=[
            ('full_remote', '100% Télétravail'),
            ('hybrid', 'Hybride'),
            ('on_site', 'Sur site'),
        ],
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    # Filtres de disponibilité
    availability = forms.ChoiceField(
        choices=[
            ('', 'Toutes les disponibilités'),
            ('immediate', 'Immédiate'),
            ('1_month', 'Dans 1 mois'),
            ('3_months', 'Dans 3 mois'),
            ('6_months', 'Dans 6 mois'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class MapSettingsForm(forms.Form):
    """Formulaire pour les paramètres de la carte"""
    
    # Paramètres d'affichage
    map_style = forms.ChoiceField(
        choices=[
            ('roadmap', 'Plan'),
            ('satellite', 'Satellite'),
            ('hybrid', 'Hybride'),
            ('terrain', 'Terrain'),
        ],
        initial='roadmap',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    # Paramètres de clustering
    enable_clustering = forms.BooleanField(
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    cluster_radius = forms.IntegerField(
        initial=50,
        min_value=10,
        max_value=200,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
    
    # Paramètres de heatmap
    enable_heatmap = forms.BooleanField(
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    heatmap_intensity = forms.FloatField(
        initial=0.5,
        min_value=0.1,
        max_value=1.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1'
        })
    )
    
    # Paramètres de performance
    max_markers = forms.IntegerField(
        initial=1000,
        min_value=100,
        max_value=5000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
    
    # Paramètres de notifications
    enable_notifications = forms.BooleanField(
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    notification_radius = forms.IntegerField(
        initial=25,
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
