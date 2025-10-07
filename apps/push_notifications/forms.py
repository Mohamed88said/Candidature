from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    Device, NotificationTemplate, NotificationPreference,
    NotificationCampaign, PushNotification
)

class DeviceForm(forms.ModelForm):
    """Formulaire pour enregistrer un appareil"""
    class Meta:
        model = Device
        fields = [
            'device_id', 'device_type', 'device_name', 'push_token'
        ]
        widgets = {
            'device_id': forms.TextInput(attrs={'class': 'form-control'}),
            'device_type': forms.Select(attrs={'class': 'form-select'}),
            'device_name': forms.TextInput(attrs={'class': 'form-control'}),
            'push_token': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_device_id(self):
        device_id = self.cleaned_data.get('device_id')
        if not device_id:
            raise ValidationError('L\'ID de l\'appareil est requis.')
        return device_id
    
    def clean_push_token(self):
        push_token = self.cleaned_data.get('push_token')
        if not push_token:
            raise ValidationError('Le token de notification push est requis.')
        return push_token

class NotificationPreferenceForm(forms.ModelForm):
    """Formulaire pour les préférences de notifications"""
    class Meta:
        model = NotificationPreference
        fields = [
            'push_enabled', 'email_enabled', 'sms_enabled',
            'job_alerts', 'application_updates', 'messages',
            'profile_reminders', 'achievements', 'badges',
            'level_ups', 'referrals', 'system_notifications',
            'marketing', 'frequency', 'quiet_hours_start',
            'quiet_hours_end'
        ]
        widgets = {
            'push_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'job_alerts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'application_updates': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'messages': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'profile_reminders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'achievements': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'badges': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'level_ups': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'referrals': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'system_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'marketing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'quiet_hours_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'quiet_hours_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        quiet_hours_start = cleaned_data.get('quiet_hours_start')
        quiet_hours_end = cleaned_data.get('quiet_hours_end')
        
        if quiet_hours_start and quiet_hours_end:
            if quiet_hours_start == quiet_hours_end:
                raise ValidationError('Les heures de début et de fin ne peuvent pas être identiques.')
        
        return cleaned_data

class NotificationTemplateForm(forms.ModelForm):
    """Formulaire pour créer/modifier un modèle de notification"""
    class Meta:
        model = NotificationTemplate
        fields = [
            'name', 'notification_type', 'title', 'body',
            'icon', 'image_url', 'action_url', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'notification_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fas fa-bell'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control'}),
            'action_url': forms.URLInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError('Le titre est requis.')
        if len(title) > 200:
            raise ValidationError('Le titre ne peut pas dépasser 200 caractères.')
        return title
    
    def clean_body(self):
        body = self.cleaned_data.get('body')
        if not body:
            raise ValidationError('Le corps du message est requis.')
        return body

class NotificationCampaignForm(forms.ModelForm):
    """Formulaire pour créer/modifier une campagne de notification"""
    class Meta:
        model = NotificationCampaign
        fields = [
            'name', 'campaign_type', 'template', 'target_filters',
            'scheduled_at', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'campaign_type': forms.Select(attrs={'class': 'form-select'}),
            'template': forms.Select(attrs={'class': 'form-select'}),
            'target_filters': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '{"user_type": "candidate", "location": "Paris"}'}),
            'scheduled_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError('Le nom de la campagne est requis.')
        return name
    
    def clean_target_filters(self):
        target_filters = self.cleaned_data.get('target_filters')
        if target_filters:
            try:
                import json
                json.loads(target_filters)
            except json.JSONDecodeError:
                raise ValidationError('Le format des filtres de ciblage n\'est pas valide JSON.')
        return target_filters
    
    def clean_scheduled_at(self):
        scheduled_at = self.cleaned_data.get('scheduled_at')
        if scheduled_at and scheduled_at < timezone.now():
            raise ValidationError('La date de planification ne peut pas être dans le passé.')
        return scheduled_at

class NotificationSearchForm(forms.Form):
    """Formulaire de recherche de notifications"""
    search_query = forms.CharField(
        max_length=255,
        required=False,
        label='Rechercher',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre, contenu...'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + PushNotification.STATUS_CHOICES,
        required=False,
        label='Statut',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    start_date = forms.DateField(
        required=False,
        label='Date de début',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    end_date = forms.DateField(
        required=False,
        label='Date de fin',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError('La date de début ne peut pas être postérieure à la date de fin.')
        
        return cleaned_data

class DeviceSearchForm(forms.Form):
    """Formulaire de recherche d'appareils"""
    search_query = forms.CharField(
        max_length=255,
        required=False,
        label='Rechercher',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom, ID...'})
    )
    
    device_type = forms.ChoiceField(
        choices=[('', 'Tous les types')] + Device.DEVICE_TYPE_CHOICES,
        required=False,
        label='Type d\'appareil',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_active = forms.ChoiceField(
        choices=[('', 'Tous'), ('true', 'Actif'), ('false', 'Inactif')],
        required=False,
        label='Statut',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class CampaignSearchForm(forms.Form):
    """Formulaire de recherche de campagnes"""
    search_query = forms.CharField(
        max_length=255,
        required=False,
        label='Rechercher',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la campagne...'})
    )
    
    campaign_type = forms.ChoiceField(
        choices=[('', 'Tous les types')] + NotificationCampaign.CAMPAIGN_TYPE_CHOICES,
        required=False,
        label='Type de campagne',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_sent = forms.ChoiceField(
        choices=[('', 'Toutes'), ('true', 'Envoyées'), ('false', 'Non envoyées')],
        required=False,
        label='Statut d\'envoi',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_active = forms.ChoiceField(
        choices=[('', 'Toutes'), ('true', 'Actives'), ('false', 'Inactives')],
        required=False,
        label='Statut',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class TemplateSearchForm(forms.Form):
    """Formulaire de recherche de modèles"""
    search_query = forms.CharField(
        max_length=255,
        required=False,
        label='Rechercher',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du modèle...'})
    )
    
    notification_type = forms.ChoiceField(
        choices=[('', 'Tous les types')] + NotificationTemplate.NOTIFICATION_TYPE_CHOICES,
        required=False,
        label='Type de notification',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_active = forms.ChoiceField(
        choices=[('', 'Tous'), ('true', 'Actifs'), ('false', 'Inactifs')],
        required=False,
        label='Statut',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class BulkNotificationActionForm(forms.Form):
    """Formulaire pour les actions groupées sur les notifications"""
    action_choices = [
        ('mark_read', 'Marquer comme lues'),
        ('mark_unread', 'Marquer comme non lues'),
        ('delete', 'Supprimer'),
    ]
    
    action = forms.ChoiceField(
        choices=action_choices,
        label='Action groupée',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    notification_ids = forms.CharField(
        widget=forms.HiddenInput,
        label='IDs des notifications sélectionnées'
    )
    
    def clean_notification_ids(self):
        notification_ids = self.cleaned_data.get('notification_ids')
        if not notification_ids:
            raise ValidationError('Aucune notification sélectionnée.')
        
        try:
            ids = [int(id.strip()) for id in notification_ids.split(',') if id.strip()]
            if not ids:
                raise ValidationError('Aucune notification valide sélectionnée.')
            return ids
        except ValueError:
            raise ValidationError('Format d\'IDs invalide.')

class NotificationTestForm(forms.Form):
    """Formulaire pour tester une notification"""
    title = forms.CharField(
        max_length=200,
        label='Titre',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    body = forms.CharField(
        label='Corps du message',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )
    
    icon = forms.CharField(
        max_length=100,
        required=False,
        label='Icône',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fas fa-bell'})
    )
    
    image_url = forms.URLField(
        required=False,
        label='URL de l\'image',
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    
    action_url = forms.URLField(
        required=False,
        label='URL d\'action',
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    
    notification_type = forms.ChoiceField(
        choices=NotificationTemplate.NOTIFICATION_TYPE_CHOICES,
        label='Type de notification',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError('Le titre est requis.')
        return title
    
    def clean_body(self):
        body = self.cleaned_data.get('body')
        if not body:
            raise ValidationError('Le corps du message est requis.')
        return body
