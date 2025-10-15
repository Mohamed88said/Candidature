import math
import re
from typing import Dict, List, Tuple, Optional
from django.db.models import Q, F
from django.utils import timezone
from apps.accounts.models import CandidateProfile, Skill, Experience
from apps.jobs.models import Job, JobSkill
from apps.matching.models import (
    MatchingAlgorithm, JobMatch, CandidatePreference, 
    SkillSimilarity, IndustrySimilarity
)
try:
    from geopy.geocoders import Nominatim
    from geopy.distance import geodesic
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
import logging

logger = logging.getLogger(__name__)


class IntelligentMatchingService:
    """Service de matching intelligent entre candidats et offres"""
    
    def __init__(self, algorithm: Optional[MatchingAlgorithm] = None):
        self.algorithm = algorithm or MatchingAlgorithm.objects.filter(is_active=True).first()
        if not self.algorithm:
            self.algorithm = self._create_default_algorithm()
    
    def _create_default_algorithm(self) -> MatchingAlgorithm:
        """Crée un algorithme par défaut"""
        return MatchingAlgorithm.objects.create(
            name="Algorithme par défaut",
            description="Algorithme de matching intelligent par défaut",
            is_active=True
        )
    
    def find_matches_for_candidate(self, candidate: CandidateProfile, limit: int = 20) -> List[JobMatch]:
        """Trouve les meilleures offres pour un candidat"""
        try:
            # Récupérer les offres actives
            active_jobs = Job.objects.filter(
                status='published',
                application_deadline__gt=timezone.now()
            ).exclude(
                applications__candidate=candidate  # Exclure les offres déjà postulées
            )
            
            matches = []
            for job in active_jobs:
                match_score = self._calculate_match_score(candidate, job)
                
                if match_score['overall_score'] >= self.algorithm.minimum_match_score:
                    match = self._create_job_match(candidate, job, match_score)
                    matches.append(match)
            
            # Trier par score décroissant et limiter
            matches.sort(key=lambda x: x.overall_score, reverse=True)
            return matches[:limit]
            
        except Exception as e:
            logger.error(f"Erreur lors du matching pour {candidate.user.full_name}: {e}")
            return []
    
    def find_matches_for_job(self, job: Job, limit: int = 20) -> List[JobMatch]:
        """Trouve les meilleurs candidats pour une offre"""
        try:
            # Récupérer les candidats actifs
            active_candidates = CandidateProfile.objects.filter(
                is_active=True,
                user__is_active=True
            ).exclude(
                applications__job=job  # Exclure les candidats ayant déjà postulé
            )
            
            matches = []
            for candidate in active_candidates:
                match_score = self._calculate_match_score(candidate, job)
                
                if match_score['overall_score'] >= self.algorithm.minimum_match_score:
                    match = self._create_job_match(candidate, job, match_score)
                    matches.append(match)
            
            # Trier par score décroissant et limiter
            matches.sort(key=lambda x: x.overall_score, reverse=True)
            return matches[:limit]
            
        except Exception as e:
            logger.error(f"Erreur lors du matching pour {job.title}: {e}")
            return []
    
    def _calculate_match_score(self, candidate: CandidateProfile, job: Job) -> Dict:
        """Calcule le score de matching détaillé"""
        scores = {
            'experience_score': self._calculate_experience_score(candidate, job),
            'skills_score': self._calculate_skills_score(candidate, job),
            'location_score': self._calculate_location_score(candidate, job),
            'salary_score': self._calculate_salary_score(candidate, job),
            'education_score': self._calculate_education_score(candidate, job),
            'culture_score': self._calculate_culture_score(candidate, job),
        }
        
        # Calcul du score global pondéré
        overall_score = (
            scores['experience_score'] * self.algorithm.experience_weight +
            scores['skills_score'] * self.algorithm.skills_weight +
            scores['location_score'] * self.algorithm.location_weight +
            scores['salary_score'] * self.algorithm.salary_weight +
            scores['education_score'] * self.algorithm.education_weight +
            scores['culture_score'] * self.algorithm.company_culture_weight
        ) / 100
        
        scores['overall_score'] = int(overall_score)
        
        # Ajouter l'analyse détaillée
        scores.update(self._generate_detailed_analysis(candidate, job, scores))
        
        return scores
    
    def _calculate_experience_score(self, candidate: CandidateProfile, job: Job) -> int:
        """Calcule le score d'expérience (0-100)"""
        try:
            # Analyser le niveau d'expérience requis
            required_level = job.experience_level
            candidate_years = candidate.years_of_experience
            
            # Mapping des niveaux d'expérience
            level_mapping = {
                'entry': (0, 2),
                'junior': (2, 5),
                'mid': (5, 8),
                'senior': (8, 12),
                'lead': (12, 15),
                'principal': (15, 20),
                'director': (20, 25),
                'executive': (25, 30),
                'c_level': (30, 50),
            }
            
            if required_level in level_mapping:
                min_req, max_req = level_mapping[required_level]
                
                if candidate_years >= min_req and candidate_years <= max_req:
                    return 100  # Expérience parfaite
                elif candidate_years < min_req:
                    # Moins d'expérience - pénalité progressive
                    deficit = min_req - candidate_years
                    penalty = min(deficit * 15, 50)  # Max 50 points de pénalité
                    return max(100 - penalty, 20)
                else:
                    # Plus d'expérience - léger bonus
                    excess = candidate_years - max_req
                    if excess <= 5:
                        return 95  # Légèrement surqualifié
                    else:
                        return 85  # Très surqualifié
            
            return 50  # Score par défaut
            
        except Exception as e:
            logger.error(f"Erreur calcul expérience: {e}")
            return 50
    
    def _calculate_skills_score(self, candidate: CandidateProfile, job: Job) -> int:
        """Calcule le score de compétences (0-100)"""
        try:
            # Récupérer les compétences requises
            required_skills = job.required_skills.all()
            if not required_skills:
                return 50  # Pas de compétences spécifiées
            
            # Récupérer les compétences du candidat
            candidate_skills = {skill.name.lower(): skill.level for skill in candidate.skills.all()}
            
            total_score = 0
            matching_skills = []
            missing_skills = []
            
            for req_skill in required_skills:
                skill_name = req_skill.skill_name.lower()
                skill_level = req_skill.level
                
                # Vérifier si le candidat a cette compétence
                if skill_name in candidate_skills:
                    candidate_level = candidate_skills[skill_name]
                    
                    # Calculer le score basé sur le niveau
                    level_scores = {
                        'required': 100,
                        'preferred': 80,
                        'nice_to_have': 60,
                    }
                    
                    base_score = level_scores.get(skill_level, 70)
                    
                    # Ajuster selon le niveau du candidat
                    candidate_level_scores = {
                        'beginner': 0.3,
                        'basic': 0.5,
                        'intermediate': 0.7,
                        'advanced': 0.9,
                        'expert': 1.0,
                        'master': 1.0,
                    }
                    
                    level_multiplier = candidate_level_scores.get(candidate_level, 0.5)
                    final_score = base_score * level_multiplier
                    
                    total_score += final_score
                    matching_skills.append({
                        'skill': req_skill.skill_name,
                        'required_level': skill_level,
                        'candidate_level': candidate_level,
                        'score': final_score
                    })
                else:
                    # Vérifier les compétences similaires
                    similar_skill = self._find_similar_skill(skill_name, candidate_skills)
                    if similar_skill:
                        total_score += 30  # Score réduit pour compétence similaire
                        matching_skills.append({
                            'skill': req_skill.skill_name,
                            'similar_skill': similar_skill,
                            'score': 30
                        })
                    else:
                        missing_skills.append(req_skill.skill_name)
                        # Pénalité pour compétence manquante
                        penalty = 20 if skill_level == 'required' else 10
                        total_score -= penalty
            
            # Normaliser le score (0-100)
            max_possible_score = len(required_skills) * 100
            if max_possible_score > 0:
                normalized_score = max(0, min(100, (total_score / max_possible_score) * 100))
            else:
                normalized_score = 50
            
            return int(normalized_score)
            
        except Exception as e:
            logger.error(f"Erreur calcul compétences: {e}")
            return 50
    
    def _calculate_location_score(self, candidate: CandidateProfile, job: Job) -> int:
        """Calcule le score de localisation (0-100)"""
        try:
            # Si télétravail autorisé
            if job.remote_work and candidate.candidate_profile.willing_to_relocate:
                return 100
            
            # Calculer la distance
            candidate_location = f"{candidate.city}, {candidate.country}"
            job_location = f"{job.city}, {job.country}"
            
            distance_km = self._calculate_distance(candidate_location, job_location)
            
            if distance_km is None:
                return 50  # Impossible de calculer la distance
            
            # Score basé sur la distance
            max_distance = self.algorithm.location_radius_km
            
            if distance_km <= 10:
                return 100  # Très proche
            elif distance_km <= 25:
                return 90   # Proche
            elif distance_km <= max_distance:
                # Score dégressif
                score = 100 - ((distance_km - 25) / (max_distance - 25)) * 40
                return max(int(score), 30)
            else:
                # Trop loin
                return 10
            
        except Exception as e:
            logger.error(f"Erreur calcul localisation: {e}")
            return 50
    
    def _calculate_salary_score(self, candidate: CandidateProfile, job: Job) -> int:
        """Calcule le score salarial (0-100)"""
        try:
            candidate_expected = candidate.expected_salary
            job_min = job.salary_min
            job_max = job.salary_max
            
            if not candidate_expected or not job_min:
                return 50  # Pas d'information salariale
            
            # Si le candidat accepte le salaire minimum
            if candidate_expected <= job_min:
                return 100
            
            # Si le candidat accepte dans la fourchette
            if job_max and candidate_expected <= job_max:
                return 90
            
            # Si le candidat demande plus que le maximum
            if job_max:
                excess = candidate_expected - job_max
                excess_percentage = (excess / job_max) * 100
                
                if excess_percentage <= 10:
                    return 80
                elif excess_percentage <= 20:
                    return 60
                elif excess_percentage <= 30:
                    return 40
                else:
                    return 20
            else:
                # Pas de salaire maximum spécifié
                excess = candidate_expected - job_min
                excess_percentage = (excess / job_min) * 100
                
                if excess_percentage <= 20:
                    return 80
                elif excess_percentage <= 40:
                    return 60
                else:
                    return 40
            
        except Exception as e:
            logger.error(f"Erreur calcul salaire: {e}")
            return 50
    
    def _calculate_education_score(self, candidate: CandidateProfile, job: Job) -> int:
        """Calcule le score d'éducation (0-100)"""
        try:
            # Pour l'instant, score basique basé sur le niveau d'éducation le plus élevé
            educations = candidate.educations.all()
            if not educations:
                return 30  # Pas d'éducation spécifiée
            
            # Trouver le niveau d'éducation le plus élevé
            highest_level = None
            level_hierarchy = {
                'high_school': 1,
                'certificate': 2,
                'diploma': 3,
                'bachelor': 4,
                'master': 5,
                'phd': 6,
            }
            
            for education in educations:
                level = education.degree_level
                if highest_level is None or level_hierarchy.get(level, 0) > level_hierarchy.get(highest_level, 0):
                    highest_level = level
            
            # Score basé sur le niveau (simplifié)
            education_scores = {
                'high_school': 40,
                'certificate': 50,
                'diploma': 60,
                'bachelor': 80,
                'master': 95,
                'phd': 100,
            }
            
            return education_scores.get(highest_level, 50)
            
        except Exception as e:
            logger.error(f"Erreur calcul éducation: {e}")
            return 50
    
    def _calculate_culture_score(self, candidate: CandidateProfile, job: Job) -> int:
        """Calcule le score de culture d'entreprise (0-100)"""
        try:
            # Score basé sur la taille d'entreprise et les préférences
            job_company_size = job.company_size
            candidate_experiences = candidate.experiences.all()
            
            if not candidate_experiences:
                return 50  # Pas d'expérience pour évaluer les préférences
            
            # Analyser les expériences passées pour déterminer les préférences
            company_sizes = [exp.company_size for exp in candidate_experiences if exp.company_size]
            
            if not company_sizes:
                return 50
            
            # Score basé sur la cohérence avec l'expérience passée
            if job_company_size in company_sizes:
                return 90  # Expérience similaire
            else:
                # Vérifier la proximité de taille
                size_hierarchy = ['startup', 'small', 'medium', 'large', 'enterprise']
                job_size_index = size_hierarchy.index(job_company_size) if job_company_size in size_hierarchy else 2
                
                for exp_size in company_sizes:
                    exp_size_index = size_hierarchy.index(exp_size) if exp_size in size_hierarchy else 2
                    if abs(job_size_index - exp_size_index) <= 1:
                        return 70  # Taille similaire
                
                return 40  # Taille très différente
            
        except Exception as e:
            logger.error(f"Erreur calcul culture: {e}")
            return 50
    
    def _generate_detailed_analysis(self, candidate: CandidateProfile, job: Job, scores: Dict) -> Dict:
        """Génère une analyse détaillée du matching"""
        analysis = {
            'matching_skills': [],
            'missing_skills': [],
            'strengths': [],
            'concerns': [],
            'recommendations': ''
        }
        
        # Analyser les compétences
        required_skills = job.required_skills.all()
        candidate_skills = {skill.name.lower(): skill for skill in candidate.skills.all()}
        
        for req_skill in required_skills:
            skill_name = req_skill.skill_name.lower()
            if skill_name in candidate_skills:
                candidate_skill = candidate_skills[skill_name]
                analysis['matching_skills'].append({
                    'skill': req_skill.skill_name,
                    'level': candidate_skill.level,
                    'years': candidate_skill.years_of_experience
                })
            else:
                analysis['missing_skills'].append(req_skill.skill_name)
        
        # Identifier les forces
        if scores['experience_score'] >= 80:
            analysis['strengths'].append("Expérience parfaitement adaptée au poste")
        if scores['skills_score'] >= 80:
            analysis['strengths'].append("Compétences techniques excellentes")
        if scores['location_score'] >= 90:
            analysis['strengths'].append("Localisation idéale")
        
        # Identifier les préoccupations
        if scores['experience_score'] < 60:
            analysis['concerns'].append("Expérience insuffisante pour le poste")
        if scores['skills_score'] < 60:
            analysis['concerns'].append("Compétences techniques à développer")
        if scores['location_score'] < 50:
            analysis['concerns'].append("Localisation éloignée")
        
        # Générer des recommandations
        recommendations = []
        if analysis['missing_skills']:
            recommendations.append(f"Développer les compétences: {', '.join(analysis['missing_skills'][:3])}")
        if scores['salary_score'] < 70:
            recommendations.append("Considérer une négociation salariale")
        if scores['location_score'] < 70:
            recommendations.append("Envisager le télétravail ou la relocalisation")
        
        analysis['recommendations'] = '; '.join(recommendations) if recommendations else "Profil très adapté au poste"
        
        return analysis
    
    def _find_similar_skill(self, skill_name: str, candidate_skills: Dict) -> Optional[str]:
        """Trouve une compétence similaire chez le candidat"""
        try:
            # Recherche dans la base de similarité
            similarities = SkillSimilarity.objects.filter(
                Q(skill1__iexact=skill_name) | Q(skill2__iexact=skill_name)
            ).filter(similarity_score__gte=0.7)
            
            for similarity in similarities:
                similar_skill = similarity.skill2 if similarity.skill1.lower() == skill_name.lower() else similarity.skill1
                if similar_skill.lower() in candidate_skills:
                    return similar_skill
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur recherche compétence similaire: {e}")
            return None
    
    def _calculate_distance(self, location1: str, location2: str) -> Optional[float]:
        """Calcule la distance entre deux localisations"""
        if not GEOPY_AVAILABLE:
            logger.warning("Geopy non disponible, distance non calculée")
            return None
            
        try:
            geolocator = Nominatim(user_agent="recruitment_platform")
            
            # Géocoder les adresses
            loc1 = geolocator.geocode(location1)
            loc2 = geolocator.geocode(location2)
            
            if loc1 and loc2:
                # Calculer la distance en kilomètres
                distance = geodesic(
                    (loc1.latitude, loc1.longitude),
                    (loc2.latitude, loc2.longitude)
                ).kilometers
                return distance
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur calcul distance: {e}")
            return None
    
    def _create_job_match(self, candidate: CandidateProfile, job: Job, match_data: Dict) -> JobMatch:
        """Crée un objet JobMatch"""
        match, created = JobMatch.objects.get_or_create(
            candidate=candidate,
            job=job,
            algorithm=self.algorithm,
            defaults={
                'overall_score': match_data['overall_score'],
                'experience_score': match_data['experience_score'],
                'skills_score': match_data['skills_score'],
                'location_score': match_data['location_score'],
                'salary_score': match_data['salary_score'],
                'education_score': match_data['education_score'],
                'culture_score': match_data['culture_score'],
                'matching_skills': match_data.get('matching_skills', []),
                'missing_skills': match_data.get('missing_skills', []),
                'strengths': match_data.get('strengths', []),
                'concerns': match_data.get('concerns', []),
                'recommendations': match_data.get('recommendations', ''),
            }
        )
        
        if not created:
            # Mettre à jour le match existant
            for field, value in match_data.items():
                if hasattr(match, field):
                    setattr(match, field, value)
            match.save()
        
        return match


