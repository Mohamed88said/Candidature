// Alerts System JavaScript

class AlertsSystem {
    constructor() {
        this.unreadCount = 0;
        this.refreshInterval = null;
        this.notificationPermission = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.requestNotificationPermission();
        this.startAutoRefresh();
        this.loadUnreadCount();
    }
    
    setupEventListeners() {
        // Gestion des clics sur les alertes
        $(document).on('click', '.alert-item', (e) => {
            if (!$(e.target).closest('.alert-actions, .alert-checkbox').length) {
                const alertId = $(e.currentTarget).data('alert-id');
                this.openAlert(alertId);
            }
        });
        
        // Gestion des actions sur les alertes
        $(document).on('click', '.mark-as-read', (e) => {
            e.preventDefault();
            const alertId = $(e.currentTarget).data('alert-id');
            this.markAsRead(alertId);
        });
        
        $(document).on('click', '.mark-as-clicked', (e) => {
            e.preventDefault();
            const alertId = $(e.currentTarget).data('alert-id');
            this.markAsClicked(alertId);
        });
        
        // Gestion des commentaires
        $(document).on('submit', '.feedback-form', (e) => {
            e.preventDefault();
            this.submitFeedback(e.target);
        });
        
        // Gestion des étoiles de notation
        $(document).on('click', '.rating-star', (e) => {
            this.setRating($(e.currentTarget));
        });
        
        // Gestion des filtres en temps réel
        $(document).on('change', '.filters-form input, .filters-form select', (e) => {
            this.debounce(() => {
                this.applyFilters();
            }, 500)();
        });
        
        // Gestion de la sélection multiple
        $(document).on('change', '.alert-select', (e) => {
            this.updateSelectionState();
        });
        
        // Gestion des actions en lot
        $(document).on('click', '.bulk-action-btn', (e) => {
            e.preventDefault();
            this.showBulkActionModal();
        });
    }
    
    requestNotificationPermission() {
        if ('Notification' in window) {
            Notification.requestPermission().then(permission => {
                this.notificationPermission = permission;
            });
        }
    }
    
    startAutoRefresh() {
        // Actualiser les alertes toutes les 60 secondes
        this.refreshInterval = setInterval(() => {
            this.loadUnreadCount();
            this.checkNewAlerts();
        }, 60000);
    }
    
    loadUnreadCount() {
        $.get('/alerts/api/unread-count/', (data) => {
            this.unreadCount = data.unread_count;
            this.updateUnreadBadge();
        }).fail(() => {
            console.log('Erreur lors du chargement du nombre d\'alertes non lues');
        });
    }
    
    updateUnreadBadge() {
        const badge = $('.unread-badge');
        if (this.unreadCount > 0) {
            badge.text(this.unreadCount).show();
        } else {
            badge.hide();
        }
    }
    
    checkNewAlerts() {
        $.get('/alerts/api/check-new/', (data) => {
            if (data.new_alerts && data.new_alerts.length > 0) {
                this.showNewAlertsNotification(data.new_alerts);
                this.loadUnreadCount();
            }
        });
    }
    
    showNewAlertsNotification(alerts) {
        if (this.notificationPermission === 'granted') {
            alerts.forEach(alert => {
                new Notification(alert.title, {
                    body: alert.message,
                    icon: '/static/images/logo.png',
                    tag: `alert-${alert.id}`
                });
            });
        } else {
            // Fallback : notification dans la page
            this.showInPageNotification(`${alerts.length} nouvelle(s) alerte(s) reçue(s)`);
        }
    }
    
    showInPageNotification(message) {
        const notification = $(`
            <div class="alert alert-info alert-dismissible fade show notification-toast">
                <i class="fas fa-bell"></i>
                ${message}
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
            </div>
        `);
        
        $('body').append(notification);
        
        // Positionner la notification
        notification.css({
            position: 'fixed',
            top: '20px',
            right: '20px',
            zIndex: 9999,
            minWidth: '300px'
        });
        
        // Supprimer automatiquement après 5 secondes
        setTimeout(() => {
            notification.alert('close');
        }, 5000);
    }
    
    openAlert(alertId) {
        // Marquer comme ouverte
        this.markAsRead(alertId);
        
        // Rediriger vers la page de détail
        window.location.href = `/alerts/alert/${alertId}/`;
    }
    
    markAsRead(alertId) {
        $.post(`/alerts/alert/${alertId}/mark-read/`, {
            'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
        }, (data) => {
            if (data.success) {
                const alertItem = $(`.alert-item[data-alert-id="${alertId}"]`);
                alertItem.removeClass('unread');
                alertItem.find('.status-badge').text('Lue').removeClass('unread').addClass('read');
                
                // Mettre à jour le compteur
                this.unreadCount = Math.max(0, this.unreadCount - 1);
                this.updateUnreadBadge();
            }
        });
    }
    
    markAsClicked(alertId) {
        $.post(`/alerts/alert/${alertId}/mark-clicked/`, {
            'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
        }, (data) => {
            if (data.success) {
                const alertItem = $(`.alert-item[data-alert-id="${alertId}"]`);
                alertItem.find('.status-badge').text('Cliquée').removeClass('read').addClass('clicked');
            }
        });
    }
    
    submitFeedback(form) {
        const formData = new FormData(form);
        
        $.ajax({
            url: form.action,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: (data) => {
                if (data.success) {
                    this.showSuccess('Merci pour vos commentaires !');
                    $(form).find('input, textarea').val('');
                    $(form).find('.rating-star').removeClass('active');
                } else {
                    this.showError('Erreur lors de l\'envoi des commentaires.');
                }
            },
            error: () => {
                this.showError('Erreur lors de l\'envoi des commentaires.');
            }
        });
    }
    
