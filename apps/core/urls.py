from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('sitemap/', views.sitemap, name='sitemap'),
    
    # Recherche
    path('search/', views.search, name='search'),
    
    # Newsletter
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('newsletter/unsubscribe/<str:email>/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
    
    # Blog
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blog/tag/<str:tag>/', views.blog_by_tag, name='blog_by_tag'),

    # =========================================================================
    # ENDPOINTS DE SANTÉ POUR ÉVITER L'HIBERNATION
    # =========================================================================
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    path('ping/', views.PingView.as_view(), name='ping'),
    path('status/', views.StatusView.as_view(), name='status'),
    path('api/health/', views.DeepHealthView.as_view(), name='api_health'),
    # =========================================================================
]