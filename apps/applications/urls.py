from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    # Candidatures
    path('apply/<int:job_id>/', views.apply_to_job, name='apply_to_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('<int:pk>/', views.application_detail, name='application_detail'),
    path('<int:pk>/withdraw/', views.withdraw_application, name='withdraw_application'),
    
    # Gestion admin/hr
    path('', views.applications_list, name='applications_list'),
    path('<int:pk>/update-status/', views.update_application_status, name='update_status'),
    path('<int:pk>/add-comment/', views.add_comment, name='add_comment'),
    path('<int:pk>/rate/', views.rate_application, name='rate_application'),
    
    # Entretiens
    path('<int:pk>/schedule-interview/', views.schedule_interview, name='schedule_interview'),
    path('interview/<int:interview_id>/feedback/', views.interview_feedback, name='interview_feedback'),
    
    # Candidatures vidéo
    path('apply-with-video/<int:job_id>/', views.apply_with_video, name='apply_with_video'),
    path('video-applications/', views.video_applications_list, name='video_applications_list'),
    path('video-application/<int:video_app_id>/', views.video_application_detail, name='video_application_detail'),
    path('video-application/<int:video_app_id>/process/', views.process_video_application, name='process_video_application'),
    path('video-application/analytics/', views.video_application_analytics, name='video_application_analytics'),
    
    # Gestion des questions vidéo
    path('job/<int:job_id>/video-questions/', views.video_questions_management, name='video_questions_management'),
    path('video-question/<int:question_id>/edit/', views.edit_video_question, name='edit_video_question'),
    path('video-question/<int:question_id>/delete/', views.delete_video_question, name='delete_video_question'),
]
