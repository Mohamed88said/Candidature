from django.urls import path
from . import views

app_name = 'company_reviews'

urlpatterns = [
    # Liste et détail des entreprises
    path('', views.companies_list, name='companies_list'),
    path('company/<slug:slug>/', views.company_detail, name='company_detail'),
    path('company/<slug:slug>/reviews/', views.company_reviews, name='company_reviews'),
    
    # Avis
    path('company/<int:company_id>/write-review/', views.write_review, name='write_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    
    # Informations salariales
    path('company/<int:company_id>/add-salary/', views.add_salary, name='add_salary'),
    
    # Expériences d'entretien
    path('company/<int:company_id>/add-interview/', views.add_interview, name='add_interview'),
    
    # Photos
    path('company/<int:company_id>/add-photo/', views.add_photo, name='add_photo'),
    
    # Suivi d'entreprises
    path('company/<int:company_id>/follow/', views.follow_company, name='follow_company'),
    path('company/<int:company_id>/unfollow/', views.unfollow_company, name='unfollow_company'),
    
    # Profil utilisateur
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('followed-companies/', views.followed_companies, name='followed_companies'),
    
    # API AJAX
    path('api/review/<int:review_id>/vote-helpful/', views.vote_helpful, name='vote_helpful'),
    path('api/review/<int:review_id>/respond/', views.respond_to_review, name='respond_to_review'),
]


