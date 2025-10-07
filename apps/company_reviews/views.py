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
from datetime import datetime, timedelta

from .models import (
    Company, CompanyReview, ReviewHelpful, ReviewResponse,
    CompanySalary, CompanyInterview, CompanyBenefit, CompanyPhoto, CompanyFollow
)
from .forms import (
    CompanyForm, CompanyReviewForm, ReviewHelpfulForm, ReviewResponseForm,
    CompanySalaryForm, CompanyInterviewForm, CompanyBenefitForm, CompanyPhotoForm,
    CompanySearchForm, ReviewSearchForm
)


def companies_list(request):
    """Liste des entreprises"""
    try:
        companies = Company.objects.filter(is_active=True).order_by('-created_at')
        
        # Filtres
        search_form = CompanySearchForm(request.GET)
        if search_form.is_valid():
            search_query = search_form.cleaned_data.get('search_query')
            industry = search_form.cleaned_data.get('industry')
            size = search_form.cleaned_data.get('size')
            location = search_form.cleaned_data.get('location')
            min_rating = search_form.cleaned_data.get('min_rating')
            
            if search_query:
                companies = companies.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query)
                )
            
            if industry:
                companies = companies.filter(industry__icontains=industry)
            
            if size:
                companies = companies.filter(size=size)
            
            if location:
                companies = companies.filter(headquarters__icontains=location)
            
            if min_rating:
                # Filtrer par note moyenne
                companies = companies.annotate(
                    avg_rating=Avg('reviews__overall_rating', filter=Q(reviews__is_approved=True))
                ).filter(avg_rating__gte=float(min_rating))
        
        # Pagination
        paginator = Paginator(companies, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'search_form': search_form,
        }
        
        return render(request, 'company_reviews/companies_list.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des entreprises: {e}")
        return redirect('home')


def company_detail(request, slug):
    """Détail d'une entreprise"""
    try:
        company = get_object_or_404(Company, slug=slug, is_active=True)
        
        # Avis approuvés
        reviews = company.reviews.filter(is_approved=True).order_by('-created_at')
        
        # Statistiques
        total_reviews = reviews.count()
        average_rating = company.get_average_rating()
        rating_distribution = company.get_rating_distribution()
        
        # Avis récents
        recent_reviews = reviews[:5]
        
        # Salaires
        salaries = company.salaries.filter(is_approved=True).order_by('-created_at')[:5]
        
        # Entretiens
        interviews = company.interviews.filter(is_approved=True).order_by('-created_at')[:5]
        
        # Photos
        photos = company.photos.filter(is_approved=True).order_by('-created_at')[:10]
        
        # Avantages
        benefits = company.benefits.filter(is_available=True).order_by('category', 'name')
        
        # Vérifier si l'utilisateur suit cette entreprise
        is_following = False
        if request.user.is_authenticated:
            is_following = CompanyFollow.objects.filter(
                user=request.user, company=company
            ).exists()
        
        context = {
            'company': company,
            'reviews': recent_reviews,
            'total_reviews': total_reviews,
            'average_rating': average_rating,
            'rating_distribution': rating_distribution,
            'salaries': salaries,
            'interviews': interviews,
            'photos': photos,
            'benefits': benefits,
            'is_following': is_following,
        }
        
        return render(request, 'company_reviews/company_detail.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement de l'entreprise: {e}")
        return redirect('company_reviews:companies_list')


@login_required
def write_review(request, company_id):
    """Écrire un avis sur une entreprise"""
    try:
        company = get_object_or_404(Company, id=company_id, is_active=True)
        
        # Vérifier si l'utilisateur a déjà écrit un avis
        existing_review = CompanyReview.objects.filter(
            company=company, user=request.user
        ).first()
        
        if existing_review:
            messages.info(request, 'Vous avez déjà écrit un avis pour cette entreprise.')
            return redirect('company_reviews:company_detail', slug=company.slug)
        
        if request.method == 'POST':
            form = CompanyReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.company = company
                review.user = request.user
                review.save()
                
                messages.success(request, 'Votre avis a été soumis et sera examiné avant publication.')
                return redirect('company_reviews:company_detail', slug=company.slug)
        else:
            form = CompanyReviewForm()
        
        context = {
            'company': company,
            'form': form,
        }
        
        return render(request, 'company_reviews/write_review.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de l'écriture de l'avis: {e}")
        return redirect('company_reviews:companies_list')


@login_required
def edit_review(request, review_id):
    """Modifier un avis existant"""
    try:
        review = get_object_or_404(CompanyReview, id=review_id, user=request.user)
        
        if request.method == 'POST':
            form = CompanyReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                messages.success(request, 'Votre avis a été mis à jour.')
                return redirect('company_reviews:company_detail', slug=review.company.slug)
        else:
            form = CompanyReviewForm(instance=review)
        
        context = {
            'review': review,
            'form': form,
        }
        
        return render(request, 'company_reviews/edit_review.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la modification de l'avis: {e}")
        return redirect('company_reviews:companies_list')


@login_required
def delete_review(request, review_id):
    """Supprimer un avis"""
    try:
        review = get_object_or_404(CompanyReview, id=review_id, user=request.user)
        
        if request.method == 'POST':
            company_slug = review.company.slug
            review.delete()
            messages.success(request, 'Votre avis a été supprimé.')
            return redirect('company_reviews:company_detail', slug=company_slug)
        
        context = {
            'review': review,
        }
        
        return render(request, 'company_reviews/delete_review.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression de l'avis: {e}")
        return redirect('company_reviews:companies_list')


def company_reviews(request, slug):
    """Liste des avis d'une entreprise"""
    try:
        company = get_object_or_404(Company, slug=slug, is_active=True)
        
        reviews = company.reviews.filter(is_approved=True).order_by('-created_at')
        
        # Filtres
        search_form = ReviewSearchForm(request.GET)
        if search_form.is_valid():
            search_query = search_form.cleaned_data.get('search_query')
            rating = search_form.cleaned_data.get('rating')
            employment_status = search_form.cleaned_data.get('employment_status')
            date_from = search_form.cleaned_data.get('date_from')
            date_to = search_form.cleaned_data.get('date_to')
            
            if search_query:
                reviews = reviews.filter(
                    Q(pros__icontains=search_query) |
                    Q(cons__icontains=search_query) |
                    Q(advice_to_management__icontains=search_query)
                )
            
            if rating:
                reviews = reviews.filter(overall_rating=rating)
            
            if employment_status:
                reviews = reviews.filter(employment_status=employment_status)
            
            if date_from:
                reviews = reviews.filter(created_at__date__gte=date_from)
            
            if date_to:
                reviews = reviews.filter(created_at__date__lte=date_to)
        
        # Pagination
        paginator = Paginator(reviews, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'company': company,
            'page_obj': page_obj,
            'search_form': search_form,
        }
        
        return render(request, 'company_reviews/company_reviews.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des avis: {e}")
        return redirect('company_reviews:companies_list')


@login_required
def add_salary(request, company_id):
    """Ajouter des informations salariales"""
    try:
        company = get_object_or_404(Company, id=company_id, is_active=True)
        
        if request.method == 'POST':
            form = CompanySalaryForm(request.POST)
            if form.is_valid():
                salary = form.save(commit=False)
                salary.company = company
                salary.user = request.user
                salary.save()
                
                messages.success(request, 'Vos informations salariales ont été soumises et seront examinées avant publication.')
                return redirect('company_reviews:company_detail', slug=company.slug)
        else:
            form = CompanySalaryForm()
        
        context = {
            'company': company,
            'form': form,
        }
        
        return render(request, 'company_reviews/add_salary.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de l'ajout des informations salariales: {e}")
        return redirect('company_reviews:companies_list')


@login_required
def add_interview(request, company_id):
    """Ajouter une expérience d'entretien"""
    try:
        company = get_object_or_404(Company, id=company_id, is_active=True)
        
        if request.method == 'POST':
            form = CompanyInterviewForm(request.POST)
            if form.is_valid():
                interview = form.save(commit=False)
                interview.company = company
                interview.user = request.user
                interview.save()
                
                messages.success(request, 'Votre expérience d\'entretien a été soumise et sera examinée avant publication.')
                return redirect('company_reviews:company_detail', slug=company.slug)
        else:
            form = CompanyInterviewForm()
        
        context = {
            'company': company,
            'form': form,
        }
        
        return render(request, 'company_reviews/add_interview.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de l'ajout de l'expérience d'entretien: {e}")
        return redirect('company_reviews:companies_list')


@login_required
def add_photo(request, company_id):
    """Ajouter une photo d'entreprise"""
    try:
        company = get_object_or_404(Company, id=company_id, is_active=True)
        
        if request.method == 'POST':
            form = CompanyPhotoForm(request.POST, request.FILES)
            if form.is_valid():
                photo = form.save(commit=False)
                photo.company = company
                photo.user = request.user
                photo.save()
                
                messages.success(request, 'Votre photo a été soumise et sera examinée avant publication.')
                return redirect('company_reviews:company_detail', slug=company.slug)
        else:
            form = CompanyPhotoForm()
        
        context = {
            'company': company,
            'form': form,
        }
        
        return render(request, 'company_reviews/add_photo.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de l'ajout de la photo: {e}")
        return redirect('company_reviews:companies_list')


@login_required
def follow_company(request, company_id):
    """Suivre une entreprise"""
    try:
        company = get_object_or_404(Company, id=company_id, is_active=True)
        
        follow, created = CompanyFollow.objects.get_or_create(
            user=request.user,
            company=company
        )
        
        if created:
            messages.success(request, f'Vous suivez maintenant {company.name}.')
        else:
            messages.info(request, f'Vous suivez déjà {company.name}.')
        
        return redirect('company_reviews:company_detail', slug=company.slug)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du suivi de l'entreprise: {e}")
        return redirect('company_reviews:companies_list')


@login_required
def unfollow_company(request, company_id):
    """Ne plus suivre une entreprise"""
    try:
        company = get_object_or_404(Company, id=company_id, is_active=True)
        
        follow = CompanyFollow.objects.filter(
            user=request.user,
            company=company
        ).first()
        
        if follow:
            follow.delete()
            messages.success(request, f'Vous ne suivez plus {company.name}.')
        else:
            messages.info(request, f'Vous ne suivez pas {company.name}.')
        
        return redirect('company_reviews:company_detail', slug=company.slug)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de l'arrêt du suivi: {e}")
        return redirect('company_reviews:companies_list')


@login_required
def my_reviews(request):
    """Mes avis"""
    try:
        reviews = CompanyReview.objects.filter(user=request.user).order_by('-created_at')
        
        # Pagination
        paginator = Paginator(reviews, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
        }
        
        return render(request, 'company_reviews/my_reviews.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement de vos avis: {e}")
        return redirect('company_reviews:companies_list')


@login_required
def followed_companies(request):
    """Entreprises suivies"""
    try:
        followed_companies = CompanyFollow.objects.filter(
            user=request.user
        ).select_related('company').order_by('-created_at')
        
        # Pagination
        paginator = Paginator(followed_companies, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
        }
        
        return render(request, 'company_reviews/followed_companies.html', context)
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement des entreprises suivies: {e}")
        return redirect('company_reviews:companies_list')


# API Views pour AJAX
@login_required
@require_http_methods(["POST"])
def vote_helpful(request, review_id):
    """Voter sur l'utilité d'un avis"""
    try:
        review = get_object_or_404(CompanyReview, id=review_id)
        is_helpful = request.POST.get('is_helpful') == 'true'
        
        vote, created = ReviewHelpful.objects.get_or_create(
            review=review,
            user=request.user,
            defaults={'is_helpful': is_helpful}
        )
        
        if not created:
            vote.is_helpful = is_helpful
            vote.save()
        
        # Compter les votes
        helpful_count = review.helpful_votes.filter(is_helpful=True).count()
        not_helpful_count = review.helpful_votes.filter(is_helpful=False).count()
        
        return JsonResponse({
            'success': True,
            'helpful_count': helpful_count,
            'not_helpful_count': not_helpful_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def respond_to_review(request, review_id):
    """Répondre à un avis (entreprise)"""
    try:
        review = get_object_or_404(CompanyReview, id=review_id)
        
        # Vérifier si l'utilisateur est autorisé à répondre
        if not request.user.is_staff and not request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'error': 'Non autorisé'
            }, status=403)
        
        response_text = request.POST.get('response_text')
        if not response_text:
            return JsonResponse({
                'success': False,
                'error': 'Le texte de la réponse est requis'
            }, status=400)
        
        response, created = ReviewResponse.objects.get_or_create(
            review=review,
            defaults={
                'company_representative': request.user,
                'response_text': response_text
            }
        )
        
        if not created:
            response.response_text = response_text
            response.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Réponse ajoutée avec succès'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)