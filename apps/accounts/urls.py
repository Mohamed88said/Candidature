from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentification
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Profil
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Formation
    path('education/add/', views.add_education, name='add_education'),
    path('education/<int:education_id>/edit/', views.edit_education, name='edit_education'),
    path('education/<int:education_id>/delete/', views.delete_education, name='delete_education'),
    
    # Expérience
    path('experience/add/', views.add_experience, name='add_experience'),
    path('experience/<int:experience_id>/edit/', views.edit_experience, name='edit_experience'),
    path('experience/<int:experience_id>/delete/', views.delete_experience, name='delete_experience'),
    
    # Compétences
    path('skill/add/', views.add_skill, name='add_skill'),
    path('skill/<int:skill_id>/delete/', views.delete_skill, name='delete_skill'),
    
    # Langues
    path('language/add/', views.add_language, name='add_language'),
    path('language/<int:language_id>/delete/', views.delete_language, name='delete_language'),
    
    # Certifications
    path('certification/add/', views.add_certification, name='add_certification'),
    path('certification/<int:certification_id>/delete/', views.delete_certification, name='delete_certification'),
    
    # Références
    path('reference/add/', views.add_reference, name='add_reference'),
    path('reference/<int:reference_id>/delete/', views.delete_reference, name='delete_reference'),
    
    # Projets
    path('project/add/', views.add_project, name='add_project'),
    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    
    # Profils sociaux
    path('social/add/', views.add_social_profile, name='add_social_profile'),
    path('social/<int:profile_id>/delete/', views.delete_social_profile, name='delete_social_profile'),
    
    # Prix et reconnaissances
    path('award/add/', views.add_award, name='add_award'),
    path('award/<int:award_id>/delete/', views.delete_award, name='delete_award'),
    
    # Réinitialisation de mot de passe
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]
