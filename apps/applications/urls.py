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
]