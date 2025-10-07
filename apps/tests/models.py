from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from cloudinary.models import CloudinaryField
import json

User = get_user_model()


class TestCategory(models.Model):
    """Catégorie de test (Technique, Comportemental, Logique, etc.)"""
    name = models.CharField(max_length=100, verbose_name='Nom')
    description = models.TextField(blank=True, verbose_name='Description')
    icon = models.CharField(max_length=50, default='fas fa-clipboard-check', verbose_name='Icône')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Couleur')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Catégorie de test'
        verbose_name_plural = 'Catégories de test'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Test(models.Model):
    """Test d'évaluation"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Débutant'),
        ('intermediate', 'Intermédiaire'),
        ('advanced', 'Avancé'),
        ('expert', 'Expert'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(verbose_name='Description')
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE, related_name='tests', verbose_name='Catégorie')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='intermediate', verbose_name='Difficulté')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Statut')
    
    # Configuration du test
    time_limit = models.PositiveIntegerField(help_text='Durée en minutes (0 = illimité)', default=0, verbose_name='Durée limite')
    max_attempts = models.PositiveIntegerField(default=3, verbose_name='Tentatives maximum')
    passing_score = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=70,
        verbose_name='Score de réussite (%)'
    )
    
    # Questions et réponses
    questions = models.JSONField(default=list, verbose_name='Questions')
    total_questions = models.PositiveIntegerField(default=0, verbose_name='Nombre total de questions')
    total_points = models.PositiveIntegerField(default=0, verbose_name='Points totaux')
    
    # Métadonnées
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tests', verbose_name='Créé par')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    # Statistiques
    total_attempts = models.PositiveIntegerField(default=0, verbose_name='Tentatives totales')
    average_score = models.FloatField(default=0, verbose_name='Score moyen')
    completion_rate = models.FloatField(default=0, verbose_name='Taux de réussite')
    
    class Meta:
        verbose_name = 'Test'
        verbose_name_plural = 'Tests'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Calculer le nombre total de questions et points
        if self.questions:
            self.total_questions = len(self.questions)
            self.total_points = sum(q.get('points', 1) for q in self.questions)
        super().save(*args, **kwargs)


class JobTest(models.Model):
    """Association entre un test et une offre d'emploi"""
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='job_tests', verbose_name='Offre d\'emploi')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='job_tests', verbose_name='Test')
    is_required = models.BooleanField(default=True, verbose_name='Obligatoire')
    order = models.PositiveIntegerField(default=0, verbose_name='Ordre')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Test d\'offre'
        verbose_name_plural = 'Tests d\'offres'
        unique_together = ['job', 'test']
        ordering = ['order', 'test__title']
    
    def __str__(self):
        return f"{self.job.title} - {self.test.title}"


