from datetime import date, timedelta
from django.db.models import Q
from .models import CandidateProfile, Experience


def calculate_candidate_experience(candidate, target_position=None):
    """Calcule l'expérience d'un candidat de manière intelligente"""
    experiences = candidate.experiences.all().order_by('start_date')
    
    if not experiences:
        return {
            'total_years': 0,
            'relevant_years': 0,
            'periods': [],
            'relevant_periods': []
        }
    
    # Convertir en périodes
    all_periods = []
    relevant_periods = []
    
    for exp in experiences:
        end_date = exp.end_date if exp.end_date else date.today()
        period = {
            'start': exp.start_date,
            'end': end_date,
            'experience': exp
        }
        all_periods.append(period)
        
        # Vérifier la pertinence si un poste cible est fourni
        if target_position and is_relevant_experience(exp, target_position):
            relevant_periods.append(period)
    
    # Calculer les années sans chevauchement
    total_years = calculate_non_overlapping_years(all_periods)
    relevant_years = calculate_non_overlapping_years(relevant_periods) if target_position else 0
    
    return {
        'total_years': total_years,
        'relevant_years': relevant_years,
        'periods': all_periods,
        'relevant_periods': relevant_periods
    }


def calculate_non_overlapping_years(periods):
    """Calcule les années d'expérience sans compter les chevauchements"""
    if not periods:
        return 0
    
    # Trier par date de début
    sorted_periods = sorted(periods, key=lambda x: x['start'])
    
    # Fusionner les périodes qui se chevauchent
    merged_periods = []
    current_period = sorted_periods[0]
    
    for period in sorted_periods[1:]:
        if period['start'] <= current_period['end']:
            # Chevauchement détecté, fusionner
            current_period['end'] = max(current_period['end'], period['end'])
        else:
            # Pas de chevauchement, ajouter la période actuelle et commencer une nouvelle
            merged_periods.append(current_period)
            current_period = period
    
    # Ajouter la dernière période
    merged_periods.append(current_period)
    
    # Calculer le total en années
    total_days = 0
    for period in merged_periods:
        days = (period['end'] - period['start']).days
        total_days += days
    
    return round(total_days / 365.25, 1)


def is_relevant_experience(experience, target_position):
    """Détermine si une expérience est pertinente pour un poste cible"""
    # Mots-clés du poste de l'expérience
    exp_words = set(experience.position.lower().split())
    
    # Mots-clés du poste cible
    target_words = set(target_position.lower().split())
    
    # Mots-clés des technologies utilisées
    tech_words = set()
    if experience.technologies_used:
        tech_words = set(experience.technologies_used.lower().split())
    
    # Mots-clés de l'industrie
    industry_words = set()
    if experience.industry:
        industry_words = set(experience.industry.lower().split())
    
    # Calculer les correspondances
    position_matches = len(exp_words.intersection(target_words))
    tech_matches = len(tech_words.intersection(target_words))
    industry_matches = len(industry_words.intersection(target_words))
    
    # Critères de pertinence
    # Au moins 1 mot-clé en commun dans le titre OU
    # Au moins 2 mots-clés techniques en commun OU
    # Même industrie + au moins 1 mot-clé
    is_relevant = (
        position_matches >= 1 or
        tech_matches >= 2 or
        (industry_matches >= 1 and position_matches >= 1)
    )
    
    return is_relevant


def calculate_candidate_score(candidate, job=None):
    """Calcule un score de compatibilité pour un candidat"""
    score = 0
    max_score = 100
    
    # Score de base sur la completion du profil (30 points)
    profile_score = (candidate.profile_completion / 100) * 30
    score += profile_score
    
    # Score d'expérience (25 points)
    if job:
        exp_data = calculate_candidate_experience(candidate, job.title)
        relevant_years = exp_data['relevant_years']
        
        # Calculer le score basé sur l'expérience pertinente
        if relevant_years >= 5:
            exp_score = 25
        elif relevant_years >= 2:
            exp_score = 20
        elif relevant_years >= 1:
            exp_score = 15
        else:
            exp_score = candidate.years_of_experience * 2.5  # Expérience générale
        
        score += min(exp_score, 25)
    else:
        # Score basé sur l'expérience totale
        exp_score = min(candidate.years_of_experience * 2.5, 25)
        score += exp_score
    
    # Score de formation (20 points)
    education_count = candidate.educations.count()
    education_score = min(education_count * 5, 20)
    score += education_score
    
    # Score de compétences (15 points)
    skills_count = candidate.skills.count()
    skills_score = min(skills_count * 1.5, 15)
    score += skills_score
    
    # Score de documents (10 points)
    doc_score = 0
    if candidate.cv_file:
        doc_score += 5
    if candidate.cover_letter:
        doc_score += 3
    if candidate.certifications.exists():
        doc_score += 2
    score += min(doc_score, 10)
    
    return min(round(score, 1), max_score)


def get_matching_jobs(candidate, limit=10):
    """Trouve les offres correspondant au profil du candidat"""
    from apps.jobs.models import Job
    
    # Récupérer les compétences du candidat
    candidate_skills = set(
        skill.name.lower() for skill in candidate.skills.all()
    )
    
    # Récupérer les mots-clés de l'expérience
    experience_keywords = set()
    for exp in candidate.experiences.all():
        experience_keywords.update(exp.position.lower().split())
        if exp.technologies_used:
            experience_keywords.update(exp.technologies_used.lower().split())
    
    # Rechercher les offres correspondantes
    matching_jobs = []
    jobs = Job.objects.filter(status='published')
    
    for job in jobs:
        score = 0
        
        # Score basé sur les compétences requises
        job_skills = set()
        for skill in job.required_skills.all():
            job_skills.add(skill.skill_name.lower())
        
        skill_matches = len(candidate_skills.intersection(job_skills))
        if job_skills:
            skill_score = (skill_matches / len(job_skills)) * 40
        else:
            skill_score = 0
        
        # Score basé sur l'expérience
        job_keywords = set(job.title.lower().split())
        job_keywords.update(job.description.lower().split()[:50])  # Limiter pour performance
        
        exp_matches = len(experience_keywords.intersection(job_keywords))
        exp_score = min(exp_matches * 5, 30)
        
        # Score basé sur la localisation
        location_score = 0
        if candidate.city and job.city:
            if candidate.city.lower() == job.city.lower():
                location_score = 20
        elif job.remote_work:
            location_score = 15
        elif candidate.willing_to_relocate:
            location_score = 10
        
        # Score basé sur le niveau d'expérience
        level_score = 0
        if job.experience_level == 'entry' and candidate.years_of_experience <= 2:
            level_score = 10
        elif job.experience_level == 'junior' and 2 <= candidate.years_of_experience <= 5:
            level_score = 10
        elif job.experience_level == 'mid' and 5 <= candidate.years_of_experience <= 8:
            level_score = 10
        elif job.experience_level == 'senior' and candidate.years_of_experience >= 8:
            level_score = 10
        
        total_score = skill_score + exp_score + location_score + level_score
        
        if total_score >= 30:  # Seuil minimum
            matching_jobs.append({
                'job': job,
                'score': round(total_score, 1),
                'skill_matches': skill_matches,
                'exp_matches': exp_matches
            })
    
    # Trier par score décroissant
    matching_jobs.sort(key=lambda x: x['score'], reverse=True)
    
    return matching_jobs[:limit]