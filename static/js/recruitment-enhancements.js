/**
 * Recruitment Platform JavaScript Enhancements
 * Provides interactive features and improved user experience
 */

(function() {
    'use strict';

    // =============================================================================
    // UTILITY FUNCTIONS
    // =============================================================================

    /**
     * Debounce function to limit the rate of function execution
     */
    function debounce(func, wait, immediate) {
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
    }

    /**
     * Throttle function to limit the rate of function execution
     */
    function throttle(func, limit) {
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
    }

    /**
     * Smooth scroll to element
     */
    function smoothScrollTo(element, offset = 0) {
        const targetPosition = element.offsetTop - offset;
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }

    /**
     * Check if element is in viewport
     */
    function isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    // =============================================================================
    // NAVIGATION ENHANCEMENTS
    // =============================================================================

    /**
     * Enhanced navigation functionality
     */
    function initNavigation() {
        const navbar = document.querySelector('.navbar');
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');

        // Add scroll effect to navbar
        if (navbar) {
            let lastScrollTop = 0;
            const scrollHandler = throttle(() => {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                
                if (scrollTop > 100) {
                    navbar.classList.add('navbar-scrolled');
                } else {
                    navbar.classList.remove('navbar-scrolled');
                }

                // Hide/show navbar on scroll
                if (scrollTop > lastScrollTop && scrollTop > 200) {
                    navbar.style.transform = 'translateY(-100%)';
                } else {
                    navbar.style.transform = 'translateY(0)';
                }
                lastScrollTop = scrollTop;
            }, 100);

            window.addEventListener('scroll', scrollHandler);
        }

        // Smooth scroll for navigation links
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href && href.startsWith('#')) {
                    e.preventDefault();
                    const target = document.querySelector(href);
                    if (target) {
                        smoothScrollTo(target, 80);
                    }
                }
            });
        });

        // Close mobile menu when clicking outside
        if (navbarToggler && navbarCollapse) {
            document.addEventListener('click', function(e) {
                if (!navbar.contains(e.target) && navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            });
        }
    }

    // =============================================================================
    // FORM ENHANCEMENTS
    // =============================================================================

    /**
     * Enhanced form functionality
     */
    function initForms() {
        const forms = document.querySelectorAll('form');
        const fileInputs = document.querySelectorAll('input[type="file"]');
        const textareas = document.querySelectorAll('textarea');

        // Form validation
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });

        // File input enhancements
        fileInputs.forEach(input => {
            input.addEventListener('change', function() {
                const files = this.files;
                const label = this.nextElementSibling;
                
                if (files.length > 0) {
                    if (label && label.classList.contains('form-label')) {
                        label.textContent = `${files.length} fichier(s) sélectionné(s)`;
                    }
                }
            });
        });

        // Auto-resize textareas
        textareas.forEach(textarea => {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });
        });

        // Real-time form validation
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', debounce(function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            }, 300));
        });
    }

    /**
     * Validate individual form field
     */
    function validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');
        let isValid = true;
        let message = '';

        // Required field validation
        if (required && !value) {
            isValid = false;
            message = 'Ce champ est requis.';
        }

        // Email validation
        if (type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                message = 'Veuillez entrer une adresse email valide.';
            }
        }

        // Password validation
        if (type === 'password' && value) {
            if (value.length < 8) {
                isValid = false;
                message = 'Le mot de passe doit contenir au moins 8 caractères.';
            }
        }

        // Phone validation
        if (type === 'tel' && value) {
            const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
            if (!phoneRegex.test(value)) {
                isValid = false;
                message = 'Veuillez entrer un numéro de téléphone valide.';
            }
        }

        // Update field appearance
        field.classList.remove('is-valid', 'is-invalid');
        field.classList.add(isValid ? 'is-valid' : 'is-invalid');

        // Update feedback message
        let feedback = field.parentNode.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            field.parentNode.appendChild(feedback);
        }
        feedback.textContent = message;

        return isValid;
    }

    // =============================================================================
    // CARD ENHANCEMENTS
    // =============================================================================

    /**
     * Enhanced card functionality
     */
    function initCards() {
        const cards = document.querySelectorAll('.card, .job-card, .profile-card, .application-card');

        cards.forEach(card => {
            // Add hover effects
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-4px)';
                this.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)';
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '';
            });

            // Add click effects
            card.addEventListener('mousedown', function() {
                this.style.transform = 'translateY(-2px) scale(0.98)';
            });

            card.addEventListener('mouseup', function() {
                this.style.transform = 'translateY(-4px) scale(1)';
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });
    }

    // =============================================================================
    // BUTTON ENHANCEMENTS
    // =============================================================================

    /**
     * Enhanced button functionality
     */
    function initButtons() {
        const buttons = document.querySelectorAll('.btn');

        buttons.forEach(button => {
            // Add loading state
            button.addEventListener('click', function() {
                if (this.type === 'submit' || this.classList.contains('btn-submit')) {
                    this.classList.add('loading');
                    this.disabled = true;
                    
                    // Add spinner
                    const spinner = document.createElement('span');
                    spinner.className = 'spinner-border spinner-border-sm me-2';
                    spinner.setAttribute('role', 'status');
                    spinner.setAttribute('aria-hidden', 'true');
                    
                    this.insertBefore(spinner, this.firstChild);
                    
                    // Remove loading state after 3 seconds (fallback)
                    setTimeout(() => {
                        this.classList.remove('loading');
                        this.disabled = false;
                        const spinner = this.querySelector('.spinner-border');
                        if (spinner) {
                            spinner.remove();
                        }
                    }, 3000);
                }
            });

            // Add ripple effect
            button.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                ripple.classList.add('ripple');
                
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
    }

    // =============================================================================
    // SEARCH ENHANCEMENTS
    // =============================================================================

    /**
     * Enhanced search functionality
     */
    function initSearch() {
        const searchInputs = document.querySelectorAll('input[type="search"], .search-input');
        const searchForms = document.querySelectorAll('.search-form');

        searchInputs.forEach(input => {
            // Add search suggestions
            input.addEventListener('input', debounce(function() {
                const query = this.value.trim();
                if (query.length >= 2) {
                    showSearchSuggestions(this, query);
                } else {
                    hideSearchSuggestions(this);
                }
            }, 300));

            // Handle keyboard navigation
            input.addEventListener('keydown', function(e) {
                const suggestions = this.parentNode.querySelector('.search-suggestions');
                if (suggestions && suggestions.style.display !== 'none') {
                    const items = suggestions.querySelectorAll('.suggestion-item');
                    const activeItem = suggestions.querySelector('.suggestion-item.active');
                    let activeIndex = -1;

                    if (activeItem) {
                        activeIndex = Array.from(items).indexOf(activeItem);
                    }

                    switch (e.key) {
                        case 'ArrowDown':
                            e.preventDefault();
                            activeIndex = Math.min(activeIndex + 1, items.length - 1);
                            updateActiveSuggestion(items, activeIndex);
                            break;
                        case 'ArrowUp':
                            e.preventDefault();
                            activeIndex = Math.max(activeIndex - 1, -1);
                            updateActiveSuggestion(items, activeIndex);
                            break;
                        case 'Enter':
                            e.preventDefault();
                            if (activeItem) {
                                activeItem.click();
                            }
                            break;
                        case 'Escape':
                            hideSearchSuggestions(this);
                            break;
                    }
                }
            });
        });

        // Close suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.search-container')) {
                hideAllSearchSuggestions();
            }
        });
    }

    /**
     * Show search suggestions
     */
    function showSearchSuggestions(input, query) {
        // This would typically make an AJAX request to get suggestions
        // For now, we'll show a placeholder
        const suggestions = [
            'Développeur Python',
            'Chef de projet',
            'Designer UX/UI',
            'Analyste financier',
            'Marketing digital'
        ].filter(item => item.toLowerCase().includes(query.toLowerCase()));

        let suggestionsContainer = input.parentNode.querySelector('.search-suggestions');
        if (!suggestionsContainer) {
            suggestionsContainer = document.createElement('div');
            suggestionsContainer.className = 'search-suggestions';
            input.parentNode.appendChild(suggestionsContainer);
        }

        suggestionsContainer.innerHTML = suggestions.map(suggestion => 
            `<div class="suggestion-item">${suggestion}</div>`
        ).join('');

        suggestionsContainer.style.display = 'block';

        // Add click handlers
        suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', function() {
                input.value = this.textContent;
                hideSearchSuggestions(input);
                input.focus();
            });
        });
    }

    /**
     * Hide search suggestions
     */
    function hideSearchSuggestions(input) {
        const suggestions = input.parentNode.querySelector('.search-suggestions');
        if (suggestions) {
            suggestions.style.display = 'none';
        }
    }

    /**
     * Hide all search suggestions
     */
    function hideAllSearchSuggestions() {
        document.querySelectorAll('.search-suggestions').forEach(suggestions => {
            suggestions.style.display = 'none';
        });
    }

    /**
     * Update active suggestion
     */
    function updateActiveSuggestion(items, activeIndex) {
        items.forEach((item, index) => {
            item.classList.toggle('active', index === activeIndex);
        });
    }

    // =============================================================================
    // MODAL ENHANCEMENTS
    // =============================================================================

    /**
     * Enhanced modal functionality
     */
    function initModals() {
        const modals = document.querySelectorAll('.modal');
        const modalTriggers = document.querySelectorAll('[data-bs-toggle="modal"]');

        modals.forEach(modal => {
            // Add animation classes
            modal.addEventListener('show.bs.modal', function() {
                this.classList.add('fade-in');
            });

            modal.addEventListener('hide.bs.modal', function() {
                this.classList.remove('fade-in');
            });

            // Close modal on escape key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && modal.classList.contains('show')) {
                    const modalInstance = bootstrap.Modal.getInstance(modal);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                }
            });
        });
    }

    // =============================================================================
    // TOOLTIP ENHANCEMENTS
    // =============================================================================

    /**
     * Enhanced tooltip functionality
     */
    function initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        
        tooltipElements.forEach(element => {
            new bootstrap.Tooltip(element, {
                trigger: 'hover focus',
                delay: { show: 500, hide: 100 }
            });
        });
    }

    // =============================================================================
    // LAZY LOADING
    // =============================================================================

    /**
     * Lazy loading for images
     */
    function initLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                });
            });

            images.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback for older browsers
            images.forEach(img => {
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                img.classList.add('loaded');
            });
        }
    }

    // =============================================================================
    // SCROLL ANIMATIONS
    // =============================================================================

    /**
     * Scroll-triggered animations
     */
    function initScrollAnimations() {
        const animatedElements = document.querySelectorAll('.animate-on-scroll');
        
        if ('IntersectionObserver' in window) {
            const animationObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animated');
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            animatedElements.forEach(el => animationObserver.observe(el));
        }
    }

    // =============================================================================
    // NOTIFICATION SYSTEM
    // =============================================================================

    /**
     * Enhanced notification system
     */
    function initNotifications() {
        // Auto-hide alerts after 5 seconds
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.style.opacity = '0';
                    alert.style.transform = 'translateX(100%)';
                    setTimeout(() => {
                        alert.remove();
                    }, 300);
                }
            }, 5000);
        });

        // Add close button functionality
        const closeButtons = document.querySelectorAll('.alert .btn-close');
        closeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const alert = this.closest('.alert');
                alert.style.opacity = '0';
                alert.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            });
        });
    }

    // =============================================================================
    // THEME SWITCHER
    // =============================================================================

    /**
     * Theme switcher functionality
     */
    function initThemeSwitcher() {
        const themeToggle = document.querySelector('.theme-toggle');
        const body = document.body;
        
        if (themeToggle) {
            // Load saved theme
            const savedTheme = localStorage.getItem('theme') || 'light';
            body.setAttribute('data-theme', savedTheme);
            
            themeToggle.addEventListener('click', function() {
                const currentTheme = body.getAttribute('data-theme');
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                
                body.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                
                // Update toggle button
                this.innerHTML = newTheme === 'light' ? 
                    '<i class="fas fa-moon"></i>' : 
                    '<i class="fas fa-sun"></i>';
            });
        }
    }

    // =============================================================================
    // INITIALIZATION
    // =============================================================================

    /**
     * Initialize all enhancements when DOM is ready
     */
    function init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        // Initialize all modules
        initNavigation();
        initForms();
        initCards();
        initButtons();
        initSearch();
        initModals();
        initTooltips();
        initLazyLoading();
        initScrollAnimations();
        initNotifications();
        initThemeSwitcher();

        // Add loaded class to body
        document.body.classList.add('enhanced');
    }

    // Start initialization
    init();

    // =============================================================================
    // CSS STYLES FOR ENHANCEMENTS
    // =============================================================================

    // Add CSS styles for enhancements
    const style = document.createElement('style');
    style.textContent = `
        /* Ripple effect */
        .btn {
            position: relative;
            overflow: hidden;
        }
        
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        }
        
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        /* Loading state */
        .btn.loading {
            opacity: 0.7;
            pointer-events: none;
        }
        
        /* Search suggestions */
        .search-suggestions {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #dee2e6;
            border-top: none;
            border-radius: 0 0 0.375rem 0.375rem;
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
            z-index: 1000;
            display: none;
        }
        
        .suggestion-item {
            padding: 0.75rem 1rem;
            cursor: pointer;
            border-bottom: 1px solid #f8f9fa;
        }
        
        .suggestion-item:last-child {
            border-bottom: none;
        }
        
        .suggestion-item:hover,
        .suggestion-item.active {
            background-color: #f8f9fa;
        }
        
        /* Lazy loading */
        .lazy {
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .loaded {
            opacity: 1;
        }
        
        /* Scroll animations */
        .animate-on-scroll {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .animate-on-scroll.animated {
            opacity: 1;
            transform: translateY(0);
        }
        
        /* Navbar scroll effect */
        .navbar {
            transition: transform 0.3s ease, background-color 0.3s ease;
        }
        
        .navbar-scrolled {
            background-color: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(10px);
        }
        
        /* Alert animations */
        .alert {
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        
        /* Theme support */
        [data-theme="dark"] {
            --bg-primary: #1a1a1a;
            --bg-secondary: #2d2d2d;
            --text-primary: #ffffff;
            --text-secondary: #b3b3b3;
            --border-color: #404040;
        }
    `;
    document.head.appendChild(style);

})();

