from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import (
    Badge, UserBadge, Level, UserLevel, Achievement, UserAchievement,
    Streak, Leaderboard, LeaderboardEntry, Reward, UserReward,
    GamificationEvent
)
from .services import GamificationService
from .forms import RewardClaimForm

@login_required
def gamification_dashboard(request):
    """Dashboard principal de la gamification"""
    try:
        user = request.user
        
        # Niveau actuel
        user_level = user.level
        if not user_level:
            # Créer le niveau initial
            first_level = Level.objects.filter(is_active=True).order_by('level_number').first()
            if first_level:
                user_level = UserLevel.objects.create(
                    user=user,
                    current_level=first_level,
                    total_points=0
                )
        
        # Badges récents
        recent_badges = UserBadge.objects.filter(user=user).order_by('-earned_at')[:5]
        
        # Réussites en cours
        active_achievements = UserAchievement.objects.filter(
            user=user,
            is_completed=False
        ).select_related('achievement')[:5]
        
        # Séries
        streaks = Streak.objects.filter(user=user).order_by('-current_streak')[:3]
        
        # Événements récents
        recent_events = GamificationEvent.objects.filter(user=user).order_by('-created_at')[:10]
        
        # Classements
        leaderboards = Leaderboard.objects.filter(is_active=True)[:3]
        leaderboard_entries = {}
        for leaderboard in leaderboards:
            entry = LeaderboardEntry.objects.filter(
                leaderboard=leaderboard,
                user=user
            ).first()
            if entry:
                leaderboard_entries[leaderboard.id] = entry
        
        # Statistiques
        stats = {
            'total_points': user_level.total_points if user_level else 0,
            'badges_count': user.badges.count(),
            'achievements_count': user.achievements.filter(is_completed=True).count(),
            'current_streak': streaks.first().current_streak if streaks.exists() else 0,
            'rank_in_points': _get_user_rank(user, 'points'),
            'rank_in_badges': _get_user_rank(user, 'badges'),
        }
        
        context = {
            'user_level': user_level,
            'recent_badges': recent_badges,
            'active_achievements': active_achievements,
            'streaks': streaks,
            'recent_events': recent_events,
            'leaderboards': leaderboards,
            'leaderboard_entries': leaderboard_entries,
            'stats': stats,
        }
        
        return render(request, 'gamification/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du dashboard: {e}")
        return redirect('home')

@login_required
def badges_list(request):
    """Liste des badges"""
    try:
        badges = Badge.objects.filter(is_active=True).order_by('badge_type', 'points')
        user_badges = UserBadge.objects.filter(user=request.user).values_list('badge_id', flat=True)
        
        # Statistiques des badges
        total_badges = badges.count()
        earned_badges = len(user_badges)
        completion_rate = (earned_badges / total_badges * 100) if total_badges > 0 else 0
        
        # Badges par type
        badges_by_type = {}
        for badge in badges:
            badge_type = badge.get_badge_type_display()
            if badge_type not in badges_by_type:
                badges_by_type[badge_type] = []
            badges_by_type[badge_type].append(badge)
        
        context = {
            'badges': badges,
            'user_badges': user_badges,
            'total_badges': total_badges,
            'earned_badges': earned_badges,
            'completion_rate': completion_rate,
            'badges_by_type': badges_by_type,
        }
        
        return render(request, 'gamification/badges_list.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des badges: {e}")
        return redirect('gamification:dashboard')

@login_required
def badge_detail(request, badge_id):
    """Détail d'un badge"""
    try:
        badge = get_object_or_404(Badge, id=badge_id)
        user_badge = UserBadge.objects.filter(user=request.user, badge=badge).first()
        
        # Badges similaires
        similar_badges = Badge.objects.filter(
            badge_type=badge.badge_type,
            is_active=True
        ).exclude(id=badge.id)[:3]
        
        context = {
            'badge': badge,
            'user_badge': user_badge,
            'similar_badges': similar_badges,
        }
        
        return render(request, 'gamification/badge_detail.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du badge: {e}")
        return redirect('gamification:badges_list')

@login_required
def achievements_list(request):
    """Liste des réussites"""
    try:
        achievements = Achievement.objects.filter(is_active=True).order_by('achievement_type', 'points')
        user_achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement')
        
        # Créer un dictionnaire pour les réussites de l'utilisateur
        user_achievements_dict = {ua.achievement_id: ua for ua in user_achievements}
        
        # Statistiques des réussites
        total_achievements = achievements.count()
        completed_achievements = len([ua for ua in user_achievements if ua.is_completed])
        completion_rate = (completed_achievements / total_achievements * 100) if total_achievements > 0 else 0
        
        # Réussites par type
        achievements_by_type = {}
        for achievement in achievements:
            achievement_type = achievement.get_achievement_type_display()
            if achievement_type not in achievements_by_type:
                achievements_by_type[achievement_type] = []
            achievements_by_type[achievement_type].append(achievement)
        
        context = {
            'achievements': achievements,
            'user_achievements_dict': user_achievements_dict,
            'total_achievements': total_achievements,
            'completed_achievements': completed_achievements,
            'completion_rate': completion_rate,
            'achievements_by_type': achievements_by_type,
        }
        
        return render(request, 'gamification/achievements_list.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des réussites: {e}")
        return redirect('gamification:dashboard')

@login_required
def achievement_detail(request, achievement_id):
    """Détail d'une réussite"""
    try:
        achievement = get_object_or_404(Achievement, id=achievement_id)
        user_achievement = UserAchievement.objects.filter(
            user=request.user,
            achievement=achievement
        ).first()
        
        # Réussites similaires
        similar_achievements = Achievement.objects.filter(
            achievement_type=achievement.achievement_type,
            is_active=True
        ).exclude(id=achievement.id)[:3]
        
        context = {
            'achievement': achievement,
            'user_achievement': user_achievement,
            'similar_achievements': similar_achievements,
        }
        
        return render(request, 'gamification/achievement_detail.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement de la réussite: {e}")
        return redirect('gamification:achievements_list')

@login_required
def leaderboards_list(request):
    """Liste des classements"""
    try:
        leaderboards = Leaderboard.objects.filter(is_active=True).order_by('leaderboard_type', 'period')
        
        # Récupérer les entrées pour chaque classement
        leaderboard_data = []
        for leaderboard in leaderboards:
            entries = LeaderboardEntry.objects.filter(
                leaderboard=leaderboard
            ).select_related('user').order_by('rank')[:10]
            
            user_entry = LeaderboardEntry.objects.filter(
                leaderboard=leaderboard,
                user=request.user
            ).first()
            
            leaderboard_data.append({
                'leaderboard': leaderboard,
                'entries': entries,
                'user_entry': user_entry,
            })
        
        context = {
            'leaderboard_data': leaderboard_data,
        }
        
        return render(request, 'gamification/leaderboards_list.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des classements: {e}")
        return redirect('gamification:dashboard')

@login_required
def leaderboard_detail(request, leaderboard_id):
    """Détail d'un classement"""
    try:
        leaderboard = get_object_or_404(Leaderboard, id=leaderboard_id)
        
        # Entrées du classement
        entries = LeaderboardEntry.objects.filter(
            leaderboard=leaderboard
        ).select_related('user').order_by('rank')
        
        # Pagination
        paginator = Paginator(entries, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Position de l'utilisateur
        user_entry = LeaderboardEntry.objects.filter(
            leaderboard=leaderboard,
            user=request.user
        ).first()
        
        context = {
            'leaderboard': leaderboard,
            'page_obj': page_obj,
            'user_entry': user_entry,
        }
        
        return render(request, 'gamification/leaderboard_detail.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du classement: {e}")
        return redirect('gamification:leaderboards_list')

@login_required
def rewards_list(request):
    """Liste des récompenses"""
    try:
        rewards = Reward.objects.filter(is_active=True).order_by('cost')
        user_rewards = UserReward.objects.filter(user=request.user).values_list('reward_id', flat=True)
        
        # Récompenses disponibles
        user_level = request.user.level
        available_rewards = []
        if user_level:
            available_rewards = rewards.filter(cost__lte=user_level.total_points)
        
        context = {
            'rewards': rewards,
            'user_rewards': user_rewards,
            'available_rewards': available_rewards,
            'user_points': user_level.total_points if user_level else 0,
        }
        
        return render(request, 'gamification/rewards_list.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des récompenses: {e}")
        return redirect('gamification:dashboard')

@login_required
def claim_reward(request, reward_id):
    """Réclamer une récompense"""
    try:
        reward = get_object_or_404(Reward, id=reward_id)
        
        if request.method == 'POST':
            form = RewardClaimForm(request.POST)
            if form.is_valid():
                # Vérifier si l'utilisateur a déjà réclamé cette récompense
                if UserReward.objects.filter(user=request.user, reward=reward).exists():
                    messages.error(request, 'Vous avez déjà réclamé cette récompense.')
                    return redirect('gamification:rewards_list')
                
                # Vérifier si l'utilisateur a assez de points
                user_level = request.user.level
                if not user_level or user_level.total_points < reward.cost:
                    messages.error(request, 'Vous n\'avez pas assez de points pour réclamer cette récompense.')
                    return redirect('gamification:rewards_list')
                
                # Réclamer la récompense
                from .services import RewardService
                reward_service = RewardService()
                success = reward_service.claim_reward(request.user, reward)
                
                if success:
                    messages.success(request, f'Récompense "{reward.name}" réclamée avec succès!')
                else:
                    messages.error(request, 'Erreur lors de la réclamation de la récompense.')
                
                return redirect('gamification:rewards_list')
        else:
            form = RewardClaimForm()
        
        context = {
            'reward': reward,
            'form': form,
        }
        
        return render(request, 'gamification/claim_reward.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la réclamation de la récompense: {e}")
        return redirect('gamification:rewards_list')

@login_required
def my_rewards(request):
    """Mes récompenses"""
    try:
        user_rewards = UserReward.objects.filter(user=request.user).select_related('reward').order_by('-claimed_at')
        
        context = {
            'user_rewards': user_rewards,
        }
        
        return render(request, 'gamification/my_rewards.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement de vos récompenses: {e}")
        return redirect('gamification:dashboard')

@login_required
def events_list(request):
    """Liste des événements de gamification"""
    try:
        events = GamificationEvent.objects.filter(user=request.user).order_by('-created_at')
        
        # Pagination
        paginator = Paginator(events, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
        }
        
        return render(request, 'gamification/events_list.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des événements: {e}")
        return redirect('gamification:dashboard')

@login_required
@require_http_methods(["GET"])
def user_stats_api(request):
    """API pour les statistiques de l'utilisateur"""
    try:
        user = request.user
        user_level = user.level
        
        stats = {
            'total_points': user_level.total_points if user_level else 0,
            'current_level': user_level.current_level.level_number if user_level else 1,
            'level_name': user_level.current_level.name if user_level else 'Débutant',
            'level_progress': user_level.level_progress if user_level else 0,
            'points_to_next_level': user_level.points_to_next_level if user_level else 0,
            'badges_count': user.badges.count(),
            'achievements_count': user.achievements.filter(is_completed=True).count(),
            'current_streak': _get_current_streak(user),
            'rank_in_points': _get_user_rank(user, 'points'),
            'rank_in_badges': _get_user_rank(user, 'badges'),
        }
        
        return JsonResponse(stats)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def trigger_action_api(request):
    """API pour déclencher une action de gamification"""
    try:
        data = json.loads(request.body)
        action_type = data.get('action_type')
        action_data = data.get('action_data', {})
        
        if not action_type:
            return JsonResponse({'error': 'action_type requis'}, status=400)
        
        # Déclencher l'action
        gamification_service = GamificationService()
        results = gamification_service.process_user_action(
            user=request.user,
            action_type=action_type,
            action_data=action_data
        )
        
        return JsonResponse(results)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def _get_user_rank(user, leaderboard_type):
    """Récupère le rang de l'utilisateur dans un classement"""
    try:
        leaderboard = Leaderboard.objects.filter(
            leaderboard_type=leaderboard_type,
            period='all_time',
            is_active=True
        ).first()
        
        if leaderboard:
            entry = LeaderboardEntry.objects.filter(
                leaderboard=leaderboard,
                user=user
            ).first()
            
            if entry:
                return entry.rank
        
        return None
        
    except Exception:
        return None

def _get_current_streak(user):
    """Récupère la série actuelle de l'utilisateur"""
    try:
        streak = Streak.objects.filter(
            user=user,
            streak_type='daily_login'
        ).first()
        
        return streak.current_streak if streak else 0
        
    except Exception:
        return 0