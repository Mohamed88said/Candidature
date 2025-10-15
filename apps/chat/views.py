from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Max
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import json

from .models import (
    ChatRoom, Message, ChatParticipant, ChatNotification, 
    ChatSettings, ChatBlock, ChatReport
)
from .forms import (
    ChatRoomForm, MessageForm, ChatSettingsForm, ChatReportForm,
    ChatSearchForm, QuickMessageForm, ChatInviteForm
)
from apps.jobs.models import Job
from apps.applications.models import Application
from apps.accounts.models import CandidateProfile


@login_required
def chat_dashboard(request):
    """Dashboard principal du chat"""
    try:
        # Récupérer les salles de chat de l'utilisateur
        user_rooms = ChatRoom.objects.filter(
            Q(candidate=request.user) | Q(recruiter=request.user),
            is_active=True
        ).order_by('-last_message_at', '-created_at')
        
        # Statistiques
        total_rooms = user_rooms.count()
        unread_messages = sum(room.candidate_notifications if request.user == room.candidate else room.recruiter_notifications 
                             for room in user_rooms)
        
        # Salles récentes
        recent_rooms = user_rooms[:10]
        
        # Messages récents
        recent_messages = Message.objects.filter(
            room__in=user_rooms
        ).order_by('-created_at')[:5]
        
        context = {
            'user_rooms': recent_rooms,
            'recent_messages': recent_messages,
            'total_rooms': total_rooms,
            'unread_messages': unread_messages,
        }
        
        return render(request, 'chat/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du dashboard: {e}")
        return redirect('home')


@login_required
def chat_rooms_list(request):
    """Liste de toutes les salles de chat"""
    try:
        # Récupérer les salles de chat de l'utilisateur
        user_rooms = ChatRoom.objects.filter(
            Q(candidate=request.user) | Q(recruiter=request.user),
            is_active=True
        ).order_by('-last_message_at', '-created_at')
        
        # Filtres
        search_query = request.GET.get('search', '')
        room_type = request.GET.get('room_type', '')
        
        if search_query:
            user_rooms = user_rooms.filter(
                Q(title__icontains=search_query) |
                Q(candidate__first_name__icontains=search_query) |
                Q(candidate__last_name__icontains=search_query) |
                Q(recruiter__first_name__icontains=search_query) |
                Q(recruiter__last_name__icontains=search_query) |
                Q(job__title__icontains=search_query)
            )
        
        if room_type:
            user_rooms = user_rooms.filter(room_type=room_type)
        
        # Pagination
        paginator = Paginator(user_rooms, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'search_query': search_query,
            'room_type': room_type,
            'total_rooms': user_rooms.count(),
        }
        
        return render(request, 'chat/rooms_list.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des conversations: {e}")
        return redirect('chat:dashboard')


@login_required
def chat_room_detail(request, room_id):
    """Détail d'une salle de chat"""
    try:
        room = get_object_or_404(ChatRoom, id=room_id)
        
        # Vérifier que l'utilisateur fait partie de la conversation
        if request.user not in [room.candidate, room.recruiter]:
            messages.error(request, 'Accès non autorisé.')
            return redirect('chat:dashboard')
        
        # Marquer les messages comme lus
        room.mark_as_read(request.user)
        
        # Récupérer les messages
        messages_list = room.messages.filter(is_deleted=False).order_by('created_at')
        
        # Pagination des messages
        paginator = Paginator(messages_list, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Formulaire de message
        if request.method == 'POST':
            form = MessageForm(request.POST, request.FILES)
            if form.is_valid():
                message = form.save(commit=False)
                message.room = room
                message.sender = request.user
                message.save()
                
                # Mettre à jour les statistiques de la salle
                room.message_count += 1
                room.last_message_at = timezone.now()
                room.last_message_by = request.user
                room.add_notification(request.user)
                room.save()
                
                # Créer une notification pour l'autre utilisateur
                other_user = room.get_other_participant(request.user)
                ChatNotification.objects.create(
                    user=other_user,
                    room=room,
                    message=message,
                    notification_type='new_message',
                    title='Nouveau message',
                    content=f"Nouveau message de {request.user.full_name}"
                )
                
                return redirect('chat:room_detail', room_id=room_id)
        else:
            form = MessageForm()
        
        context = {
            'room': room,
            'page_obj': page_obj,
            'form': form,
            'other_user': room.get_other_participant(request.user),
        }
        
        return render(request, 'chat/room_detail.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement de la conversation: {e}")
        return redirect('chat:dashboard')


@login_required
def create_chat_room(request):
    """Créer une nouvelle salle de chat"""
    try:
        if request.method == 'POST':
            form = ChatRoomForm(request.POST)
            if form.is_valid():
                room = form.save(commit=False)
                room.candidate = request.user
                room.save()
                
                # Créer les participants
                ChatParticipant.objects.create(user=room.candidate, room=room)
                ChatParticipant.objects.create(user=room.recruiter, room=room)
                
                messages.success(request, 'Conversation créée avec succès.')
                return redirect('chat:room_detail', room_id=room.id)
        else:
            form = ChatRoomForm()
        
        # Récupérer les utilisateurs disponibles
        from django.contrib.auth import get_user_model
        User = get_user_model()
        available_users = User.objects.exclude(id=request.user.id)
        
        context = {
            'form': form,
            'available_users': available_users,
        }
        
        return render(request, 'chat/create_room.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la création de la conversation: {e}")
        return redirect('chat:dashboard')


@login_required
def start_chat_with_user(request, user_id):
    """Démarrer une conversation avec un utilisateur spécifique"""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other_user = get_object_or_404(User, id=user_id)
        
        # Vérifier qu'il n'y a pas déjà une conversation
        existing_room = ChatRoom.objects.filter(
            Q(candidate=request.user, recruiter=other_user) |
            Q(candidate=other_user, recruiter=request.user),
            is_active=True
        ).first()
        
        if existing_room:
            return redirect('chat:room_detail', room_id=existing_room.id)
        
        # Créer une nouvelle conversation
        room = ChatRoom.objects.create(
            candidate=request.user if request.user.user_type == 'candidate' else other_user,
            recruiter=other_user if request.user.user_type == 'candidate' else request.user,
            room_type='general'
        )
        
        # Créer les participants
        ChatParticipant.objects.create(user=room.candidate, room=room)
        ChatParticipant.objects.create(user=room.recruiter, room=room)
        
        messages.success(request, f'Conversation démarrée avec {other_user.full_name}.')
        return redirect('chat:room_detail', room_id=room.id)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du démarrage de la conversation: {e}")
        return redirect('chat:dashboard')


@login_required
def start_chat_from_application(request, application_id):
    """Démarrer une conversation à partir d'une candidature"""
    try:
        application = get_object_or_404(Application, id=application_id)
        
        # Vérifier les permissions
        if request.user not in [application.candidate.user, application.job.created_by]:
            messages.error(request, 'Accès non autorisé.')
            return redirect('applications:application_detail', pk=application_id)
        
        # Vérifier qu'il n'y a pas déjà une conversation
        existing_room = ChatRoom.objects.filter(
            application=application,
            is_active=True
        ).first()
        
        if existing_room:
            return redirect('chat:room_detail', room_id=existing_room.id)
        
        # Créer une nouvelle conversation
        room = ChatRoom.objects.create(
            candidate=application.candidate.user,
            recruiter=application.job.created_by,
            job=application.job,
            application=application,
            room_type='application',
            title=f"Candidature: {application.job.title}"
        )
        
        # Créer les participants
        ChatParticipant.objects.create(user=room.candidate, room=room)
        ChatParticipant.objects.create(user=room.recruiter, room=room)
        
        messages.success(request, 'Conversation démarrée pour cette candidature.')
        return redirect('chat:room_detail', room_id=room.id)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du démarrage de la conversation: {e}")
        return redirect('applications:application_detail', pk=application_id)


@login_required
@require_http_methods(["POST"])
def send_message(request, room_id):
    """Envoyer un message via AJAX"""
    try:
        room = get_object_or_404(ChatRoom, id=room_id)
        
        # Vérifier que l'utilisateur fait partie de la conversation
        if request.user not in [room.candidate, room.recruiter]:
            return JsonResponse({'error': 'Accès non autorisé'}, status=403)
        
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.room = room
            message.sender = request.user
            message.save()
            
            # Mettre à jour les statistiques de la salle
            room.message_count += 1
            room.last_message_at = timezone.now()
            room.last_message_by = request.user
            room.add_notification(request.user)
            room.save()
            
            # Retourner le message créé
            message_data = {
                'id': str(message.id),
                'content': message.content,
                'message_type': message.message_type,
                'sender': {
                    'id': message.sender.id,
                    'name': message.sender.full_name,
                    'avatar': message.sender.candidate_profile.profile_picture.url if hasattr(message.sender, 'candidate_profile') and message.sender.candidate_profile.profile_picture else None
                },
                'created_at': message.created_at.isoformat(),
                'is_own': message.sender == request.user
            }
            
            return JsonResponse({'success': True, 'message': message_data})
        else:
            return JsonResponse({'error': 'Données invalides', 'errors': form.errors}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def chat_settings(request):
    """Paramètres du chat"""
    try:
        settings, created = ChatSettings.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            form = ChatSettingsForm(request.POST, instance=settings)
            if form.is_valid():
                form.save()
                messages.success(request, 'Paramètres sauvegardés avec succès.')
                return redirect('chat:settings')
        else:
            form = ChatSettingsForm(instance=settings)
        
        context = {
            'form': form,
            'settings': settings,
        }
        
        return render(request, 'chat/settings.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des paramètres: {e}")
        return redirect('chat:dashboard')


@login_required
@require_http_methods(["POST"])
def add_reaction(request, message_id):
    """Ajouter une réaction à un message"""
    try:
        message = get_object_or_404(Message, id=message_id)
        
        # Vérifier que l'utilisateur fait partie de la conversation
        if request.user not in [message.room.candidate, message.room.recruiter]:
            return JsonResponse({'error': 'Accès non autorisé'}, status=403)
        
        emoji = request.POST.get('emoji')
        if not emoji:
            return JsonResponse({'error': 'Emoji requis'}, status=400)
        
        message.add_reaction(request.user, emoji)
        
        return JsonResponse({
            'success': True,
            'reaction_count': message.get_reaction_count(emoji),
            'has_user_reacted': message.has_user_reacted(request.user, emoji)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def remove_reaction(request, message_id):
    """Supprimer une réaction d'un message"""
    try:
        message = get_object_or_404(Message, id=message_id)
        
        # Vérifier que l'utilisateur fait partie de la conversation
        if request.user not in [message.room.candidate, message.room.recruiter]:
            return JsonResponse({'error': 'Accès non autorisé'}, status=403)
        
        emoji = request.POST.get('emoji')
        if not emoji:
            return JsonResponse({'error': 'Emoji requis'}, status=400)
        
        message.remove_reaction(request.user, emoji)
        
        return JsonResponse({
            'success': True,
            'reaction_count': message.get_reaction_count(emoji),
            'has_user_reacted': message.has_user_reacted(request.user, emoji)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def report_user(request, user_id):
    """Signaler un utilisateur"""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        reported_user = get_object_or_404(User, id=user_id)
        
        if request.method == 'POST':
            form = ChatReportForm(request.POST)
            if form.is_valid():
                report = form.save(commit=False)
                report.reporter = request.user
                report.reported_user = reported_user
                report.save()
                
                messages.success(request, 'Signalement envoyé avec succès.')
                return redirect('chat:dashboard')
        else:
            form = ChatReportForm()
        
        context = {
            'form': form,
            'reported_user': reported_user,
        }
        
        return render(request, 'chat/report_user.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du signalement: {e}")
        return redirect('chat:dashboard')


@login_required
def block_user(request, user_id):
    """Bloquer un utilisateur"""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user_to_block = get_object_or_404(User, id=user_id)
        
        if request.method == 'POST':
            ChatBlock.objects.get_or_create(
                blocker=request.user,
                blocked=user_to_block
            )
            
            messages.success(request, f'{user_to_block.full_name} a été bloqué.')
            return redirect('chat:dashboard')
        
        return render(request, 'chat/block_user.html', {
            'user_to_block': user_to_block
        })
        
    except Exception as e:
        messages.error(request, f"Erreur lors du blocage: {e}")
        return redirect('chat:dashboard')


@login_required
def unblock_user(request, user_id):
    """Débloquer un utilisateur"""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user_to_unblock = get_object_or_404(User, id=user_id)
        
        ChatBlock.objects.filter(
            blocker=request.user,
            blocked=user_to_unblock
        ).delete()
        
        messages.success(request, f'{user_to_unblock.full_name} a été débloqué.')
        return redirect('chat:dashboard')
        
    except Exception as e:
        messages.error(request, f"Erreur lors du déblocage: {e}")
        return redirect('chat:dashboard')


@login_required
def chat_notifications(request):
    """Liste des notifications de chat"""
    try:
        notifications = ChatNotification.objects.filter(
            user=request.user
        ).order_by('-created_at')
        
        # Marquer toutes les notifications comme lues
        notifications.update(is_read=True, read_at=timezone.now())
        
        # Pagination
        paginator = Paginator(notifications, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
        }
        
        return render(request, 'chat/notifications.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des notifications: {e}")
        return redirect('chat:dashboard')


@login_required
def chat_analytics(request):
    """Analytics du chat (admin)"""
    if not request.user.is_staff:
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        # Statistiques générales
        total_rooms = ChatRoom.objects.count()
        total_messages = Message.objects.count()
        active_rooms = ChatRoom.objects.filter(is_active=True).count()
        
        # Statistiques par type de salle
        room_type_stats = ChatRoom.objects.values('room_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Messages par jour (7 derniers jours)
        from datetime import timedelta
        seven_days_ago = timezone.now() - timedelta(days=7)
        daily_messages = Message.objects.filter(
            created_at__gte=seven_days_ago
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        context = {
            'total_rooms': total_rooms,
            'total_messages': total_messages,
            'active_rooms': active_rooms,
            'room_type_stats': room_type_stats,
            'daily_messages': list(daily_messages),
        }
        
        return render(request, 'chat/analytics.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des analytics: {e}")
        return redirect('chat:dashboard')



