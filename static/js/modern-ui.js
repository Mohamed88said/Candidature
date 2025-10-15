/**
 * Modern UI JavaScript
 * Professional interactions and animations
 */

(function() {
    'use strict';

    // ========================================
    // UTILITY FUNCTIONS
    // ========================================

    const utils = {
        // Debounce function
        debounce: function(func, wait, immediate) {
            let timeout;
            return function executedFunction() {
                const context = this;
                const args = arguments;
                const later = function() {
                    timeout = null;
                    if (!immediate) func.apply(context, args);
                };
                const callNow = immediate && !timeout;
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
                if (callNow) func.apply(context, args);
            };
        },

        // Throttle function
        throttle: function(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },

        // Check if element is in viewport
        isInViewport: function(element) {
            const rect = element.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        },

        // Smooth scroll to element
        smoothScrollTo: function(element, offset = 0) {
            const targetPosition = element.offsetTop - offset;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        },

        // Format number with commas
        formatNumber: function(num) {
            return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        },

        // Get random number between min and max
        randomBetween: function(min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
        }
    };

    // ========================================
    // LOADING SPINNER
    // ========================================

    const LoadingSpinner = {
        show: function() {
            const spinner = document.getElementById('loading-spinner');
            if (spinner) {
                spinner.style.display = 'flex';
                document.body.style.overflow = 'hidden';
            }
        },

        hide: function() {
            const spinner = document.getElementById('loading-spinner');
            if (spinner) {
                spinner.style.display = 'none';
                document.body.style.overflow = '';
            }
        }
    };

    // ========================================
    // NAVIGATION
    // ========================================

    const Navigation = {
        init: function() {
            this.initMobileMenu();
            this.initUserDropdown();
            this.initNotificationDropdown();
            this.initScrollBehavior();
        },

        initMobileMenu: function() {
            const toggle = document.getElementById('mobile-menu-toggle');
            const close = document.getElementById('mobile-nav-close');
            const nav = document.getElementById('mobile-nav');
            const overlay = document.createElement('div');
            overlay.className = 'mobile-nav-overlay';
            document.body.appendChild(overlay);

            if (toggle && nav) {
                toggle.addEventListener('click', () => {
                    nav.classList.add('active');
                    overlay.classList.add('active');
                    document.body.style.overflow = 'hidden';
                });

                close.addEventListener('click', () => {
                    nav.classList.remove('active');
                    overlay.classList.remove('active');
                    document.body.style.overflow = '';
                });

                overlay.addEventListener('click', () => {
                    nav.classList.remove('active');
                    overlay.classList.remove('active');
                    document.body.style.overflow = '';
                });
            }
        },

        initUserDropdown: function() {
            const userBtn = document.getElementById('user-btn');
            const userMenu = document.getElementById('user-menu');

            if (userBtn && userMenu) {
                userBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    userMenu.classList.toggle('active');
                });

                document.addEventListener('click', () => {
                    userMenu.classList.remove('active');
                });
            }
        },

        initNotificationDropdown: function() {
            const notificationBtn = document.getElementById('notification-btn');
            const notificationMenu = document.getElementById('notification-menu');

            if (notificationBtn && notificationMenu) {
                notificationBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    notificationMenu.classList.toggle('active');
                });

                document.addEventListener('click', () => {
                    notificationMenu.classList.remove('active');
                });
            }
        },

        initScrollBehavior: function() {
            let lastScrollTop = 0;
            const navbar = document.querySelector('.navbar');

            if (navbar) {
                window.addEventListener('scroll', utils.throttle(() => {
                    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                    
                    if (scrollTop > lastScrollTop && scrollTop > 100) {
                        // Scrolling down
                        navbar.classList.add('navbar-hidden');
                    } else {
                        // Scrolling up
                        navbar.classList.remove('navbar-hidden');
                    }
                    
                    lastScrollTop = scrollTop;
                }, 100));
            }
        }
    };

    // ========================================
    // ANIMATIONS
    // ========================================

    const Animations = {
        init: function() {
            this.initScrollAnimations();
            this.initHoverEffects();
            this.initLoadingAnimations();
        },

        initScrollAnimations: function() {
            const animatedElements = document.querySelectorAll('[data-animate]');
            
            if (animatedElements.length > 0) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const element = entry.target;
                            const animationType = element.dataset.animate;
                            element.classList.add(`animate-${animationType}`);
                            observer.unobserve(element);
                        }
                    });
                }, {
                    threshold: 0.1,
                    rootMargin: '0px 0px -50px 0px'
                });

                animatedElements.forEach(element => {
                    observer.observe(element);
                });
            }
        },

        initHoverEffects: function() {
            // Card hover effects
            const cards = document.querySelectorAll('.card');
            cards.forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-5px)';
                    this.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)';
                });

                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                    this.style.boxShadow = '';
                });
            });

            // Button hover effects
            const buttons = document.querySelectorAll('.btn');
            buttons.forEach(button => {
                button.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-1px)';
                });

                button.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                });
            });
        },

        initLoadingAnimations: function() {
            // Stagger animation for lists
            const lists = document.querySelectorAll('.stagger-animation');
            lists.forEach(list => {
                const items = list.querySelectorAll('.stagger-item');
                items.forEach((item, index) => {
                    item.style.animationDelay = `${index * 0.1}s`;
                });
            });
        }
    };

    // ========================================
    // NOTIFICATIONS
    // ========================================

    const Notifications = {
        init: function() {
            this.loadNotifications();
            this.initRealTimeUpdates();
        },

        loadNotifications: function() {
            // Load recent notifications via AJAX
            fetch('/api/notifications/recent/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.updateNotificationList(data.notifications);
                    this.updateNotificationCount(data.unread_count);
                }
            })
            .catch(error => {
                console.error('Error loading notifications:', error);
            });
        },

        updateNotificationList: function(notifications) {
            const list = document.getElementById('notification-list');
            if (!list) return;

            if (notifications.length === 0) {
                list.innerHTML = `
                    <div class="notification-empty">
                        <i class="fas fa-bell-slash"></i>
                        <p>Aucune notification</p>
                    </div>
                `;
                return;
            }

            list.innerHTML = notifications.map(notification => `
                <div class="notification-item ${notification.is_read ? 'read' : 'unread'}">
                    <div class="notification-icon">
                        <i class="${this.getNotificationIcon(notification.type)}"></i>
                    </div>
                    <div class="notification-content">
                        <h5>${notification.title}</h5>
                        <p>${notification.message}</p>
                        <span class="notification-time">${notification.time_ago}</span>
                    </div>
                </div>
            `).join('');
        },

        updateNotificationCount: function(count) {
            const badge = document.getElementById('notification-count');
            if (badge) {
                if (count > 0) {
                    badge.textContent = count;
                    badge.style.display = 'block';
                } else {
                    badge.style.display = 'none';
                }
            }
        },

        getNotificationIcon: function(type) {
            const icons = {
                'job_alert': 'fas fa-briefcase',
                'application_update': 'fas fa-file-alt',
                'message_received': 'fas fa-comment',
                'achievement': 'fas fa-trophy',
                'badge_earned': 'fas fa-medal',
                'level_up': 'fas fa-arrow-up',
                'default': 'fas fa-bell'
            };
            return icons[type] || icons.default;
        },

        initRealTimeUpdates: function() {
            // WebSocket connection for real-time notifications
            if (window.WebSocket) {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const ws = new WebSocket(`${protocol}//${window.location.host}/ws/notifications/`);
                
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    if (data.type === 'notification') {
                        this.showToastNotification(data.notification);
                        this.loadNotifications(); // Reload notifications
                    }
                };

                ws.onclose = () => {
                    // Reconnect after 5 seconds
                    setTimeout(() => {
                        this.initRealTimeUpdates();
                    }, 5000);
                };
            }
        },

        showToastNotification: function(notification) {
            const toast = document.createElement('div');
            toast.className = 'toast-notification';
            toast.innerHTML = `
                <div class="toast-content">
                    <div class="toast-icon">
                        <i class="${this.getNotificationIcon(notification.type)}"></i>
                    </div>
                    <div class="toast-text">
                        <h5>${notification.title}</h5>
                        <p>${notification.message}</p>
                    </div>
                    <button class="toast-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;

            document.body.appendChild(toast);

            // Show toast
            setTimeout(() => {
                toast.classList.add('show');
            }, 100);

            // Auto hide after 5 seconds
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => {
                    document.body.removeChild(toast);
                }, 300);
            }, 5000);

            // Close button
            toast.querySelector('.toast-close').addEventListener('click', () => {
                toast.classList.remove('show');
                setTimeout(() => {
                    document.body.removeChild(toast);
                }, 300);
            });
        }
    };

    // ========================================
    // SEARCH
    // ========================================

    const Search = {
        init: function() {
            this.initGlobalSearch();
            this.initSearchSuggestions();
        },

        initGlobalSearch: function() {
            const searchInput = document.getElementById('global-search');
            if (searchInput) {
                searchInput.addEventListener('input', utils.debounce((e) => {
                    const query = e.target.value.trim();
                    if (query.length >= 2) {
                        this.performSearch(query);
                    }
                }, 300));
            }
        },

        performSearch: function(query) {
            // Implement global search functionality
            console.log('Searching for:', query);
        },

        initSearchSuggestions: function() {
            // Implement search suggestions
        }
    };

    // ========================================
    // BACK TO TOP
    // ========================================

    const BackToTop = {
        init: function() {
            const button = document.getElementById('back-to-top');
            if (button) {
                window.addEventListener('scroll', utils.throttle(() => {
                    if (window.pageYOffset > 300) {
                        button.classList.add('show');
                    } else {
                        button.classList.remove('show');
                    }
                }, 100));

                button.addEventListener('click', () => {
                    window.scrollTo({
                        top: 0,
                        behavior: 'smooth'
                    });
                });
            }
        }
    };

    // ========================================
    // FORM ENHANCEMENTS
    // ========================================

    const FormEnhancements = {
        init: function() {
            this.initFormValidation();
            this.initFileUploads();
            this.initAutoSave();
        },

        initFormValidation: function() {
            const forms = document.querySelectorAll('form[data-validate]');
            forms.forEach(form => {
                form.addEventListener('submit', (e) => {
                    if (!this.validateForm(form)) {
                        e.preventDefault();
                    }
                });
            });
        },

        validateForm: function(form) {
            let isValid = true;
            const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    this.showFieldError(input, 'Ce champ est requis');
                    isValid = false;
                } else {
                    this.clearFieldError(input);
                }
            });

            return isValid;
        },

        showFieldError: function(field, message) {
            this.clearFieldError(field);
            field.classList.add('is-invalid');
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = message;
            field.parentNode.appendChild(errorDiv);
        },

        clearFieldError: function(field) {
            field.classList.remove('is-invalid');
            const errorDiv = field.parentNode.querySelector('.invalid-feedback');
            if (errorDiv) {
                errorDiv.remove();
            }
        },

        initFileUploads: function() {
            const fileInputs = document.querySelectorAll('input[type="file"]');
            fileInputs.forEach(input => {
                input.addEventListener('change', (e) => {
                    const files = e.target.files;
                    if (files.length > 0) {
                        this.previewFiles(files, input);
                    }
                });
            });
        },

        previewFiles: function(files, input) {
            // Implement file preview functionality
        },

        initAutoSave: function() {
            const autoSaveForms = document.querySelectorAll('form[data-autosave]');
            autoSaveForms.forEach(form => {
                const inputs = form.querySelectorAll('input, select, textarea');
                inputs.forEach(input => {
                    input.addEventListener('input', utils.debounce(() => {
                        this.autoSaveForm(form);
                    }, 2000));
                });
            });
        },

        autoSaveForm: function(form) {
            const formData = new FormData(form);
            const url = form.dataset.autosaveUrl;
            
            if (url) {
                fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.showAutoSaveIndicator();
                    }
                })
                .catch(error => {
                    console.error('Auto-save error:', error);
                });
            }
        },

        showAutoSaveIndicator: function() {
            const indicator = document.createElement('div');
            indicator.className = 'autosave-indicator';
            indicator.innerHTML = '<i class="fas fa-check"></i> Sauvegardé automatiquement';
            document.body.appendChild(indicator);

            setTimeout(() => {
                indicator.classList.add('show');
            }, 100);

            setTimeout(() => {
                indicator.classList.remove('show');
                setTimeout(() => {
                    document.body.removeChild(indicator);
                }, 300);
            }, 2000);
        }
    };

    // ========================================
    // INITIALIZATION
    // ========================================

    document.addEventListener('DOMContentLoaded', function() {
        // Hide loading spinner
        LoadingSpinner.hide();

        // Initialize all modules
        Navigation.init();
        Animations.init();
        Notifications.init();
        Search.init();
        BackToTop.init();
        FormEnhancements.init();

        // Add loaded class to body
        document.body.classList.add('loaded');

        // Initialize any page-specific functionality
        if (window.pageInit) {
            window.pageInit();
        }
    });

    // ========================================
    // GLOBAL ERROR HANDLING
    // ========================================

    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        // You could send error reports to your server here
    });

    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        // You could send error reports to your server here
    });

    // ========================================
    // EXPOSE UTILITIES
    // ========================================

    window.ModernUI = {
        utils: utils,
        LoadingSpinner: LoadingSpinner,
        Navigation: Navigation,
        Animations: Animations,
        Notifications: Notifications,
        Search: Search,
        BackToTop: BackToTop,
        FormEnhancements: FormEnhancements
    };

})();