class TestAttempt(models.Model):
    """Tentative de test par un candidat"""
    STATUS_CHOICES = [
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('abandoned', 'Abandonné'),
        ('expired', 'Expiré'),
    ]
    
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_attempts', verbose_name='Candidat')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts', verbose_name='Test')
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='test_attempts', null=True, blank=True, verbose_name='Offre d\'emploi')
    
    # Statut et progression
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress', verbose_name='Statut')
    current_question = models.PositiveIntegerField(default=0, verbose_name='Question actuelle')
    
    # Réponses
    answers = models.JSONField(default=dict, verbose_name='Réponses')
    score = models.FloatField(default=0, verbose_name='Score')
    percentage = models.FloatField(default=0, verbose_name='Pourcentage')
    passed = models.BooleanField(default=False, verbose_name='Réussi')
    
    # Temps
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Commencé le')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Terminé le')
    time_spent = models.PositiveIntegerField(default=0, help_text='Temps en secondes', verbose_name='Temps passé')
    
    # Métadonnées
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Adresse IP')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    
    class Meta:
        verbose_name = 'Tentative de test'
        verbose_name_plural = 'Tentatives de test'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.candidate.full_name} - {self.test.title}"
    
    def save(self, *args, **kwargs):
        # Calculer le score et le pourcentage
        if self.answers and self.test.total_points > 0:
            self.score = self.calculate_score()
            self.percentage = (self.score / self.test.total_points) * 100
            self.passed = self.percentage >= self.test.passing_score
        
        # Marquer comme terminé si toutes les questions sont répondues
        if self.current_question >= self.test.total_questions and self.status == 'in_progress':
            self.status = 'completed'
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def calculate_score(self):
        """Calculer le score basé sur les réponses"""
        score = 0
        for question_id, answer in self.answers.items():
            question = self.get_question_by_id(question_id)
            if question and self.is_correct_answer(question, answer):
                score += question.get('points', 1)
        return score
    
    def get_question_by_id(self, question_id):
        """Récupérer une question par son ID"""
        for question in self.test.questions:
            if str(question.get('id')) == str(question_id):
                return question
        return None
    
    def is_correct_answer(self, question, answer):
        """Vérifier si une réponse est correcte"""
        question_type = question.get('type', 'multiple_choice')
        correct_answer = question.get('correct_answer')
        
        if question_type == 'multiple_choice':
            return str(answer) == str(correct_answer)
        elif question_type == 'multiple_select':
            return set(answer) == set(correct_answer)
        elif question_type == 'true_false':
            return bool(answer) == bool(correct_answer)
        elif question_type == 'text':
            # Pour les questions texte, on peut faire une comparaison simple
            return str(answer).lower().strip() == str(correct_answer).lower().strip()
        
        return False


class TestResult(models.Model):
    """Résultat détaillé d'un test"""
    attempt = models.OneToOneField(TestAttempt, on_delete=models.CASCADE, related_name='result', verbose_name='Tentative')
    
    # Détails des réponses
    question_results = models.JSONField(default=list, verbose_name='Résultats par question')
    correct_answers = models.PositiveIntegerField(default=0, verbose_name='Réponses correctes')
    incorrect_answers = models.PositiveIntegerField(default=0, verbose_name='Réponses incorrectes')
    skipped_questions = models.PositiveIntegerField(default=0, verbose_name='Questions ignorées')
    
    # Analyse
    strengths = models.JSONField(default=list, verbose_name='Points forts')
    weaknesses = models.JSONField(default=list, verbose_name='Points faibles')
    recommendations = models.TextField(blank=True, verbose_name='Recommandations')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Résultat de test'
        verbose_name_plural = 'Résultats de test'
    
    def __str__(self):
        return f"Résultat - {self.attempt}"


class TestCertificate(models.Model):
    """Certificat de réussite d'un test"""
    attempt = models.OneToOneField(TestAttempt, on_delete=models.CASCADE, related_name='certificate', verbose_name='Tentative')
    certificate_number = models.CharField(max_length=50, unique=True, verbose_name='Numéro de certificat')
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name='Émis le')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Expire le')
    is_valid = models.BooleanField(default=True, verbose_name='Valide')
    
    # Fichier du certificat
    certificate_file = CloudinaryField('certificates', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Certificat de test'
        verbose_name_plural = 'Certificats de test'
    
    def __str__(self):
        return f"Certificat {self.certificate_number} - {self.attempt.candidate.full_name}"


class TestAnalytics(models.Model):
    """Analytics et statistiques des tests"""
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='analytics', verbose_name='Test')
    date = models.DateField(verbose_name='Date')
    
    # Statistiques quotidiennes
    total_attempts = models.PositiveIntegerField(default=0, verbose_name='Tentatives totales')
    completed_attempts = models.PositiveIntegerField(default=0, verbose_name='Tentatives terminées')
    passed_attempts = models.PositiveIntegerField(default=0, verbose_name='Tentatives réussies')
    average_score = models.FloatField(default=0, verbose_name='Score moyen')
    average_time = models.FloatField(default=0, verbose_name='Temps moyen')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Analytics de test'
        verbose_name_plural = 'Analytics de tests'
        unique_together = ['test', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics {self.test.title} - {self.date}"