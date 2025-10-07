from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, F
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
import json
import uuid
from datetime import datetime, timedelta

from .models import (
    ReferralProgram, ReferralCode, Referral, ReferralReward,
    ReferralInvitation, ReferralLeaderboard, ReferralAnalytics
)
from .forms import (
    ReferralInvitationForm, BulkInvitationForm, ReferralCodeForm,
    ReferralProgramForm, ReferralRewardForm, ReferralSearchForm,
    ReferralSettingsForm, ReferralFeedbackForm, ReferralLeaderboardForm,
    ReferralAnalyticsForm
)


@login_required
def referrals_dashboard(request):
    """Dashboard principal du programme de recommandation"""
    try:
        # Programmes actifs
        active_programs = ReferralProgram.objects.filter(is_active=True)
        
        # Code de recommandation de l'utilisateur
        referral_code, created = ReferralCode.objects.get_or_create(
            user=request.user,
            program=active_programs.first() if active_programs.exists() else None
        )
        
        # Statistiques de l'utilisateur
        user_referrals = Referral.objects.filter(referrer=request.user)
        total_referrals = user_referrals.count()
        successful_referrals = user_referrals.filter(status='completed').count()
        pending_referrals = user_referrals.filter(status='pending').count()
        
        # Récompenses
        total_rewards = ReferralReward.objects.filter(user=request.user).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Invitations récentes
        recent_invitations = ReferralInvitation.objects.filter(
            referrer=request.user
        ).order_by('-created_at')[:5]
        
        # Classement
        leaderboard_position = ReferralLeaderboard.objects.filter(
            user=request.user
        ).order_by('-created_at').first()
        
        context = {
            'active_programs': active_programs,
            'referral_code': referral_code,
            'total_referrals': total_referrals,
            'successful_referrals': successful_referrals,
            'pending_referrals': pending_referrals,
            'total_rewards': total_rewards,
            'recent_invitations': recent_invitations,
            'leaderboard_position': leaderboard_position,
        }
        
        return render(request, 'referrals/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du dashboard: {e}")
        return redirect('home')


@login_required
def invite_friends(request):
    """Page pour inviter des amis"""
    try:
        if request.method == 'POST':
            form = ReferralInvitationForm(request.POST)
            if form.is_valid():
                # Créer l'invitation
                invitation = ReferralInvitation.objects.create(
                    referrer=request.user,
                    referral_code=request.user.referral_codes.first(),
                    email=form.cleaned_data['email'],
                    name=form.cleaned_data['name'],
                    message=form.cleaned_data['message'],
                    expires_at=timezone.now() + timedelta(days=7)
                )
                
                # Envoyer l'email si demandé
                if form.cleaned_data.get('send_email'):
                    send_referral_invitation_email(invitation)
                
                messages.success(request, 'Invitation envoyée avec succès !')
                return redirect('referrals:invite_friends')
        else:
            form = ReferralInvitationForm()
        
        # Invitations récentes
        recent_invitations = ReferralInvitation.objects.filter(
            referrer=request.user
        ).order_by('-created_at')[:10]
        
        context = {
            'form': form,
            'recent_invitations': recent_invitations,
        }
        
        return render(request, 'referrals/invite_friends.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de l'envoi de l'invitation: {e}")
        return redirect('referrals:dashboard')


@login_required
def bulk_invite(request):
    """Inviter plusieurs amis en masse"""
    try:
        if request.method == 'POST':
            form = BulkInvitationForm(request.POST)
            if form.is_valid():
                emails = form.cleaned_data['emails']
                message = form.cleaned_data['message']
                
                created_count = 0
                for email in emails:
                    invitation, created = ReferralInvitation.objects.get_or_create(
                        referrer=request.user,
                        referral_code=request.user.referral_codes.first(),
                        email=email,
                        defaults={
                            'message': message,
                            'expires_at': timezone.now() + timedelta(days=7)
                        }
                    )
                    if created:
                        created_count += 1
                        send_referral_invitation_email(invitation)
                
                messages.success(request, f'{created_count} invitations envoyées avec succès !')
                return redirect('referrals:invite_friends')
        else:
            form = BulkInvitationForm()
        
        context = {
            'form': form,
        }
        
        return render(request, 'referrals/bulk_invite.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de l'envoi en masse: {e}")
        return redirect('referrals:invite_friends')


@login_required
def my_referrals(request):
    """Liste des recommandations de l'utilisateur"""
    try:
        referrals = Referral.objects.filter(referrer=request.user).order_by('-created_at')
        
        # Filtres
        search_form = ReferralSearchForm(request.GET)
        if search_form.is_valid():
            search_query = search_form.cleaned_data.get('search_query')
            status = search_form.cleaned_data.get('status')
            date_from = search_form.cleaned_data.get('date_from')
            date_to = search_form.cleaned_data.get('date_to')
            
            if search_query:
                referrals = referrals.filter(
                    Q(referee__first_name__icontains=search_query) |
                    Q(referee__last_name__icontains=search_query) |
                    Q(referee__email__icontains=search_query)
                )
            
            if status:
                referrals = referrals.filter(status=status)
            
            if date_from:
                referrals = referrals.filter(created_at__date__gte=date_from)
            
            if date_to:
                referrals = referrals.filter(created_at__date__lte=date_to)
        
        # Pagination
        paginator = Paginator(referrals, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'search_form': search_form,
        }
        
        return render(request, 'referrals/my_referrals.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des recommandations: {e}")
        return redirect('referrals:dashboard')


@login_required
def my_rewards(request):
    """Liste des récompenses de l'utilisateur"""
    try:
        rewards = ReferralReward.objects.filter(user=request.user).order_by('-created_at')
        
        # Statistiques
        total_rewards = rewards.aggregate(total=Sum('amount'))['total'] or 0
        claimed_rewards = rewards.filter(is_claimed=True).aggregate(total=Sum('amount'))['total'] or 0
        pending_rewards = rewards.filter(is_claimed=False).aggregate(total=Sum('amount'))['total'] or 0
        
        # Pagination
        paginator = Paginator(rewards, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'total_rewards': total_rewards,
            'claimed_rewards': claimed_rewards,
            'pending_rewards': pending_rewards,
        }
        
        return render(request, 'referrals/my_rewards.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des récompenses: {e}")
        return redirect('referrals:dashboard')


@login_required
def leaderboard(request):
    """Classement des recommandations"""
    try:
        form = ReferralLeaderboardForm(request.GET)
        leaderboard_data = []
        
        if form.is_valid():
            period = form.cleaned_data.get('period', 'all_time')
            program = form.cleaned_data.get('program')
            
            # Filtrer par période
            if period == 'this_month':
                start_date = timezone.now().replace(day=1)
                end_date = timezone.now()
            elif period == 'last_month':
                last_month = timezone.now().replace(day=1) - timedelta(days=1)
                start_date = last_month.replace(day=1)
                end_date = last_month
            elif period == 'this_year':
                start_date = timezone.now().replace(month=1, day=1)
                end_date = timezone.now()
            elif period == 'last_year':
                last_year = timezone.now().year - 1
                start_date = timezone.now().replace(year=last_year, month=1, day=1)
                end_date = timezone.now().replace(year=last_year, month=12, day=31)
            else:
                start_date = None
                end_date = None
            
            # Récupérer les données du classement
            leaderboard_data = ReferralLeaderboard.objects.all()
            
            if start_date and end_date:
                leaderboard_data = leaderboard_data.filter(
                    period_start__gte=start_date,
                    period_end__lte=end_date
                )
            
            if program:
                leaderboard_data = leaderboard_data.filter(program=program)
            
            leaderboard_data = leaderboard_data.order_by('rank', '-total_referrals')[:50]
        
        context = {
            'form': form,
            'leaderboard_data': leaderboard_data,
        }
        
        return render(request, 'referrals/leaderboard.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du classement: {e}")
        return redirect('referrals:dashboard')


@login_required
def referral_settings(request):
    """Paramètres de recommandation de l'utilisateur"""
    try:
        if request.method == 'POST':
            form = ReferralSettingsForm(request.POST)
            if form.is_valid():
                # Sauvegarder les paramètres (vous devrez créer un modèle UserReferralSettings)
                messages.success(request, 'Paramètres mis à jour avec succès !')
                return redirect('referrals:referral_settings')
        else:
            form = ReferralSettingsForm()
        
        context = {
            'form': form,
        }
        
        return render(request, 'referrals/referral_settings.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des paramètres: {e}")
        return redirect('referrals:dashboard')


def referral_signup(request, referral_code):
    """Inscription avec un code de recommandation"""
    try:
        # Vérifier le code de recommandation
        try:
            referral_code_obj = ReferralCode.objects.get(code=referral_code)
        except ReferralCode.DoesNotExist:
            messages.error(request, 'Code de recommandation invalide.')
            return redirect('accounts:signup')
        
        # Vérifier si l'utilisateur est déjà connecté
        if request.user.is_authenticated:
            messages.info(request, 'Vous êtes déjà connecté.')
            return redirect('home')
        
        # Stocker le code de recommandation en session
        request.session['referral_code'] = referral_code
        
        # Rediriger vers l'inscription
        return redirect('accounts:signup')
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la validation du code: {e}")
        return redirect('accounts:signup')


@login_required
def claim_reward(request, reward_id):
    """Réclamer une récompense"""
    try:
        reward = get_object_or_404(ReferralReward, id=reward_id, user=request.user)
        
        if reward.is_claimed:
            messages.warning(request, 'Cette récompense a déjà été réclamée.')
            return redirect('referrals:my_rewards')
        
        # Réclamer la récompense
        reward.claim()
        
        messages.success(request, f'Récompense de {reward.amount} {reward.get_reward_type_display()} réclamée avec succès !')
        return redirect('referrals:my_rewards')
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la réclamation: {e}")
        return redirect('referrals:my_rewards')


@login_required
def referral_analytics(request):
    """Analytics des recommandations (admin)"""
    if not request.user.is_staff:
        messages.error(request, 'Accès non autorisé.')
        return redirect('referrals:dashboard')
    
    try:
        form = ReferralAnalyticsForm(request.GET)
        analytics_data = []
        
        if form.is_valid():
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')
            program = form.cleaned_data.get('program')
            
            # Récupérer les données d'analytics
            analytics_data = ReferralAnalytics.objects.all()
            
            if date_from:
                analytics_data = analytics_data.filter(date__gte=date_from)
            
            if date_to:
                analytics_data = analytics_data.filter(date__lte=date_to)
            
            if program:
                analytics_data = analytics_data.filter(program=program)
            
            analytics_data = analytics_data.order_by('-date')
        
        context = {
            'form': form,
            'analytics_data': analytics_data,
        }
        
        return render(request, 'referrals/analytics.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des analytics: {e}")
        return redirect('referrals:dashboard')


# API Views pour AJAX
@login_required
@require_http_methods(["POST"])
def send_invitation(request):
    """Envoyer une invitation via AJAX"""
    try:
        form = ReferralInvitationForm(request.POST)
        if form.is_valid():
            invitation = ReferralInvitation.objects.create(
                referrer=request.user,
                referral_code=request.user.referral_codes.first(),
                email=form.cleaned_data['email'],
                name=form.cleaned_data['name'],
                message=form.cleaned_data['message'],
                expires_at=timezone.now() + timedelta(days=7)
            )
            
            # Envoyer l'email
            send_referral_invitation_email(invitation)
            
            return JsonResponse({
                'success': True,
                'message': 'Invitation envoyée avec succès'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def track_invitation_click(request, invitation_id):
    """Tracker le clic sur une invitation"""
    try:
        invitation = get_object_or_404(ReferralInvitation, id=invitation_id)
        invitation.mark_as_clicked()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def track_invitation_open(request, invitation_id):
    """Tracker l'ouverture d'une invitation"""
    try:
        invitation = get_object_or_404(ReferralInvitation, id=invitation_id)
        invitation.mark_as_opened()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Fonctions utilitaires
def send_referral_invitation_email(invitation):
    """Envoyer un email d'invitation de recommandation"""
    try:
        subject = f"Invitation de {invitation.referrer.full_name}"
        
        message = f"""
        Bonjour,
        
        {invitation.referrer.full_name} vous invite à rejoindre notre plateforme de recrutement !
        
        {invitation.message if invitation.message else "Découvrez de nouvelles opportunités d'emploi et créez votre profil professionnel."}
        
        Cliquez sur le lien suivant pour vous inscrire :
        {settings.BASE_URL}/referrals/signup/{invitation.referral_code.code}/
        
        Cette invitation expire le {invitation.expires_at.strftime('%d/%m/%Y')}.
        
        Cordialement,
        L'équipe de {settings.SITE_NAME}
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [invitation.email],
            fail_silently=False,
        )
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")


def create_referral_on_signup(user, referral_code):
    """Créer une recommandation lors de l'inscription"""
    try:
        referral_code_obj = ReferralCode.objects.get(code=referral_code)
        
        # Créer la recommandation
        referral = Referral.objects.create(
            referrer=referral_code_obj.user,
            referee=user,
            program=referral_code_obj.program,
            referral_code=referral_code_obj,
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        # Marquer l'invitation comme inscrite
        ReferralInvitation.objects.filter(
            referral_code=referral_code_obj,
            email=user.email
        ).update(
            status='registered',
            registered_at=timezone.now()
        )
        
        # Mettre à jour les statistiques du code
        referral_code_obj.total_uses += 1
        referral_code_obj.last_used_at = timezone.now()
        referral_code_obj.save()
        
        return referral
        
    except Exception as e:
        print(f"Erreur lors de la création de la recommandation: {e}")
        return None