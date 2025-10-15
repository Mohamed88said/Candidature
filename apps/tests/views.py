from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, F
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import render_to_string
from django.conf import settings
import json
import uuid
from datetime import datetime, timedelta

from .models import (
    Test, TestCategory, JobTest, TestAttempt, TestResult, 
    TestCertificate, TestAnalytics
)
from .forms import (
    TestForm, TestCategoryForm, QuestionForm, TestAttemptForm,
    JobTestForm, TestSearchForm, TestAnalyticsForm, TestCertificateForm,
    TestSettingsForm, TestFeedbackForm
)
from apps.jobs.models import Job
from apps.applications.models import Application


@login_required
def tests_dashboard(request):
    """Dashboard principal des tests"""
    try:
        # Statistiques générales
        total_tests = Test.objects.filter(status='active').count()
        user_attempts = TestAttempt.objects.filter(candidate=request.user).count()
        user_passed = TestAttempt.objects.filter(candidate=request.user, passed=True).count()
        user_certificates = TestCertificate.objects.filter(attempt__candidate=request.user, is_valid=True).count()
        
        # Tests récents
        recent_tests = Test.objects.filter(status='active').order_by('-created_at')[:5]
        
        # Tentatives récentes
        recent_attempts = TestAttempt.objects.filter(candidate=request.user).order_by('-started_at')[:5]
        
        # Catégories populaires
        popular_categories = TestCategory.objects.filter(
            is_active=True,
            tests__status='active'
        ).annotate(
            test_count=Count('tests')
        ).order_by('-test_count')[:6]
        
        context = {
            'total_tests': total_tests,
            'user_attempts': user_attempts,
            'user_passed': user_passed,
            'user_certificates': user_certificates,
            'recent_tests': recent_tests,
            'recent_attempts': recent_attempts,
            'popular_categories': popular_categories,
        }
        
        return render(request, 'tests/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du dashboard: {e}")
        return redirect('home')


@login_required
def tests_list(request):
    """Liste de tous les tests disponibles"""
    try:
        # Récupérer les tests actifs
        tests = Test.objects.filter(status='active').select_related('category', 'created_by')
        
        # Filtres
        search_query = request.GET.get('search', '')
        category_id = request.GET.get('category', '')
        difficulty = request.GET.get('difficulty', '')
        test_type = request.GET.get('test_type', '')
        
        if search_query:
            tests = tests.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        if category_id:
            tests = tests.filter(category_id=category_id)
        
        if difficulty:
            tests = tests.filter(difficulty=difficulty)
        
        # Filtres spécifiques à l'utilisateur
        if test_type == 'my_tests':
            tests = tests.filter(created_by=request.user)
        elif test_type == 'completed_tests':
            completed_test_ids = TestAttempt.objects.filter(
                candidate=request.user,
                status='completed'
            ).values_list('test_id', flat=True)
            tests = tests.filter(id__in=completed_test_ids)
        elif test_type == 'available_tests':
            # Tests non encore tentés ou non réussis
            attempted_test_ids = TestAttempt.objects.filter(
                candidate=request.user,
                passed=True
            ).values_list('test_id', flat=True)
            tests = tests.exclude(id__in=attempted_test_ids)
        
        # Pagination
        paginator = Paginator(tests, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Formulaires
        search_form = TestSearchForm(request.GET)
        
        context = {
            'page_obj': page_obj,
            'search_form': search_form,
            'search_query': search_query,
            'category_id': category_id,
            'difficulty': difficulty,
            'test_type': test_type,
        }
        
        return render(request, 'tests/tests_list.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des tests: {e}")
        return redirect('tests:dashboard')


@login_required
def test_detail(request, test_id):
    """Détail d'un test"""
    try:
        test = get_object_or_404(Test, id=test_id, status='active')
        
        # Vérifier les tentatives existantes
        user_attempts = TestAttempt.objects.filter(
            candidate=request.user,
            test=test
        ).order_by('-started_at')
        
        can_attempt = user_attempts.count() < test.max_attempts
        last_attempt = user_attempts.first()
        
        # Statistiques du test
        total_attempts = TestAttempt.objects.filter(test=test).count()
        passed_attempts = TestAttempt.objects.filter(test=test, passed=True).count()
        completion_rate = (passed_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        context = {
            'test': test,
            'user_attempts': user_attempts,
            'can_attempt': can_attempt,
            'last_attempt': last_attempt,
            'total_attempts': total_attempts,
            'passed_attempts': passed_attempts,
            'completion_rate': completion_rate,
        }
        
        return render(request, 'tests/test_detail.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du test: {e}")
        return redirect('tests:tests_list')


@login_required
def start_test(request, test_id):
    """Commencer un test"""
    try:
        test = get_object_or_404(Test, id=test_id, status='active')
        
        # Vérifier si l'utilisateur peut tenter le test
        existing_attempts = TestAttempt.objects.filter(
            candidate=request.user,
            test=test
        ).count()
        
        if existing_attempts >= test.max_attempts:
            messages.error(request, f'Nombre maximum de tentatives atteint ({test.max_attempts})')
            return redirect('tests:test_detail', test_id=test_id)
        
        # Créer une nouvelle tentative
        attempt = TestAttempt.objects.create(
            candidate=request.user,
            test=test,
            status='in_progress',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Mettre à jour les statistiques du test
        test.total_attempts += 1
        test.save()
        
        messages.success(request, 'Test démarré avec succès !')
        return redirect('tests:take_test', attempt_id=attempt.id)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du démarrage du test: {e}")
        return redirect('tests:test_detail', test_id=test_id)


@login_required
def take_test(request, attempt_id):
    """Passer un test"""
    try:
        attempt = get_object_or_404(TestAttempt, id=attempt_id, candidate=request.user)
        
        if attempt.status != 'in_progress':
            messages.error(request, 'Cette tentative n\'est plus active.')
            return redirect('tests:test_detail', test_id=attempt.test.id)
        
        # Vérifier si le test a expiré
        if attempt.test.time_limit > 0:
            time_elapsed = (timezone.now() - attempt.started_at).total_seconds() / 60
            if time_elapsed >= attempt.test.time_limit:
                attempt.status = 'expired'
                attempt.save()
                messages.error(request, 'Le temps imparti pour ce test a expiré.')
                return redirect('tests:test_result', attempt_id=attempt.id)
        
        # Récupérer la question actuelle
        current_question = None
        if attempt.current_question < len(attempt.test.questions):
            current_question = attempt.test.questions[attempt.current_question]
        
        if request.method == 'POST':
            form = TestAttemptForm(request.POST, test=attempt.test, candidate=request.user)
            if form.is_valid():
                # Traiter la réponse
                question_id = request.POST.get('question_id')
                answer = request.POST.get('answer')
                
                if question_id and answer is not None:
                    # Sauvegarder la réponse
                    if not attempt.answers:
                        attempt.answers = {}
                    
                    attempt.answers[str(question_id)] = answer
                    attempt.current_question += 1
                    attempt.save()
                    
                    # Vérifier si toutes les questions sont répondues
                    if attempt.current_question >= len(attempt.test.questions):
                        attempt.status = 'completed'
                        attempt.completed_at = timezone.now()
                        attempt.time_spent = int((attempt.completed_at - attempt.started_at).total_seconds())
                        attempt.save()
                        
                        # Créer le résultat détaillé
                        create_test_result(attempt)
                        
                        messages.success(request, 'Test terminé avec succès !')
                        return redirect('tests:test_result', attempt_id=attempt.id)
                    
                    # Passer à la question suivante
                    return redirect('tests:take_test', attempt_id=attempt.id)
        
        # Calculer le temps restant
        time_remaining = None
        if attempt.test.time_limit > 0:
            time_elapsed = (timezone.now() - attempt.started_at).total_seconds() / 60
            time_remaining = max(0, attempt.test.time_limit - time_elapsed)
        
        context = {
            'attempt': attempt,
            'current_question': current_question,
            'question_number': attempt.current_question + 1,
            'total_questions': len(attempt.test.questions),
            'time_remaining': time_remaining,
            'progress': (attempt.current_question / len(attempt.test.questions)) * 100,
        }
        
        return render(request, 'tests/take_test.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du passage du test: {e}")
        return redirect('tests:dashboard')


@login_required
def test_result(request, attempt_id):
    """Résultat d'un test"""
    try:
        attempt = get_object_or_404(TestAttempt, id=attempt_id, candidate=request.user)
        
        # Récupérer le résultat détaillé
        result = getattr(attempt, 'result', None)
        
        # Générer un certificat si le test est réussi
        certificate = None
        if attempt.passed and not hasattr(attempt, 'certificate'):
            certificate = create_test_certificate(attempt)
        
        context = {
            'attempt': attempt,
            'result': result,
            'certificate': certificate,
        }
        
        return render(request, 'tests/test_result.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du résultat: {e}")
        return redirect('tests:dashboard')


@login_required
def my_attempts(request):
    """Mes tentatives de tests"""
    try:
        attempts = TestAttempt.objects.filter(candidate=request.user).select_related('test', 'test__category').order_by('-started_at')
        
        # Filtres
        status = request.GET.get('status', '')
        test_id = request.GET.get('test', '')
        
        if status:
            attempts = attempts.filter(status=status)
        
        if test_id:
            attempts = attempts.filter(test_id=test_id)
        
        # Pagination
        paginator = Paginator(attempts, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'status': status,
            'test_id': test_id,
        }
        
        return render(request, 'tests/my_attempts.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des tentatives: {e}")
        return redirect('tests:dashboard')


@login_required
def my_certificates(request):
    """Mes certificats"""
    try:
        certificates = TestCertificate.objects.filter(
            attempt__candidate=request.user,
            is_valid=True
        ).select_related('attempt__test', 'attempt__test__category').order_by('-issued_at')
        
        # Pagination
        paginator = Paginator(certificates, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
        }
        
        return render(request, 'tests/my_certificates.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des certificats: {e}")
        return redirect('tests:dashboard')


@login_required
def test_analytics(request, test_id):
    """Analytics d'un test (admin)"""
    if not request.user.is_staff:
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    try:
        test = get_object_or_404(Test, id=test_id)
        
        # Statistiques générales
        total_attempts = TestAttempt.objects.filter(test=test).count()
        completed_attempts = TestAttempt.objects.filter(test=test, status='completed').count()
        passed_attempts = TestAttempt.objects.filter(test=test, passed=True).count()
        average_score = TestAttempt.objects.filter(test=test, status='completed').aggregate(
            avg_score=Avg('percentage')
        )['avg_score'] or 0
        
        # Tentatives par jour (30 derniers jours)
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_attempts = TestAttempt.objects.filter(
            test=test,
            started_at__gte=thirty_days_ago
        ).extra(
            select={'day': 'date(started_at)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # Répartition par score
        score_distribution = TestAttempt.objects.filter(
            test=test,
            status='completed'
        ).extra(
            select={
                'score_range': "CASE WHEN percentage < 50 THEN '0-49' WHEN percentage < 70 THEN '50-69' WHEN percentage < 85 THEN '70-84' ELSE '85-100' END"
            }
        ).values('score_range').annotate(
            count=Count('id')
        ).order_by('score_range')
        
        context = {
            'test': test,
            'total_attempts': total_attempts,
            'completed_attempts': completed_attempts,
            'passed_attempts': passed_attempts,
            'average_score': average_score,
            'daily_attempts': list(daily_attempts),
            'score_distribution': list(score_distribution),
        }
        
        return render(request, 'tests/test_analytics.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des analytics: {e}")
        return redirect('tests:dashboard')


# Fonctions utilitaires

def create_test_result(attempt):
    """Créer un résultat détaillé pour une tentative"""
    try:
        result = TestResult.objects.create(attempt=attempt)
        
        correct_count = 0
        incorrect_count = 0
        skipped_count = 0
        question_results = []
        
        for i, question in enumerate(attempt.test.questions):
            question_id = str(question.get('id', i))
            user_answer = attempt.answers.get(question_id)
            
            if user_answer is None:
                skipped_count += 1
                is_correct = False
            else:
                is_correct = is_correct_answer(question, user_answer)
                if is_correct:
                    correct_count += 1
                else:
                    incorrect_count += 1
            
            question_results.append({
                'question_id': question_id,
                'question_text': question.get('text', ''),
                'user_answer': user_answer,
                'correct_answer': question.get('correct_answer'),
                'is_correct': is_correct,
                'points': question.get('points', 1),
                'explanation': question.get('explanation', '')
            })
        
        result.question_results = question_results
        result.correct_answers = correct_count
        result.incorrect_answers = incorrect_count
        result.skipped_questions = skipped_count
        
        # Générer des recommandations
        result.recommendations = generate_recommendations(attempt, result)
        
        result.save()
        return result
        
    except Exception as e:
        print(f"Erreur lors de la création du résultat: {e}")
        return None


def is_correct_answer(question, answer):
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
        return str(answer).lower().strip() == str(correct_answer).lower().strip()
    
    return False


def generate_recommendations(attempt, result):
    """Générer des recommandations basées sur les résultats"""
    recommendations = []
    
    if result.percentage >= 90:
        recommendations.append("Excellent travail ! Vous maîtrisez parfaitement ce sujet.")
    elif result.percentage >= 70:
        recommendations.append("Bon travail ! Quelques points à améliorer pour une maîtrise complète.")
    elif result.percentage >= 50:
        recommendations.append("Résultat correct, mais il y a encore des progrès à faire.")
    else:
        recommendations.append("Il est recommandé de revoir les concepts de base avant de repasser le test.")
    
    if result.skipped_questions > 0:
        recommendations.append(f"Vous avez ignoré {result.skipped_questions} question(s). Essayez de répondre à toutes les questions.")
    
    return "\n".join(recommendations)


def create_test_certificate(attempt):
    """Créer un certificat pour une tentative réussie"""
    try:
        certificate_number = f"CERT-{attempt.test.id}-{attempt.id}-{uuid.uuid4().hex[:8].upper()}"
        
        certificate = TestCertificate.objects.create(
            attempt=attempt,
            certificate_number=certificate_number,
            expires_at=timezone.now() + timedelta(days=365)  # Valide 1 an
        )
        
        return certificate
        
    except Exception as e:
        print(f"Erreur lors de la création du certificat: {e}")
        return None