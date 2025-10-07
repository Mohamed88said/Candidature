from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML, Field
from .models import ChatRoom, Message, ChatSettings, ChatReport


class ChatRoomForm(forms.ModelForm):
    """Formulaire pour créer une salle de chat"""
    class Meta:
        model = ChatRoom
        fields = ['room_type', 'title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la conversation (optionnel)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description de la conversation (optionnel)'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop('candidate', None)
        self.recruiter = kwargs.pop('recruiter', None)
        self.job = kwargs.pop('job', None)
        self.application = kwargs.pop('application', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'room_type',
            'title',
            'description',
            Submit('submit', 'Créer la conversation', css_class='btn btn-primary')
        )

    def clean(self):
        cleaned_data = super().clean()
        
        # Vérifier que les participants sont différents
        if self.candidate and self.recruiter and self.candidate == self.recruiter:
            raise ValidationError("Un utilisateur ne peut pas créer une conversation avec lui-même.")
        
        return cleaned_data


class MessageForm(forms.ModelForm):
    """Formulaire pour envoyer un message"""
    class Meta:
        model = Message
        fields = ['content', 'message_type', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tapez votre message...',
                'id': 'messageInput'
            }),
            'message_type': forms.HiddenInput(),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,video/*,audio/*,.pdf,.doc,.docx,.txt'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False
        self.fields['attachment'].required = False

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        attachment = cleaned_data.get('attachment')
        
        # Vérifier qu'il y a au moins du contenu ou un fichier
        if not content and not attachment:
            raise ValidationError("Vous devez saisir un message ou joindre un fichier.")
        
        return cleaned_data


class ChatSettingsForm(forms.ModelForm):
    """Formulaire pour les paramètres de chat"""
    class Meta:
        model = ChatSettings
        fields = [
            'email_notifications', 'push_notifications', 'sound_notifications',
            'theme', 'font_size', 'show_typing_indicator', 'show_read_receipts',
            'auto_download_media', 'show_online_status', 'allow_direct_messages'
        ]
        widgets = {
            'theme': forms.Select(attrs={'class': 'form-select'}),
            'font_size': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5>Notifications</h5>'),
            Row(
                Column('email_notifications', css_class='form-group col-md-4 mb-0'),
                Column('push_notifications', css_class='form-group col-md-4 mb-0'),
                Column('sound_notifications', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h5 class="mt-4">Apparence</h5>'),
            Row(
                Column('theme', css_class='form-group col-md-6 mb-0'),
                Column('font_size', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h5 class="mt-4">Comportement</h5>'),
            Row(
                Column('show_typing_indicator', css_class='form-group col-md-4 mb-0'),
                Column('show_read_receipts', css_class='form-group col-md-4 mb-0'),
                Column('auto_download_media', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h5 class="mt-4">Confidentialité</h5>'),
            Row(
                Column('show_online_status', css_class='form-group col-md-6 mb-0'),
                Column('allow_direct_messages', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            
            Submit('submit', 'Sauvegarder les paramètres', css_class='btn btn-primary mt-4')
        )


class ChatReportForm(forms.ModelForm):
    """Formulaire pour signaler un utilisateur ou un message"""
    class Meta:
        model = ChatReport
        fields = ['report_type', 'description']
        widgets = {
            'report_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez le problème rencontré...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'report_type',
            'description',
            Submit('submit', 'Envoyer le signalement', css_class='btn btn-danger')
        )


class ChatSearchForm(forms.Form):
    """Formulaire de recherche dans les messages"""
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher dans les messages...'
        })
    )
    
    message_type = forms.ChoiceField(
        choices=[('', 'Tous les types')] + list(Message.MESSAGE_TYPES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    has_attachments = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('query', css_class='form-group col-md-6 mb-0'),
                Column('message_type', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('date_from', css_class='form-group col-md-4 mb-0'),
                Column('date_to', css_class='form-group col-md-4 mb-0'),
                Column('has_attachments', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Rechercher', css_class='btn btn-primary')
        )


class QuickMessageForm(forms.Form):
    """Formulaire pour un message rapide"""
    content = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tapez votre message...',
            'id': 'quickMessageInput'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            'content',
            Submit('submit', 'Envoyer', css_class='btn btn-primary btn-sm')
        )


class ChatInviteForm(forms.Form):
    """Formulaire pour inviter un utilisateur à une conversation"""
    user = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Sélectionner un utilisateur"
    )
    
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Message d\'invitation (optionnel)'
        })
    )

    def __init__(self, *args, **kwargs):
        self.room = kwargs.pop('room', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les utilisateurs qui ne sont pas déjà dans la conversation
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if self.room:
            existing_participants = [self.room.candidate, self.room.recruiter]
            self.fields['user'].queryset = User.objects.exclude(
                id__in=[u.id for u in existing_participants]
            )
        else:
            self.fields['user'].queryset = User.objects.all()
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'user',
            'message',
            Submit('submit', 'Inviter', css_class='btn btn-primary')
        )

