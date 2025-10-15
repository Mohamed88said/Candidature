"""
URL configuration for recruitment_platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('jobs/', include('apps.jobs.urls')),
    path('applications/', include('apps.applications.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('matching/', include('apps.matching.urls')),
    path('chat/', include('apps.chat.urls')),
    path('tests/', include('apps.tests.urls')),
    path('alerts/', include('apps.alerts.urls')),
    path('maps/', include('apps.maps.urls')),
    path('cv-builder/', include('apps.cv_builder.urls')),
    path('referrals/', include('apps.referrals.urls')),
    path('company-reviews/', include('apps.company_reviews.urls')),
    path('notifications/', include('apps.push_notifications.urls')),
    path('gamification/', include('apps.gamification.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "Plateforme de Recrutement"
admin.site.site_title = "Administration"
admin.site.index_title = "Panneau d'administration"