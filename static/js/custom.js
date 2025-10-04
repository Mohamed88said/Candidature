// Enhanced JavaScript for Recruitment Platform

class RecruitmentPlatform {
    constructor() {
        this.init();
    }

    init() {
        this.initComponents();
        this.initEventListeners();
        this.initAnimations();
        this.initIntersectionObserver();
    }

    initComponents() {
        // Initialize Bootstrap components
        this.initTooltips();
        this.initPopovers();
        
        // Initialize custom components
        this.initBackToTop();
        this.initSmoothScrolling();
        this.initFormEnhancements();
        this.initNotificationSystem();
    }

    initEventListeners() {
        // Newsletter subscription
        this.handleNewsletterSubscription();
        
        // Job interactions
        this.handleJobInteractions();
        
        // Form submissions
        this.handleFormSubmissions();
        
        // File upload enhancements
        this.handleFileUploads();
        
        // Search enhancements
        this.handleSearchInteractions();
    }

    initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                trigger: 'hover focus'
            });
        });
    }

    initPopovers() {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(popoverTriggerEl => {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    initBackToTop() {
        const backToTopBtn = this.createBackToTopButton();
        document.body.appendChild(backToTopBtn);

        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                backToTopBtn.classList.add('show');
            } else {
                backToTopBtn.classList.remove('show');
            }
        });

        backToTopBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.smoothScrollToTop();
        });
    }

    createBackToTopButton() {
        const btn = document.createElement('button');
        btn.className = 'back-to-top';
        btn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        btn.style.display = 'none';
        
        setTimeout(() => {
            btn.classList.add('show');
            btn.style.display = 'flex';
        }, 100);
        
        return btn;
    }

    smoothScrollToTop() {
        const scrollToTop = () => {
            const currentPosition = window.scrollY;
            if (currentPosition > 0) {
                window.requestAnimationFrame(scrollToTop);
                window.scrollTo(0, currentPosition - currentPosition / 8);
            }
        };
        scrollToTop();
    }

    initSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    const offsetTop = target.getBoundingClientRect().top + window.scrollY - 100;
                    this.smoothScrollTo(offsetTop);
                }
            });
        });
    }

    smoothScrollTo(position) {
        window.scrollTo({
            top: position,
            behavior: 'smooth'
        });
    }

    handleNewsletterSubscription() {
        const newsletterForm = document.getElementById('newsletter-form');
        if (newsletterForm) {
            newsletterForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.submitNewsletterForm(newsletterForm);
            });
        }
    }

    async submitNewsletterForm(form) {
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;

        try {
            this.showLoadingState(submitBtn);
            
            const response = await fetch('/newsletter/subscribe/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showAlert('success', data.message);
                form.reset();
            } else {
                this.showAlert('warning', data.message);
            }
        } catch (error) {
            this.showAlert('danger', 'Une erreur est survenue. Veuillez réessayer.');
        } finally {
            this.hideLoadingState(submitBtn, originalBtnText);
        }
    }

    handleJobInteractions() {
        // Job save/unsave functionality
        document.querySelectorAll('.save-job-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                await this.toggleJobSave(btn);
            });
        });

        // Job alert toggle
        document.querySelectorAll('.toggle-alert-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                await this.toggleJobAlert(btn);
            });
        });
    }

    async toggleJobSave(btn) {
        const jobId = btn.dataset.jobId;
        const icon = btn.querySelector('i');

        try {
            const response = await fetch(`/jobs/save/${jobId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.updateSaveButton(btn, icon, data.is_saved);
                this.showAlert('success', data.message);
            }
        } catch (error) {
            this.showAlert('danger', 'Une erreur est survenue.');
        }
    }

    updateSaveButton(btn, icon, isSaved) {
        if (isSaved) {
            icon.classList.replace('far', 'fas');
            btn.classList.replace('btn-outline-primary', 'btn-primary');
            btn.classList.add('animate__animated', 'animate__pulse');
        } else {
            icon.classList.replace('fas', 'far');
            btn.classList.replace('btn-primary', 'btn-outline-primary');
        }
        
        setTimeout(() => {
            btn.classList.remove('animate__animated', 'animate__pulse');
        }, 1000);
    }

    initFormEnhancements() {
        // Character counters
        this.initCharacterCounters();
        
        // Auto-save functionality
        this.initAutoSave();
        
        // Form validation enhancements
        this.initFormValidation();
    }

    initCharacterCounters() {
        document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
            const maxLength = textarea.getAttribute('maxlength');
            const counter = document.createElement('small');
            counter.className = 'text-muted character-counter';
            counter.textContent = `0/${maxLength}`;
            textarea.parentNode.appendChild(counter);

            textarea.addEventListener('input', () => {
                const currentLength = textarea.value.length;
                counter.textContent = `${currentLength}/${maxLength}`;
                
                if (currentLength > maxLength * 0.9) {
                    counter.classList.replace('text-muted', 'text-warning');
                } else {
                    counter.classList.replace('text-warning', 'text-muted');
                }
            });
        });
    }

    initAutoSave() {
        document.querySelectorAll('form[data-autosave]').forEach(form => {
            const formId = form.dataset.autosave;
            this.loadSavedFormData(form, formId);
            
            form.querySelectorAll('input, textarea, select').forEach(field => {
                field.addEventListener('change', () => {
                    this.saveFormData(form, formId);
                });
                
                field.addEventListener('input', this.debounce(() => {
                    this.saveFormData(form, formId);
                }, 500));
            });

            form.addEventListener('submit', () => {
                localStorage.removeItem(`form_${formId}`);
            });
        });
    }

    loadSavedFormData(form, formId) {
        const savedData = localStorage.getItem(`form_${formId}`);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(name => {
                    const field = form.querySelector(`[name="${name}"]`);
                    if (field && field.type !== 'password') {
                        field.value = data[name];
                    }
                });
            } catch (error) {
                console.warn('Error loading saved form data:', error);
            }
        }
    }

    saveFormData(form, formId) {
        const formData = {};
        form.querySelectorAll('input, textarea, select').forEach(field => {
            if (field.name && field.type !== 'password') {
                formData[field.name] = field.value;
            }
        });
        localStorage.setItem(`form_${formId}`, JSON.stringify(formData));
    }

    initFormValidation() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                if (submitBtn) {
                    this.showFormLoadingState(submitBtn);
                }
            });
        });
    }

    showFormLoadingState(submitBtn) {
        const originalText = submitBtn.innerHTML || submitBtn.value;
        submitBtn.disabled = true;

        if (submitBtn.tagName === 'BUTTON') {
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Traitement...';
        } else {
            submitBtn.value = 'Traitement...';
        }

        // Safety timeout to re-enable button
        setTimeout(() => {
            submitBtn.disabled = false;
            if (submitBtn.tagName === 'BUTTON') {
                submitBtn.innerHTML = originalText;
            } else {
                submitBtn.value = originalText;
            }
        }, 10000);
    }

    handleFileUploads() {
        document.querySelectorAll('.file-upload-area').forEach(area => {
            const input = area.querySelector('input[type="file"]');
            const fileName = area.querySelector('.file-name');

            ['dragover', 'dragenter'].forEach(event => {
                area.addEventListener(event, (e) => {
                    e.preventDefault();
                    area.classList.add('dragover');
                });
            });

            ['dragleave', 'dragend'].forEach(event => {
                area.addEventListener(event, (e) => {
                    e.preventDefault();
                    area.classList.remove('dragover');
                });
            });

            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    input.files = files;
                    if (fileName) {
                        fileName.textContent = files[0].name;
                    }
                    this.showAlert('success', 'Fichier sélectionné avec succès');
                }
            });

            input.addEventListener('change', () => {
                if (input.files.length > 0 && fileName) {
                    fileName.textContent = input.files[0].name;
                }
            });
        });
    }

    handleSearchInteractions() {
        document.querySelectorAll('.search-form input').forEach(input => {
            input.addEventListener('focus', () => {
                input.closest('.search-form').classList.add('focused');
            });

            input.addEventListener('blur', () => {
                input.closest('.search-form').classList.remove('focused');
            });
        });
    }

    initAnimations() {
        // Animate numbers in dashboard stats
        this.animateNumbers();
        
        // Initialize AOS (Animate On Scroll) if available
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                once: true,
                offset: 100
            });
        }
    }

    animateNumbers() {
        document.querySelectorAll('.dashboard-stat h3').forEach(element => {
            const target = parseInt(element.textContent);
            const duration = 2000;
            const step = target / (duration / 16);
            let current = 0;

            const timer = setInterval(() => {
                current += step;
                if (current >= target) {
                    element.textContent = target.toLocaleString();
                    clearInterval(timer);
                } else {
                    element.textContent = Math.floor(current).toLocaleString();
                }
            }, 16);
        });
    }

    initIntersectionObserver() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });

        // Observe elements for animation
        document.querySelectorAll('.card, .stat-card, .job-card').forEach(el => {
            observer.observe(el);
        });
    }

    initNotificationSystem() {
        // Auto-hide alerts
        document.querySelectorAll('.alert').forEach(alert => {
            setTimeout(() => {
                this.hideAlert(alert);
            }, 5000);
        });

        // Mark notifications as read
        document.querySelectorAll('.mark-notification-read').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                await this.markNotificationAsRead(btn);
            });
        });
    }

    async markNotificationAsRead(btn) {
        const notificationId = btn.dataset.notificationId;

        try {
            const response = await fetch(`/dashboard/api/notification/${notificationId}/read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();
            if (data.success) {
                btn.closest('.notification-item').style.opacity = '0';
                setTimeout(() => {
                    btn.closest('.notification-item').remove();
                }, 300);
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    // Utility methods
    showLoadingState(button) {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }

    hideLoadingState(button, originalText) {
        button.disabled = false;
        button.innerHTML = originalText;
    }

    showAlert(type, message) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        const container = document.querySelector('.container') || document.body;
        if (container.querySelector('.alert') || container.classList.contains('container')) {
            container.insertAdjacentHTML('afterbegin', alertHtml);
        } else {
            document.body.insertAdjacentHTML('afterbegin', 
                `<div class="container mt-3">${alertHtml}</div>`
            );
        }

        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideAlert(document.querySelector('.alert'));
        }, 5000);
    }

    hideAlert(alert) {
        if (alert) {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
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

    // Public utility methods
    static formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    }

    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    static formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Initialize the platform when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.RecruitmentApp = new RecruitmentPlatform();
});

// Export for global use
window.RecruitmentPlatform = {
    showAlert: (type, message) => {
        const app = window.RecruitmentApp;
        if (app) app.showAlert(type, message);
    },
    formatNumber: RecruitmentPlatform.formatNumber,
    formatDate: RecruitmentPlatform.formatDate,
    formatDateTime: RecruitmentPlatform.formatDateTime
};