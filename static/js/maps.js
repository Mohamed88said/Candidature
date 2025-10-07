// Maps System JavaScript

class MapsSystem {
    constructor() {
        this.map = null;
        this.markers = [];
        this.clusters = [];
        this.heatmap = null;
        this.infoWindow = null;
        this.autocomplete = null;
        this.currentFilters = {};
        this.isClusteringEnabled = true;
        this.isHeatmapEnabled = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeMap();
        this.initializeLocationSearch();
    }
    
    setupEventListeners() {
        // Gestion des filtres
        $(document).on('change', '.filters-panel input, .filters-panel select', (e) => {
            this.debounce(() => {
                this.applyFilters();
            }, 500)();
        });
        
        // Gestion des signets
        $(document).on('click', '.bookmark-btn', (e) => {
            e.preventDefault();
            this.saveBookmark();
        });
        
        // Gestion des recherches
        $(document).on('submit', '#location-search-form', (e) => {
            e.preventDefault();
            this.searchLocation();
        });
        
        // Gestion des clics sur les marqueurs
        $(document).on('click', '.marker-info', (e) => {
            this.showMarkerDetails(e.target.dataset.markerId);
        });
    }
    
    initializeMap() {
        if (typeof google === 'undefined') {
            console.error('Google Maps API not loaded');
            return;
        }
        
        const mapElement = document.getElementById('interactive-map') || document.getElementById('dashboard-map');
        if (!mapElement) return;
        
        // Configuration par défaut
        const defaultCenter = { lat: 46.603354, lng: 1.888334 }; // Centre de la France
        const defaultZoom = 6;
        
        this.map = new google.maps.Map(mapElement, {
            zoom: defaultZoom,
            center: defaultCenter,
            mapTypeId: 'roadmap',
            styles: this.getMapStyles(),
            gestureHandling: 'greedy',
            zoomControl: true,
            mapTypeControl: true,
            scaleControl: true,
            streetViewControl: false,
            rotateControl: false,
            fullscreenControl: true
        });
        
        this.infoWindow = new google.maps.InfoWindow();
        
        // Événements de la carte
        this.map.addListener('bounds_changed', () => {
            this.updateResultsCount();
        });
        
        this.map.addListener('center_changed', () => {
            this.saveCurrentView();
        });
        
        this.map.addListener('zoom_changed', () => {
            this.saveCurrentView();
        });
        
        // Charger les paramètres depuis l'URL
        this.loadUrlParams();
    }
    
    initializeLocationSearch() {
        const searchInput = document.getElementById('location-search');
        if (!searchInput) return;
        
        this.autocomplete = new google.maps.places.Autocomplete(searchInput, {
            types: ['geocode'],
            componentRestrictions: { country: 'fr' }
        });
        
        this.autocomplete.addListener('place_changed', () => {
            const place = this.autocomplete.getPlace();
            if (place.geometry) {
                this.map.setCenter(place.geometry.location);
                this.map.setZoom(12);
                this.searchJobsInArea(place.geometry.location, 25);
            }
        });
    }
    
    loadMapData(data) {
        if (!this.map) return;
        
        this.clearMarkers();
        
        data.forEach(job => {
            const marker = this.createMarker(job);
            this.markers.push(marker);
        });
        
        if (this.isClusteringEnabled) {
            this.enableClustering();
        }
        
        this.updateResultsCount();
    }
    
    createMarker(job) {
        const position = { lat: job.latitude, lng: job.longitude };
        
        // Icône selon le type de localisation
        let iconConfig = this.getMarkerIcon(job);
        
        const marker = new google.maps.Marker({
            position: position,
            map: this.map,
            title: job.job_title,
            icon: iconConfig,
            animation: google.maps.Animation.DROP
        });
        
        // InfoWindow
        marker.addListener('click', () => {
            this.showInfoWindow(marker, job);
        });
        
        // Animation au survol
        marker.addListener('mouseover', () => {
            marker.setAnimation(google.maps.Animation.BOUNCE);
            setTimeout(() => {
                marker.setAnimation(null);
            }, 750);
        });
        
        return marker;
    }
    