class MatchingAnalytics:
    """Service d'analytics pour le système de matching"""
    
    @staticmethod
    def get_matching_statistics() -> Dict:
        """Retourne les statistiques de matching"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Statistiques générales
        total_matches = JobMatch.objects.count()
        high_matches = JobMatch.objects.filter(overall_score__gte=80).count()
        applications_from_matches = JobMatch.objects.filter(
            candidate_interest='applied'
        ).count()
        
        # Statistiques récentes (30 derniers jours)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_matches = JobMatch.objects.filter(created_at__gte=thirty_days_ago).count()
        
        # Taux de conversion
        conversion_rate = (applications_from_matches / total_matches * 100) if total_matches > 0 else 0
        
        return {
            'total_matches': total_matches,
            'high_matches': high_matches,
            'recent_matches': recent_matches,
            'applications_from_matches': applications_from_matches,
            'conversion_rate': round(conversion_rate, 2),
            'high_match_percentage': round((high_matches / total_matches * 100) if total_matches > 0 else 0, 2)
        }
    
    @staticmethod
    def get_top_matching_skills() -> List[Dict]:
        """Retourne les compétences les plus matchées"""
        from django.db.models import Count
        
        # Compétences les plus fréquentes dans les matches
        skill_stats = JobMatch.objects.values('matching_skills').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return list(skill_stats)
    
    @staticmethod
    def get_matching_trends() -> Dict:
        """Retourne les tendances de matching"""
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        
        # Tendance sur 7 jours
        seven_days_ago = timezone.now() - timedelta(days=7)
        daily_matches = JobMatch.objects.filter(
            created_at__gte=seven_days_ago
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        return {
            'daily_matches': list(daily_matches),
            'trend_direction': 'up' if len(daily_matches) > 0 else 'stable'
        }
