from django.urls import path
from . import views

app_name = 'tests'

urlpatterns = [
    # Dashboard et liste des tests
    path('', views.tests_dashboard, name='dashboard'),
    path('list/', views.tests_list, name='tests_list'),
    path('test/<int:test_id>/', views.test_detail, name='test_detail'),
    
    # Passage des tests
    path('test/<int:test_id>/start/', views.start_test, name='start_test'),
    path('attempt/<int:attempt_id>/', views.take_test, name='take_test'),
    path('attempt/<int:attempt_id>/result/', views.test_result, name='test_result'),
    
    # Mes tentatives et certificats
    path('my-attempts/', views.my_attempts, name='my_attempts'),
    path('my-certificates/', views.my_certificates, name='my_certificates'),
    
    # Analytics (admin)
    path('test/<int:test_id>/analytics/', views.test_analytics, name='test_analytics'),
]



