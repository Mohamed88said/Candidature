from django.urls import path
from . import views

app_name = 'cv_builder'

urlpatterns = [
    # Dashboard et galerie
    path('', views.cv_builder_dashboard, name='dashboard'),
    path('templates/', views.template_gallery, name='template_gallery'),
    
    # Gestion des CVs
    path('create/', views.create_cv, name='create_cv'),
    path('create/<int:template_id>/', views.create_cv, name='create_cv_with_template'),
    path('edit/<int:cv_id>/', views.edit_cv, name='edit_cv'),
    path('preview/<int:cv_id>/', views.preview_cv, name='preview_cv'),
    path('my-cvs/', views.my_cvs, name='my_cvs'),
    path('delete/<int:cv_id>/', views.delete_cv, name='delete_cv'),
    
    # Partage et téléchargement
    path('share/<int:cv_id>/', views.share_cv, name='share_cv'),
    path('download/<int:cv_id>/<str:format>/', views.download_cv, name='download_cv'),
    path('view/<str:share_url>/', views.public_cv_view, name='public_cv_view'),
    
    # Analytics et paramètres
    path('analytics/<int:cv_id>/', views.cv_analytics, name='cv_analytics'),
    path('settings/', views.cv_settings, name='cv_settings'),
    
    # API AJAX
    path('api/save-section/<int:cv_id>/', views.save_cv_section, name='save_cv_section'),
    path('api/duplicate/<int:cv_id>/', views.duplicate_cv, name='duplicate_cv'),
    path('api/change-template/<int:cv_id>/', views.change_cv_template, name='change_cv_template'),
]


