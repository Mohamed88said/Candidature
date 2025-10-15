from django.urls import path
from . import views

app_name = 'maps'

urlpatterns = [
    # Dashboard et carte principale
    path('', views.maps_dashboard, name='dashboard'),
    path('map/', views.interactive_map, name='interactive_map'),
    
    # Actions sur la carte
    path('save-view/', views.save_map_view, name='save_map_view'),
    path('create-bookmark/', views.create_bookmark, name='create_bookmark'),
    path('delete-bookmark/<int:bookmark_id>/', views.delete_bookmark, name='delete_bookmark'),
    
    # Recherche et données
    path('search-locations/', views.search_locations, name='search_locations'),
    path('jobs-in-radius/', views.get_jobs_in_radius, name='get_jobs_in_radius'),
    
    # Signets
    path('bookmarks/', views.my_bookmarks, name='my_bookmarks'),
    path('bookmark/<int:bookmark_id>/', views.bookmark_detail, name='bookmark_detail'),
    
    # Analytics (admin)
    path('analytics/', views.map_analytics, name='analytics'),
]


