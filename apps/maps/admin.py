from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Location, JobLocation, MapView, MapBookmark, MapAnalytics,
    MapHeatmap, MapCluster, MapSearch
)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'city', 'region', 'country', 'coordinates_display',
        'is_remote', 'is_hybrid', 'job_count', 'created_at'
    ]
    list_filter = ['is_remote', 'is_hybrid', 'country', 'region', 'created_at']
    search_fields = ['name', 'city', 'region', 'country', 'address']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'address', 'city', 'region', 'country', 'postal_code')
        }),
        ('Coordonnées', {
            'fields': ('latitude', 'longitude')
        }),
        ('Options', {
            'fields': ('is_remote', 'is_hybrid')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def coordinates_display(self, obj):
        return f"{obj.latitude}, {obj.longitude}"
    coordinates_display.short_description = 'Coordonnées'
    
    def job_count(self, obj):
        return obj.job_locations.count()
    job_count.short_description = 'Nombre d\'offres'


@admin.register(JobLocation)
class JobLocationAdmin(admin.ModelAdmin):
    list_display = [
        'job', 'location', 'location_type', 'is_primary',
        'work_days_per_week', 'created_at'
    ]
    list_filter = ['location_type', 'is_primary', 'created_at']
    search_fields = ['job__title', 'job__company', 'location__name', 'location__city']
    readonly_fields = ['created_at']
    raw_id_fields = ['job', 'location']
    
    fieldsets = (
        ('Liaison', {
            'fields': ('job', 'location')
        }),
        ('Configuration', {
            'fields': ('location_type', 'is_primary', 'work_days_per_week')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(MapView)
class MapViewAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'center_coordinates', 'zoom_level', 'created_at', 'updated_at'
    ]
    list_filter = ['zoom_level', 'created_at', 'updated_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Position', {
            'fields': ('center_latitude', 'center_longitude', 'zoom_level')
        }),
        ('Filtres', {
            'fields': ('filters',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def center_coordinates(self, obj):
        return f"{obj.center_latitude}, {obj.center_longitude}"
    center_coordinates.short_description = 'Coordonnées du centre'


@admin.register(MapBookmark)
class MapBookmarkAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user', 'center_coordinates', 'zoom_level',
        'is_public', 'created_at', 'updated_at'
    ]
    list_filter = ['is_public', 'created_at', 'updated_at']
    search_fields = ['name', 'description', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'description', 'user')
        }),
        ('Position', {
            'fields': ('center_latitude', 'center_longitude', 'zoom_level')
        }),
        ('Configuration', {
            'fields': ('filters', 'is_public')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def center_coordinates(self, obj):
        return f"{obj.center_latitude}, {obj.center_longitude}"
    center_coordinates.short_description = 'Coordonnées du centre'


@admin.register(MapAnalytics)
class MapAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'total_views', 'unique_users', 'total_searches',
        'remote_jobs_views', 'hybrid_jobs_views', 'on_site_jobs_views'
    ]
    list_filter = ['date']
    search_fields = ['date']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Date', {
            'fields': ('date',)
        }),
        ('Statistiques générales', {
            'fields': ('total_views', 'unique_users', 'total_searches')
        }),
        ('Statistiques par localisation', {
            'fields': ('most_viewed_locations', 'most_searched_cities')
        }),
        ('Statistiques par type', {
            'fields': ('remote_jobs_views', 'hybrid_jobs_views', 'on_site_jobs_views')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(MapHeatmap)
class MapHeatmapAdmin(admin.ModelAdmin):
    list_display = [
        'location', 'intensity', 'job_count', 'view_count',
        'period_start', 'period_end', 'calculated_at'
    ]
    list_filter = ['calculated_at', 'period_start', 'period_end']
    search_fields = ['location__name', 'location__city']
    readonly_fields = ['calculated_at']
    raw_id_fields = ['location']
    
    fieldsets = (
        ('Localisation', {
            'fields': ('location',)
        }),
        ('Données de heatmap', {
            'fields': ('intensity', 'job_count', 'view_count')
        }),
        ('Période', {
            'fields': ('period_start', 'period_end')
        }),
        ('Métadonnées', {
            'fields': ('calculated_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(MapCluster)
class MapClusterAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'center_coordinates', 'job_count', 'location_count',
        'radius', 'created_at', 'updated_at'
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name',)
        }),
        ('Position et taille', {
            'fields': ('center_latitude', 'center_longitude', 'radius')
        }),
        ('Statistiques', {
            'fields': ('job_count', 'location_count')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def center_coordinates(self, obj):
        return f"{obj.center_latitude}, {obj.center_longitude}"
    center_coordinates.short_description = 'Coordonnées du centre'


@admin.register(MapSearch)
class MapSearchAdmin(admin.ModelAdmin):
    list_display = [
        'query', 'user', 'location_query', 'search_coordinates',
        'search_radius', 'results_count', 'created_at'
    ]
    list_filter = ['created_at', 'search_radius']
    search_fields = ['query', 'location_query', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Recherche', {
            'fields': ('query', 'location_query')
        }),
        ('Position de recherche', {
            'fields': ('search_latitude', 'search_longitude', 'search_radius')
        }),
        ('Résultats', {
            'fields': ('results_count', 'filters_applied')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def search_coordinates(self, obj):
        if obj.search_latitude and obj.search_longitude:
            return f"{obj.search_latitude}, {obj.search_longitude}"
        return '-'
    search_coordinates.short_description = 'Coordonnées de recherche'