from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from typing import Dict, List, Optional, Any
import logging

from .models import (
    Badge, UserBadge, Level, UserLevel, Achievement, UserAchievement,
    Streak, Leaderboard, LeaderboardEntry, Reward, UserReward,
    GamificationEvent
)

User = get_user_model()
logger = logging.getLogger(__name__)

class GamificationService:
    """Service principal pour la gamification"""
    
    def __init__(self):
        self.points_service = PointsService()
        self.badge_service = BadgeService()
        self.level_service = LevelService()
        self.achievement_service = AchievementService()
        self.streak_service = StreakService()
        self.leaderboard_service = LeaderboardService()
        self.reward_service = RewardService()

    def process_user_action(self, user: User, action_type: str, action_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Traite une action utilisateur et déclenche les événements de gamification"""
        if action_data is None:
            action_data = {}
        
        results = {
            'points_earned': 0,
            'badges_earned': [],
            'level_up': False,
            'achievements_completed': [],
            'streaks_updated': [],
            'events_created': []
        }
        
        try:
            with transaction.atomic():
                # Calculer les points
                points = self.points_service.calculate_points(user, action_type, action_data)
                if points > 0:
                    self.points_service.award_points(user, points, action_type, action_data)
                    results['points_earned'] = points
                
                # Vérifier les badges
                badges = self.badge_service.check_badges(user, action_type, action_data)
                for badge in badges:
                    self.badge_service.award_badge(user, badge)
                    results['badges_earned'].append(badge)
                
                # Vérifier les niveaux
                level_up = self.level_service.check_level_up(user)
                if level_up:
                    results['level_up'] = True
                
                # Vérifier les réussites
                achievements = self.achievement_service.check_achievements(user, action_type, action_data)
                for achievement in achievements:
                    self.achievement_service.complete_achievement(user, achievement)
                    results['achievements_completed'].append(achievement)
                
                # Mettre à jour les séries
                streaks = self.streak_service.update_streaks(user, action_type, action_data)
                results['streaks_updated'] = streaks
                
                # Créer des événements
                events = self._create_events(user, action_type, action_data, results)
                results['events_created'] = events
                
                # Mettre à jour les classements
                self.leaderboard_service.update_leaderboards(user)
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'action {action_type} pour {user.username}: {e}")
            raise
        
        return results

    def _create_events(self, user: User, action_type: str, action_data: Dict, results: Dict) -> List[GamificationEvent]:
        """Crée les événements de gamification"""
        events = []
        
        # Événement pour les points
        if results['points_earned'] > 0:
            event = GamificationEvent.objects.create(
                user=user,
                event_type='points_earned',
                title=f"+{results['points_earned']} points",
                description=f"Vous avez gagné {results['points_earned']} points pour {action_type}",
                points_earned=results['points_earned'],
                metadata={'action_type': action_type, 'action_data': action_data}
            )
            events.append(event)
        
        # Événements pour les badges
        for badge in results['badges_earned']:
            event = GamificationEvent.objects.create(
                user=user,
                event_type='badge_earned',
                title=f"Badge obtenu: {badge.name}",
                description=badge.description,
                points_earned=badge.points,
                metadata={'badge_id': badge.id, 'badge_type': badge.badge_type}
            )
            events.append(event)
        
        # Événement pour la montée de niveau
        if results['level_up']:
            user_level = user.level
            event = GamificationEvent.objects.create(
                user=user,
                event_type='level_up',
                title=f"Niveau {user_level.current_level.level_number} atteint!",
                description=f"Félicitations! Vous avez atteint le niveau {user_level.current_level.level_number}",
                points_earned=0,
                metadata={'new_level': user_level.current_level.level_number}
            )
            events.append(event)
        
        # Événements pour les réussites
        for achievement in results['achievements_completed']:
            event = GamificationEvent.objects.create(
                user=user,
                event_type='achievement_completed',
                title=f"Réussite: {achievement.name}",
                description=achievement.description,
                points_earned=achievement.points,
                metadata={'achievement_id': achievement.id}
            )
            events.append(event)
        
        return events

class PointsService:
    """Service pour la gestion des points"""
    
    POINTS_CONFIG = {
        'profile_completion': {
            'basic_info': 10,
            'photo': 5,
            'summary': 15,
            'skills': 5,
            'experience': 10,
            'education': 10,
            'contact_info': 5,
        },
        'job_application': {
            'first_application': 50,
            'application': 10,
            'application_with_cover_letter': 15,
            'application_with_video': 25,
        },
        'cv_creation': {
            'create_cv': 30,
            'complete_cv': 20,
            'export_cv': 5,
        },
        'skill_verification': {
            'verify_skill': 20,
            'complete_test': 30,
        },
        'referral': {
            'invite_friend': 25,
            'friend_signs_up': 50,
            'friend_completes_profile': 25,
        },
        'social': {
            'like_job': 2,
            'share_job': 5,
            'follow_company': 3,
            'write_review': 15,
        },
        'daily_login': 5,
        'weekly_login': 25,
        'monthly_login': 100,
    }
    
    def calculate_points(self, user: User, action_type: str, action_data: Dict[str, Any]) -> int:
        """Calcule les points pour une action"""
        points = 0
        
        if action_type in self.POINTS_CONFIG:
            config = self.POINTS_CONFIG[action_type]
            
            if isinstance(config, dict):
                # Points basés sur les données de l'action
                for key, value in action_data.items():
                    if key in config:
                        points += config[key]
            else:
                # Points fixes
                points = config
        
        return points
    
    def award_points(self, user: User, points: int, action_type: str, action_data: Dict[str, Any]):
        """Attribue des points à un utilisateur"""
        user_level, created = UserLevel.objects.get_or_create(user=user)
        
        if created:
            # Créer le niveau initial
            first_level = Level.objects.filter(is_active=True).order_by('level_number').first()
            if first_level:
                user_level.current_level = first_level
                user_level.save()
        
        user_level.total_points += points
        user_level.calculate_progress()
        user_level.save()
        
        logger.info(f"Points attribués: {user.username} +{points} points pour {action_type}")

class BadgeService:
    """Service pour la gestion des badges"""
    
    def check_badges(self, user: User, action_type: str, action_data: Dict[str, Any]) -> List[Badge]:
        """Vérifie si l'utilisateur mérite de nouveaux badges"""
        badges = []
        
        # Badges basés sur l'action
        if action_type == 'profile_completion':
            completion_rate = self._calculate_profile_completion(user)
            if completion_rate >= 100:
                badge = Badge.objects.filter(badge_type='profile_completion', name='Profil complet').first()
                if badge and not UserBadge.objects.filter(user=user, badge=badge).exists():
                    badges.append(badge)
        
        elif action_type == 'job_application':
            application_count = user.applications.count()
            if application_count == 1:
                badge = Badge.objects.filter(badge_type='job_application', name='Première candidature').first()
                if badge and not UserBadge.objects.filter(user=user, badge=badge).exists():
                    badges.append(badge)
            elif application_count == 10:
                badge = Badge.objects.filter(badge_type='job_application', name='Candidat actif').first()
                if badge and not UserBadge.objects.filter(user=user, badge=badge).exists():
                    badges.append(badge)
        
        elif action_type == 'cv_creation':
            cv_count = user.cvs.count()
            if cv_count == 1:
                badge = Badge.objects.filter(badge_type='cv_creation', name='Premier CV').first()
                if badge and not UserBadge.objects.filter(user=user, badge=badge).exists():
                    badges.append(badge)
        
        elif action_type == 'referral':
            referral_count = user.referrals.count()
            if referral_count == 1:
                badge = Badge.objects.filter(badge_type='referral', name='Premier parrainage').first()
                if badge and not UserBadge.objects.filter(user=user, badge=badge).exists():
                    badges.append(badge)
        
        return badges
    
    def award_badge(self, user: User, badge: Badge):
        """Attribue un badge à un utilisateur"""
        user_badge, created = UserBadge.objects.get_or_create(
            user=user,
            badge=badge
        )
        
        if created:
            # Attribuer les points du badge
            points_service = PointsService()
            points_service.award_points(user, badge.points, 'badge_earned', {'badge_id': badge.id})
            
            logger.info(f"Badge attribué: {user.username} a obtenu le badge {badge.name}")
    
    def _calculate_profile_completion(self, user: User) -> float:
        """Calcule le pourcentage de complétion du profil"""
        try:
            profile = user.candidate_profile
            total_fields = 10  # Nombre total de champs importants
            completed_fields = 0
            
            if profile.first_name:
                completed_fields += 1
            if profile.last_name:
                completed_fields += 1
            if profile.email:
                completed_fields += 1
            if profile.phone:
                completed_fields += 1
            if profile.location:
                completed_fields += 1
            if profile.summary:
                completed_fields += 1
            if profile.photo:
                completed_fields += 1
            if profile.skills.exists():
                completed_fields += 1
            if profile.experiences.exists():
                completed_fields += 1
            if profile.educations.exists():
                completed_fields += 1
            
            return (completed_fields / total_fields) * 100
        except:
            return 0

class LevelService:
    """Service pour la gestion des niveaux"""
    
    def check_level_up(self, user: User) -> bool:
        """Vérifie si l'utilisateur peut monter de niveau"""
        try:
            user_level = user.level
            if not user_level:
                return False
            
            # Trouver le prochain niveau
            next_level = Level.objects.filter(
                level_number__gt=user_level.current_level.level_number,
                is_active=True
            ).order_by('level_number').first()
            
            if next_level and user_level.total_points >= next_level.required_points:
                # Monter de niveau
                user_level.current_level = next_level
                user_level.last_level_up = timezone.now()
                user_level.calculate_progress()
                user_level.save()
                
                logger.info(f"Montée de niveau: {user.username} est maintenant niveau {next_level.level_number}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de niveau pour {user.username}: {e}")
            return False

class AchievementService:
    """Service pour la gestion des réussites"""
    
    def check_achievements(self, user: User, action_type: str, action_data: Dict[str, Any]) -> List[Achievement]:
        """Vérifie si l'utilisateur a terminé des réussites"""
        achievements = []
        
        # Vérifier les réussites basées sur l'action
        if action_type == 'job_application':
            application_count = user.applications.count()
            achievement = Achievement.objects.filter(
                achievement_type='job_application',
                condition__type='count',
                condition__target='job_applications',
                condition__value=application_count
            ).first()
            
            if achievement:
                user_achievement, created = UserAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement
                )
                if not user_achievement.is_completed:
                    user_achievement.is_completed = True
                    user_achievement.completed_at = timezone.now()
                    user_achievement.save()
                    achievements.append(achievement)
        
        return achievements
    
    def complete_achievement(self, user: User, achievement: Achievement):
        """Marque une réussite comme terminée"""
        user_achievement, created = UserAchievement.objects.get_or_create(
            user=user,
            achievement=achievement
        )
        
        if not user_achievement.is_completed:
            user_achievement.is_completed = True
            user_achievement.completed_at = timezone.now()
            user_achievement.save()
            
            # Attribuer les points
            points_service = PointsService()
            points_service.award_points(user, achievement.points, 'achievement_completed', {'achievement_id': achievement.id})
            
            logger.info(f"Réussite terminée: {user.username} a terminé {achievement.name}")