    getMarkerIcon(job) {
        const baseUrl = '/static/images/';
        let iconName = 'map-marker.png';
        
        if (job.is_remote) {
            iconName = 'map-marker-remote.png';
        } else if (job.is_hybrid) {
            iconName = 'map-marker-hybrid.png';
        }
        
        return {
            url: baseUrl + iconName,
            scaledSize: new google.maps.Size(30, 30),
            anchor: new google.maps.Point(15, 30)
        };
    }
    
    showInfoWindow(marker, job) {
        const content = this.createInfoWindowContent(job);
        
        this.infoWindow.setContent(content);
        this.infoWindow.open(this.map, marker);
        
        // Ajouter des événements aux boutons dans l'InfoWindow
        google.maps.event.addListenerOnce(this.infoWindow, 'domready', () => {
            const applyBtn = document.getElementById(`apply-job-${job.job_id}`);
            if (applyBtn) {
                applyBtn.addEventListener('click', () => {
                    window.open(job.url, '_blank');
                });
            }
        });
    }
    
    createInfoWindowContent(job) {
        return `
            <div class="info-window">
                <h6>${this.escapeHtml(job.job_title)}</h6>
                <p><strong>${this.escapeHtml(job.company)}</strong></p>
                <p><i class="fas fa-map-marker-alt"></i> ${this.escapeHtml(job.location)}, ${this.escapeHtml(job.city)}</p>
                <p><i class="fas fa-briefcase"></i> ${this.escapeHtml(job.job_type)}</p>
                <p><i class="fas fa-user"></i> ${this.escapeHtml(job.experience_level)}</p>
                ${job.salary_min ? `<p><i class="fas fa-euro-sign"></i> ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()} €</p>` : ''}
                <p><i class="fas fa-clock"></i> ${this.formatDate(job.created_at)}</p>
                <div class="info-actions">
                    <button id="apply-job-${job.job_id}" class="btn btn-primary btn-sm">
                        <i class="fas fa-external-link-alt"></i> Voir l'offre
                    </button>
                </div>
            </div>
        `;
    }
    
    clearMarkers() {
        this.markers.forEach(marker => marker.setMap(null));
        this.markers = [];
        
        if (this.clusters.length > 0) {
            this.clusters.forEach(cluster => cluster.clearMarkers());
            this.clusters = [];
        }
    }
    
    enableClustering() {
        if (typeof MarkerClusterer === 'undefined') {
            console.warn('MarkerClusterer not loaded');
            return;
        }
        
        const clusterer = new MarkerClusterer(this.map, this.markers, {
            imagePath: '/static/images/m',
            maxZoom: 15,
            gridSize: 50,
            styles: this.getClusterStyles()
        });
        
        this.clusters.push(clusterer);
    }
    
    getClusterStyles() {
        return [
            {
                textColor: 'white',
                url: '/static/images/cluster-1.png',
                height: 50,
                width: 50
            },
            {
                textColor: 'white',
                url: '/static/images/cluster-2.png',
                height: 60,
                width: 60
            },
            {
                textColor: 'white',
                url: '/static/images/cluster-3.png',
                height: 70,
                width: 70
            }
        ];
    }
    
    toggleClustering() {
        this.isClusteringEnabled = !this.isClusteringEnabled;
        
        if (this.isClusteringEnabled) {
            this.enableClustering();
        } else {
            this.clusters.forEach(cluster => cluster.clearMarkers());
            this.clusters = [];
        }
        
        this.updateClusteringButton();
    }
    
    toggleHeatmap() {
        this.isHeatmapEnabled = !this.isHeatmapEnabled;
        
        if (this.isHeatmapEnabled) {
            this.enableHeatmap();
        } else {
            this.disableHeatmap();
        }
        
        this.updateHeatmapButton();
    }
    
    enableHeatmap() {
        if (!this.map || typeof google.maps.visualization === 'undefined') {
            return;
        }
        
        const heatmapData = this.markers.map(marker => ({
            location: marker.getPosition(),
            weight: 1
        }));
        
        this.heatmap = new google.maps.visualization.HeatmapLayer({
            data: heatmapData,
            map: this.map,
            radius: 50,
            opacity: 0.6
        });
    }
    
    disableHeatmap() {
        if (this.heatmap) {
            this.heatmap.setMap(null);
            this.heatmap = null;
        }
    }
    
    searchLocation() {
        const query = document.getElementById('location-search').value;
        if (!query) return;
        
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ address: query }, (results, status) => {
            if (status === 'OK') {
                this.map.setCenter(results[0].geometry.location);
                this.map.setZoom(12);
                this.searchJobsInArea(results[0].geometry.location, 25);
            } else {
                this.showNotification('Localisation non trouvée', 'error');
            }
        });
    }
    
    searchJobsInArea(center, radius) {
        const bounds = this.map.getBounds();
        if (!bounds) return;
        
        // Filtrer les marqueurs dans la zone
        const visibleMarkers = this.markers.filter(marker => {
            return bounds.contains(marker.getPosition());
        });
        
        this.updateResultsCount(visibleMarkers.length);
    }
    
    applyFilters() {
        const formData = new FormData(document.getElementById('filters-form'));
        this.currentFilters = Object.fromEntries(formData.entries());
        
        // Recharger les données avec les filtres
        this.loadFilteredData();
    }
    
    loadFilteredData() {
        const params = new URLSearchParams(this.currentFilters);
        
        fetch(`/maps/jobs-in-radius/?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                if (data.results) {
                    this.loadMapData(data.results);
                }
            })
            .catch(error => {
                console.error('Error loading filtered data:', error);
                this.showNotification('Erreur lors du chargement des données', 'error');
            });
    }
    
    saveCurrentView() {
        if (!this.map) return;
        
        const center = this.map.getCenter();
        const zoom = this.map.getZoom();
        
        // Sauvegarder dans le localStorage
        localStorage.setItem('mapView', JSON.stringify({
            center: { lat: center.lat(), lng: center.lng() },
            zoom: zoom,
            timestamp: Date.now()
        }));
    }
    
    loadSavedView() {
        const savedView = localStorage.getItem('mapView');
        if (savedView) {
            try {
                const view = JSON.parse(savedView);
                // Vérifier que la vue n'est pas trop ancienne (24h)
                if (Date.now() - view.timestamp < 24 * 60 * 60 * 1000) {
                    this.map.setCenter(view.center);
                    this.map.setZoom(view.zoom);
                }
            } catch (e) {
                console.error('Error loading saved view:', e);
            }
        }
    }
    
    saveBookmark() {
        if (!this.map) return;
        
        const center = this.map.getCenter();
        const zoom = this.map.getZoom();
        
        // Remplir le formulaire de signet
        document.getElementById('bookmark-lat').value = center.lat();
        document.getElementById('bookmark-lng').value = center.lng();
        document.getElementById('bookmark-zoom').value = zoom;
        document.getElementById('bookmark-filters').value = JSON.stringify(this.currentFilters);
        
        $('#bookmarkModal').modal('show');
    }
    
    createBookmark() {
        const formData = new FormData(document.getElementById('bookmark-form'));
        
        fetch('/maps/create-bookmark/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $('#bookmarkModal').modal('hide');
                this.showNotification('Signet créé avec succès', 'success');
            } else {
                this.showNotification('Erreur lors de la création du signet', 'error');
            }
        })
        .catch(error => {
            console.error('Error creating bookmark:', error);
            this.showNotification('Erreur lors de la création du signet', 'error');
        });
    }
    
    updateResultsCount(count = null) {
        const counter = document.getElementById('results-count');
        if (!counter) return;
        
        if (count === null) {
            const visibleMarkers = this.markers.filter(marker => {
                return this.map.getBounds().contains(marker.getPosition());
            });
            count = visibleMarkers.length;
        }
        
        counter.textContent = count;
    }
    
    loadUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const lat = urlParams.get('lat');
        const lng = urlParams.get('lng');
        const zoom = urlParams.get('zoom');
        
        if (lat && lng && this.map) {
            this.map.setCenter({ lat: parseFloat(lat), lng: parseFloat(lng) });
            if (zoom) {
                this.map.setZoom(parseInt(zoom));
            }
        }
    }
    
    resetMapView() {
        if (!this.map) return;
        
        this.map.setCenter({ lat: 46.603354, lng: 1.888334 });
        this.map.setZoom(6);
    }
    
    showFilters() {
        document.getElementById('filters-panel').style.display = 'block';
    }
    
    hideFilters() {
        document.getElementById('filters-panel').style.display = 'none';
    }
    
    showInfoPanel() {
        document.getElementById('info-panel').style.display = 'block';
    }
    
    hideInfoPanel() {
        document.getElementById('info-panel').style.display = 'none';
    }
    
    updateClusteringButton() {
        const btn = document.querySelector('[onclick="toggleClustering()"]');
        if (btn) {
            btn.classList.toggle('active', this.isClusteringEnabled);
        }
    }
    
    updateHeatmapButton() {
        const btn = document.querySelector('[onclick="toggleHeatmap()"]');
        if (btn) {
            btn.classList.toggle('active', this.isHeatmapEnabled);
        }
    }
    
    // Fonctions utilitaires
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR');
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    showNotification(message, type = 'info') {
        const alertClass = type === 'error' ? 'danger' : type;
        const icon = type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle';
        
        const notification = $(`
            <div class="alert alert-${alertClass} alert-dismissible fade show notification-toast">
                <i class="fas fa-${icon}"></i>
                ${message}
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
            </div>
        `);
        
        $('body').append(notification);
        
        setTimeout(() => {
            notification.alert('close');
        }, 5000);
    }
}

// Fonctions globales pour les templates
function initDashboardMap() {
    if (typeof google === 'undefined') {
        console.error('Google Maps API not loaded');
        return;
    }
    
    const mapElement = document.getElementById('dashboard-map');
    if (!mapElement) return;
    
    const map = new google.maps.Map(mapElement, {
        zoom: 6,
        center: { lat: 46.603354, lng: 1.888334 },
        mapTypeId: 'roadmap',
        styles: [
            {
                featureType: 'poi',
                elementType: 'labels',
                stylers: [{ visibility: 'off' }]
            }
        ]
    });
    
    // Ajouter quelques marqueurs d'exemple
    const locations = [
        { lat: 48.8566, lng: 2.3522, title: 'Paris' },
        { lat: 45.7640, lng: 4.8357, title: 'Lyon' },
        { lat: 43.2965, lng: 5.3698, title: 'Marseille' },
        { lat: 43.6047, lng: 1.4442, title: 'Toulouse' },
        { lat: 44.8378, lng: -0.5792, title: 'Bordeaux' }
    ];
    
    locations.forEach(location => {
        new google.maps.Marker({
            position: location,
            map: map,
            title: location.title,
            icon: {
                url: '/static/images/map-marker.png',
                scaledSize: new google.maps.Size(30, 30)
            }
        });
    });
}

function initInteractiveMap() {
    window.mapsSystem = new MapsSystem();
}

function searchLocation() {
    if (window.mapsSystem) {
        window.mapsSystem.searchLocation();
    }
}

function resetMapView() {
    if (window.mapsSystem) {
        window.mapsSystem.resetMapView();
    }
}

function toggleClustering() {
    if (window.mapsSystem) {
        window.mapsSystem.toggleClustering();
    }
}

function toggleHeatmap() {
    if (window.mapsSystem) {
        window.mapsSystem.toggleHeatmap();
    }
}

function showFilters() {
    if (window.mapsSystem) {
        window.mapsSystem.showFilters();
    }
}

function hideFilters() {
    if (window.mapsSystem) {
        window.mapsSystem.hideFilters();
    }
}

function saveBookmark() {
    if (window.mapsSystem) {
        window.mapsSystem.saveBookmark();
    }
}

function createBookmark() {
    if (window.mapsSystem) {
        window.mapsSystem.createBookmark();
    }
}

function applyFilters() {
    if (window.mapsSystem) {
        window.mapsSystem.applyFilters();
    }
}

function clearFilters() {
    document.getElementById('filters-form').reset();
    if (window.mapsSystem) {
        window.mapsSystem.currentFilters = {};
        window.mapsSystem.loadMapData(window.mapsSystem.originalData || []);
    }
}

// Initialiser le système de cartes
$(document).ready(function() {
    // Attendre que Google Maps soit chargé
    if (typeof google !== 'undefined') {
        initInteractiveMap();
    } else {
        // Attendre le chargement de Google Maps
        window.addEventListener('load', () => {
            if (typeof google !== 'undefined') {
                initInteractiveMap();
            }
        });
    }
});
