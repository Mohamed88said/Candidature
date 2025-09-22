// Custom JavaScript for Recruitment Platform

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Newsletter subscription
    $('#newsletter-form').on('submit', function(e) {
        e.preventDefault();
        
        var form = $(this);
        var email = form.find('input[name="email"]').val();
        var submitBtn = form.find('button[type="submit"]');
        var originalBtnText = submitBtn.html();
        
        // Show loading state
        submitBtn.html('<i class="fas fa-spinner fa-spin"></i>').prop('disabled', true);
        
        $.ajax({
            url: '/newsletter/subscribe/',
            type: 'POST',
            data: {
                'email': email,
                'csrfmiddlewaretoken': form.find('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function(response) {
                if (response.success) {
                    showAlert('success', response.message);
                    form[0].reset();
                } else {
                    showAlert('warning', response.message);
                }
            },
            error: function() {
                showAlert('danger', 'Une errGNF est survenue. Veuillez réessayer.');
            },
            complete: function() {
                submitBtn.html(originalBtnText).prop('disabled', false);
            }
        });
    });

    // Job save/unsave functionality
    $('.save-job-btn').on('click', function(e) {
        e.preventDefault();
        
        var btn = $(this);
        var jobId = btn.data('job-id');
        var icon = btn.find('i');
        
        $.ajax({
            url: '/jobs/save/' + jobId + '/',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    if (response.is_saved) {
                        icon.removeClass('far').addClass('fas');
                        btn.removeClass('btn-outline-primary').addClass('btn-primary');
                    } else {
                        icon.removeClass('fas').addClass('far');
                        btn.removeClass('btn-primary').addClass('btn-outline-primary');
                    }
                    showAlert('success', response.message);
                }
            },
            error: function() {
                showAlert('danger', 'Une errGNF est survenue.');
            }
        });
    });

    // Job alert toggle
    $('.toggle-alert-btn').on('click', function(e) {
        e.preventDefault();
        
        var btn = $(this);
        var alertId = btn.data('alert-id');
        
        $.ajax({
            url: '/jobs/alerts/' + alertId + '/toggle/',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    if (response.is_active) {
                        btn.removeClass('btn-outline-success').addClass('btn-success')
                           .html('<i class="fas fa-bell"></i> Actif');
                    } else {
                        btn.removeClass('btn-success').addClass('btn-outline-success')
                           .html('<i class="fas fa-bell-slash"></i> Inactif');
                    }
                    showAlert('success', response.message);
                }
            },
            error: function() {
                showAlert('danger', 'Une errGNF est survenue.');
            }
        });
    });

    // Skill and language management (AJAX)
    $('.delete-skill-btn, .delete-language-btn').on('click', function(e) {
        e.preventDefault();
        
        if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) {
            return;
        }
        
        var btn = $(this);
        var url = btn.attr('href');
        var row = btn.closest('.list-group-item, tr');
        
        $.ajax({
            url: url,
            type: 'DELETE',
            data: {
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    row.fadeOut(300, function() {
                        $(this).remove();
                    });
                    showAlert('success', 'Élément supprimé avec succès.');
                }
            },
            error: function() {
                showAlert('danger', 'Une errGNF est survenue.');
            }
        });
    });

    // File upload drag and drop
    $('.file-upload-area').on('dragover', function(e) {
        e.preventDefault();
        $(this).addClass('dragover');
    });

    $('.file-upload-area').on('dragleave', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover');
    });

    $('.file-upload-area').on('drop', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover');
        
        var files = e.originalEvent.dataTransfer.files;
        var input = $(this).find('input[type="file"]')[0];
        input.files = files;
        
        // Update file name display
        if (files.length > 0) {
            $(this).find('.file-name').text(files[0].name);
        }
    });

    // Auto-hide alerts after 5 seconds
    $('.alert').each(function() {
        var alert = $(this);
        setTimeout(function() {
            alert.fadeOut();
        }, 5000);
    });

    // Search form enhancements
    $('.search-form input').on('focus', function() {
        $(this).closest('.search-form').addClass('focused');
    });

    $('.search-form input').on('blur', function() {
        $(this).closest('.search-form').removeClass('focused');
    });

    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        
        var target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 100
            }, 500);
        }
    });

    // Back to top button
    var backToTopBtn = $('<button class="btn btn-primary btn-floating back-to-top" style="position: fixed; bottom: 20px; right: 20px; z-index: 1000; display: none;"><i class="fas fa-arrow-up"></i></button>');
    $('body').append(backToTopBtn);

    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            backToTopBtn.fadeIn();
        } else {
            backToTopBtn.fadeOut();
        }
    });

    backToTopBtn.on('click', function() {
        $('html, body').animate({scrollTop: 0}, 500);
    });

    // Form validation enhancements
    $('form').on('submit', function() {
        var form = $(this);
        var submitBtn = form.find('button[type="submit"], input[type="submit"]');
        
        if (submitBtn.length) {
            var originalText = submitBtn.html() || submitBtn.val();
            submitBtn.prop('disabled', true);
            
            if (submitBtn.is('button')) {
                submitBtn.html('<i class="fas fa-spinner fa-spin"></i> Traitement...');
            } else {
                submitBtn.val('Traitement...');
            }
            
            // Re-enable after 10 seconds to prevent permanent disable
            setTimeout(function() {
                submitBtn.prop('disabled', false);
                if (submitBtn.is('button')) {
                    submitBtn.html(originalText);
                } else {
                    submitBtn.val(originalText);
                }
            }, 10000);
        }
    });

    // Character counter for textareas
    $('textarea[maxlength]').each(function() {
        var textarea = $(this);
        var maxLength = textarea.attr('maxlength');
        var counter = $('<small class="text-muted character-counter">0/' + maxLength + '</small>');
        textarea.after(counter);
        
        textarea.on('input', function() {
            var currentLength = $(this).val().length;
            counter.text(currentLength + '/' + maxLength);
            
            if (currentLength > maxLength * 0.9) {
                counter.removeClass('text-muted').addClass('text-warning');
            } else {
                counter.removeClass('text-warning').addClass('text-muted');
            }
        });
    });

    // Auto-save for forms (draft functionality)
    $('form[data-autosave]').each(function() {
        var form = $(this);
        var formId = form.data('autosave');
        
        // Load saved data
        var savedData = localStorage.getItem('form_' + formId);
        if (savedData) {
            try {
                var data = JSON.parse(savedData);
                $.each(data, function(name, value) {
                    form.find('[name="' + name + '"]').val(value);
                });
            } catch (e) {
                console.log('Error loading saved form data:', e);
            }
        }
        
        // Save data on change
        form.find('input, textarea, select').on('change input', function() {
            var formData = {};
            form.find('input, textarea, select').each(function() {
                var field = $(this);
                if (field.attr('name') && field.attr('type') !== 'password') {
                    formData[field.attr('name')] = field.val();
                }
            });
            localStorage.setItem('form_' + formId, JSON.stringify(formData));
        });
        
        // Clear saved data on successful submit
        form.on('submit', function() {
            setTimeout(function() {
                localStorage.removeItem('form_' + formId);
            }, 1000);
        });
    });

    // Dashboard stats animation
    $('.dashboard-stat h3').each(function() {
        var $this = $(this);
        var countTo = parseInt($this.text());
        
        $({ countNum: 0 }).animate({
            countNum: countTo
        }, {
            duration: 2000,
            easing: 'swing',
            step: function() {
                $this.text(Math.floor(this.countNum));
            },
            complete: function() {
                $this.text(countTo);
            }
        });
    });

    // Notification management
    $('.mark-notification-read').on('click', function(e) {
        e.preventDefault();
        
        var btn = $(this);
        var notificationId = btn.data('notification-id');
        
        $.ajax({
            url: '/dashboard/api/notification/' + notificationId + '/read/',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    btn.closest('.notification-item').fadeOut();
                }
            }
        });
    });
});

// Utility functions
function showAlert(type, message) {
    var alertHtml = '<div class="alert alert-' + type + ' alert-dismissible fade show" role="alert">' +
                    message +
                    '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
                    '</div>';
    
    var container = $('.container').first();
    if (container.length) {
        container.prepend(alertHtml);
    } else {
        $('body').prepend('<div class="container mt-3">' + alertHtml + '</div>');
    }
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        $('.alert').first().fadeOut();
    }, 5000);
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Export functions for global use
window.RecruitmentPlatform = {
    showAlert: showAlert,
    formatNumber: formatNumber,
    formatDate: formatDate,
    formatDateTime: formatDateTime
};