class StreakService:
    """Service pour la gestion des séries"""
    
    def update_streaks(self, user: User, action_type: str, action_data: Dict[str, Any]) -> List[Streak]:
        """Met à jour les séries d'activité"""
        updated_streaks = []
        
        if action_type == 'daily_login':
            streak, created = Streak.objects.get_or_create(
                user=user,
                streak_type='daily_login'
            )
            
            if self._is_new_day(streak.last_activity):
                streak.current_streak += 1
                if streak.current_streak > streak.longest_streak:
                    streak.longest_streak = streak.current_streak
            else:
                streak.current_streak = 1
            
            streak.last_activity = timezone.now()
            streak.save()
            updated_streaks.append(streak)
        
        return updated_streaks
    
    def _is_new_day(self, last_activity) -> bool:
        """Vérifie si c'est un nouveau jour depuis la dernière activité"""
        if not last_activity:
            return True
        
        now = timezone.now()
        return now.date() > last_activity.date()

class LeaderboardService:
    """Service pour la gestion des classements"""
    
    def update_leaderboards(self, user: User):
        """Met à jour les classements"""
        # Mettre à jour le classement des points
        self._update_points_leaderboard(user)
        
        # Mettre à jour le classement des badges
        self._update_badges_leaderboard(user)
        
        # Mettre à jour le classement des candidatures
        self._update_applications_leaderboard(user)
    
    def _update_points_leaderboard(self, user: User):
        """Met à jour le classement des points"""
        leaderboard = Leaderboard.objects.filter(
            leaderboard_type='points',
            period='all_time',
            is_active=True
        ).first()
        
        if leaderboard:
            user_level = user.level
            if user_level:
                entry, created = LeaderboardEntry.objects.get_or_create(
                    leaderboard=leaderboard,
                    user=user
                )
                entry.score = user_level.total_points
                entry.save()
                
                # Recalculer les rangs
                self._recalculate_ranks(leaderboard)
    
    def _update_badges_leaderboard(self, user: User):
        """Met à jour le classement des badges"""
        leaderboard = Leaderboard.objects.filter(
            leaderboard_type='badges',
            period='all_time',
            is_active=True
        ).first()
        
        if leaderboard:
            badge_count = user.badges.count()
            entry, created = LeaderboardEntry.objects.get_or_create(
                leaderboard=leaderboard,
                user=user
            )
            entry.score = badge_count
            entry.save()
            
            # Recalculer les rangs
            self._recalculate_ranks(leaderboard)
    
    def _update_applications_leaderboard(self, user: User):
        """Met à jour le classement des candidatures"""
        leaderboard = Leaderboard.objects.filter(
            leaderboard_type='applications',
            period='all_time',
            is_active=True
        ).first()
        
        if leaderboard:
            application_count = user.applications.count()
            entry, created = LeaderboardEntry.objects.get_or_create(
                leaderboard=leaderboard,
                user=user
            )
            entry.score = application_count
            entry.save()
            
            # Recalculer les rangs
            self._recalculate_ranks(leaderboard)
    
    def _recalculate_ranks(self, leaderboard: Leaderboard):
        """Recalcule les rangs d'un classement"""
        entries = LeaderboardEntry.objects.filter(leaderboard=leaderboard).order_by('-score')
        
        for rank, entry in enumerate(entries, 1):
            entry.rank = rank
            entry.save()

class RewardService:
    """Service pour la gestion des récompenses"""
    
    def get_available_rewards(self, user: User) -> List[Reward]:
        """Retourne les récompenses disponibles pour l'utilisateur"""
        user_level = user.level
        if not user_level:
            return []
        
        return Reward.objects.filter(
            is_active=True,
            cost__lte=user_level.total_points
        ).order_by('cost')
    
    def claim_reward(self, user: User, reward: Reward) -> bool:
        """Permet à l'utilisateur de réclamer une récompense"""
        user_level = user.level
        if not user_level or user_level.total_points < reward.cost:
            return False
        
        # Vérifier si l'utilisateur a déjà réclamé cette récompense
        if UserReward.objects.filter(user=user, reward=reward).exists():
            return False
        
        with transaction.atomic():
            # Créer l'enregistrement de récompense
            UserReward.objects.create(user=user, reward=reward)
            
            # Déduire les points
            user_level.total_points -= reward.cost
            user_level.save()
            
            logger.info(f"Récompense réclamée: {user.username} a réclamé {reward.name}")
            return True

