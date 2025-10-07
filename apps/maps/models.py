from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import json

User = get_user_model()


class Location(models.Model):
    """Modèle pour stocker les informations de localisation"""
    name = models.CharField(max_length=200, verbose_name='Nom de la localisation')
    address = models.TextField(verbose_name='Adresse complète')
    city = models.CharField(max_length=100, verbose_name='Ville')
    region = models.CharField(max_length=100, verbose_name='Région')
    country = models.CharField(max_length=100, default='France', verbose_name='Pays')
    postal_code = models.CharField(max_length=20, verbose_name='Code postal')
    
    # Coordonnées géographiques
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Latitude')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Longitude')
    
    # Informations supplémentaires
    is_remote = models.BooleanField(default=False, verbose_name='Télétravail')
    is_hybrid = models.BooleanField(default=False, verbose_name='Hybride')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Localisation'
        verbose_name_plural = 'Localisations'
        ordering = ['city', 'name']
        unique_together = ['latitude', 'longitude']
    
    def __str__(self):
        return f"{self.name}, {self.city}"
    
    def get_coordinates(self):
        """Retourner les coordonnées sous forme de tuple"""
        return (float(self.latitude), float(self.longitude))
    
    def get_full_address(self):
        """Retourner l'adresse complète"""
        return f"{self.address}, {self.postal_code} {self.city}, {self.region}, {self.country}"


class JobLocation(models.Model):
    """Modèle pour lier les offres d'emploi aux localisations"""
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='job_locations', verbose_name='Offre d\'emploi')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='job_locations', verbose_name='Localisation')
    
    # Type de localisation pour cette offre
    LOCATION_TYPE_CHOICES = [
        ('primary', 'Localisation principale'),
        ('secondary', 'Localisation secondaire'),
        ('remote', 'Télétravail'),
        ('hybrid', 'Hybride'),
    ]
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPE_CHOICES, default='primary', verbose_name='Type de localisation')
    
    # Informations spécifiques à cette offre
    is_primary = models.BooleanField(default=True, verbose_name='Localisation principale')
    work_days_per_week = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(7)], verbose_name='Jours de travail par semaine')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Localisation d\'offre'
        verbose_name_plural = 'Localisations d\'offres'
        unique_together = ['job', 'location']
        ordering = ['-is_primary', 'created_at']
    
    def __str__(self):
        return f"{self.job.title} - {self.location.name}"


class MapView(models.Model):
    """Modèle pour stocker les vues de carte des utilisateurs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='map_views', verbose_name='Utilisateur')
    
    # Paramètres de la vue
    center_latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Latitude du centre')
    center_longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Longitude du centre')
    zoom_level = models.PositiveIntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(20)], verbose_name='Niveau de zoom')
    
    # Filtres appliqués
    filters = models.JSONField(default=dict, verbose_name='Filtres appliqués')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Vue de carte'
        verbose_name_plural = 'Vues de carte'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Vue de {self.user.full_name} - {self.created_at.date()}"


class MapBookmark(models.Model):
    """Modèle pour les signets de carte des utilisateurs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='map_bookmarks', verbose_name='Utilisateur')
    name = models.CharField(max_length=200, verbose_name='Nom du signet')
    description = models.TextField(blank=True, verbose_name='Description')
    
    # Paramètres de la vue sauvegardée
    center_latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Latitude du centre')
    center_longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Longitude du centre')
    zoom_level = models.PositiveIntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(20)], verbose_name='Niveau de zoom')
    
    # Filtres sauvegardés
    filters = models.JSONField(default=dict, verbose_name='Filtres sauvegardés')
    
    # Métadonnées
    is_public = models.BooleanField(default=False, verbose_name='Public')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Signet de carte'
        verbose_name_plural = 'Signets de carte'
        ordering = ['-updated_at']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.user.full_name}"


class MapAnalytics(models.Model):
    """Modèle pour les analytics de la carte"""
    date = models.DateField(verbose_name='Date')
    
    # Statistiques générales
    total_views = models.PositiveIntegerField(default=0, verbose_name='Vues totales')
    unique_users = models.PositiveIntegerField(default=0, verbose_name='Utilisateurs uniques')
    total_searches = models.PositiveIntegerField(default=0, verbose_name='Recherches totales')
    
    # Statistiques par localisation
    most_viewed_locations = models.JSONField(default=list, verbose_name='Localisations les plus vues')
    most_searched_cities = models.JSONField(default=list, verbose_name='Villes les plus recherchées')
    
    # Statistiques par type d'offre
    remote_jobs_views = models.PositiveIntegerField(default=0, verbose_name='Vues d\'offres à distance')
    hybrid_jobs_views = models.PositiveIntegerField(default=0, verbose_name='Vues d\'offres hybrides')
    on_site_jobs_views = models.PositiveIntegerField(default=0, verbose_name='Vues d\'offres sur site')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Analytics de carte'
        verbose_name_plural = 'Analytics de cartes'
        unique_together = ['date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics - {self.date}"


class MapHeatmap(models.Model):
    """Modèle pour les données de heatmap"""
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='heatmap_data', verbose_name='Localisation')
    
    # Données de la heatmap
    intensity = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], verbose_name='Intensité')
    job_count = models.PositiveIntegerField(default=0, verbose_name='Nombre d\'offres')
    view_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de vues')
    
    # Période de calcul
    period_start = models.DateTimeField(verbose_name='Début de période')
    period_end = models.DateTimeField(verbose_name='Fin de période')
    
    # Métadonnées
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name='Calculé le')
    
    class Meta:
        verbose_name = 'Données de heatmap'
        verbose_name_plural = 'Données de heatmap'
        ordering = ['-intensity']
    
    def __str__(self):
        return f"Heatmap - {self.location.name} ({self.intensity:.2f})"


class MapCluster(models.Model):
    """Modèle pour les clusters de localisations"""
    name = models.CharField(max_length=200, verbose_name='Nom du cluster')
    center_latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Latitude du centre')
    center_longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Longitude du centre')
    
    # Informations du cluster
    job_count = models.PositiveIntegerField(default=0, verbose_name='Nombre d\'offres')
    location_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de localisations')
    radius = models.FloatField(verbose_name='Rayon du cluster (km)')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Cluster de carte'
        verbose_name_plural = 'Clusters de carte'
        ordering = ['-job_count']
    
    def __str__(self):
        return f"Cluster {self.name} ({self.job_count} offres)"


class MapSearch(models.Model):
    """Modèle pour les recherches sur la carte"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='map_searches', verbose_name='Utilisateur', null=True, blank=True)
    
    # Paramètres de recherche
    query = models.CharField(max_length=500, verbose_name='Requête de recherche')
    location_query = models.CharField(max_length=200, blank=True, verbose_name='Localisation recherchée')
    
    # Coordonnées de recherche
    search_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Latitude de recherche')
    search_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Longitude de recherche')
    search_radius = models.FloatField(default=50, verbose_name='Rayon de recherche (km)')
    
    # Résultats
    results_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de résultats')
    filters_applied = models.JSONField(default=dict, verbose_name='Filtres appliqués')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        verbose_name = 'Recherche de carte'
        verbose_name_plural = 'Recherches de carte'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Recherche: {self.query} - {self.results_count} résultats"