    setRating(starElement) {
        const rating = starElement.data('rating');
        const container = starElement.closest('.rating-stars');
        
        // Mettre à jour l'affichage des étoiles
        container.find('.rating-star').each(function(index) {
            if (index < rating) {
                $(this).addClass('active');
            } else {
                $(this).removeClass('active');
            }
        });
        
        // Mettre à jour la valeur cachée
        container.find('input[name="rating"]').val(rating);
    }
    
    applyFilters() {
        const form = $('.filters-form');
        const formData = form.serialize();
        
        // Mettre à jour l'URL sans recharger la page
        const url = new URL(window.location);
        const params = new URLSearchParams(formData);
        
        // Effacer les paramètres existants
        url.search = '';
        
        // Ajouter les nouveaux paramètres
        params.forEach((value, key) => {
            if (value) {
                url.searchParams.set(key, value);
            }
        });
        
        // Recharger la page avec les nouveaux filtres
        window.location.href = url.toString();
    }
    
    updateSelectionState() {
        const selectedCount = $('.alert-select:checked').length;
        const totalCount = $('.alert-select').length;
        
        if (selectedCount === 0) {
            $('.alert-item').removeClass('selected');
        } else if (selectedCount === totalCount) {
            $('.alert-item').addClass('selected');
        } else {
            $('.alert-select:checked').closest('.alert-item').addClass('selected');
            $('.alert-select:not(:checked)').closest('.alert-item').removeClass('selected');
        }
        
        // Mettre à jour le bouton d'action en lot
        const bulkBtn = $('.bulk-action-btn');
        if (selectedCount > 0) {
            bulkBtn.prop('disabled', false).text(`Actions (${selectedCount})`);
        } else {
            bulkBtn.prop('disabled', true).text('Actions en lot');
        }
    }
    
    showBulkActionModal() {
        const selectedIds = $('.alert-select:checked').map(function() {
            return this.value;
        }).get();
        
        if (selectedIds.length === 0) {
            this.showWarning('Veuillez sélectionner au moins une alerte.');
            return;
        }
        
        $('#selectedAlertIds').val(selectedIds.join(','));
        $('#bulkActionModal').modal('show');
    }
    
    submitBulkAction() {
        const form = $('#bulkActionForm');
        const formData = form.serialize();
        
        $.ajax({
            url: '/alerts/bulk-action/',
            type: 'POST',
            data: formData,
            success: (data) => {
                if (data.success) {
                    $('#bulkActionModal').modal('hide');
                    location.reload();
                } else {
                    this.showError('Erreur lors de l\'exécution de l\'action.');
                }
            },
            error: () => {
                this.showError('Erreur lors de l\'exécution de l\'action.');
            }
        });
    }
    
    // Fonctions utilitaires
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
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showWarning(message) {
        this.showNotification(message, 'warning');
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
        
        // Positionner la notification
        notification.css({
            position: 'fixed',
            top: '20px',
            right: '20px',
            zIndex: 9999,
            minWidth: '300px'
        });
        
        // Supprimer automatiquement après 5 secondes
        setTimeout(() => {
            notification.alert('close');
        }, 5000);
    }
    
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// Initialiser le système d'alertes
let alertsSystem;
$(document).ready(function() {
    alertsSystem = new AlertsSystem();
    
    // Nettoyer lors de la fermeture de la page
    $(window).on('beforeunload', function() {
        if (alertsSystem) {
            alertsSystem.destroy();
        }
    });
});

// Fonctions globales pour les templates
function selectAllAlerts() {
    const checkboxes = $('.alert-select');
    const allChecked = checkboxes.length === checkboxes.filter(':checked').length;
    
    checkboxes.prop('checked', !allChecked);
    alertsSystem.updateSelectionState();
}

function bulkAction() {
    alertsSystem.showBulkActionModal();
}

function submitBulkAction() {
    alertsSystem.submitBulkAction();
}

function markAsRead(alertId) {
    alertsSystem.markAsRead(alertId);
}

function markAsClicked(alertId) {
    alertsSystem.markAsClicked(alertId);
}

function deleteAlert(alertId) {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette alerte ?')) {
        $.post(`/alerts/alert/${alertId}/delete/`, {
            'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
        }, (data) => {
            if (data.success) {
                $(`.alert-item[data-alert-id="${alertId}"]`).fadeOut();
            } else {
                alertsSystem.showError('Erreur lors de la suppression de l\'alerte.');
            }
        });
    }
}

function setRating(rating) {
    const stars = $('.rating-star');
    stars.removeClass('active');
    
    for (let i = 0; i < rating; i++) {
        stars.eq(i).addClass('active');
    }
    
    $('input[name="rating"]').val(rating);
}

// Styles CSS pour les notifications
const notificationStyles = `
    .notification-toast {
        animation: slideInRight 0.3s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .rating-star {
        cursor: pointer;
        transition: color 0.2s;
    }
    
    .rating-star:hover,
    .rating-star.active {
        color: #ffc107;
    }
    
    .alert-item {
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .alert-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .alert-item.selected {
        background-color: #e3f2fd;
        border-color: #2196f3;
    }
    
    .unread-badge {
        position: absolute;
        top: -5px;
        right: -5px;
        background: #dc3545;
        color: white;
        border-radius: 50%;
        width: 18px;
        height: 18px;
        font-size: 0.7rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
`;

// Ajouter les styles au document
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

