// CV Builder JavaScript

class CVBuilder {
    constructor() {
        this.currentCV = null;
        this.autoSaveInterval = null;
        this.isAutoSaveEnabled = true;
        this.autoSaveIntervalTime = 30000; // 30 seconds
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeAutoSave();
        this.initializeFormValidation();
        this.initializeDragAndDrop();
    }
    
    setupEventListeners() {
        // Gestion des sections
        $(document).on('click', '.section-item', (e) => {
            this.switchSection($(e.currentTarget).data('section'));
        });
        
        // Gestion des formulaires
        $(document).on('submit', '.cv-form', (e) => {
            e.preventDefault();
            this.saveCV();
        });
        
        // Gestion des changements de contenu
        $(document).on('input change', '.cv-form input, .cv-form textarea, .cv-form select', (e) => {
            this.debounce(() => {
                this.autoSave();
            }, 1000)();
        });
        
        // Gestion des ajouts d'éléments
        $(document).on('click', '.add-experience', (e) => {
            e.preventDefault();
            this.addExperience();
        });
        
        $(document).on('click', '.add-education', (e) => {
            e.preventDefault();
            this.addEducation();
        });
        
        $(document).on('click', '.add-skill', (e) => {
            e.preventDefault();
            this.addSkill();
        });
        
        $(document).on('click', '.add-project', (e) => {
            e.preventDefault();
            this.addProject();
        });
        
        $(document).on('click', '.add-language', (e) => {
            e.preventDefault();
            this.addLanguage();
        });
        
        $(document).on('click', '.add-certification', (e) => {
            e.preventDefault();
            this.addCertification();
        });
        
        $(document).on('click', '.add-reference', (e) => {
            e.preventDefault();
            this.addReference();
        });
        
        // Gestion des suppressions
        $(document).on('click', '.remove-item', (e) => {
            e.preventDefault();
            this.removeItem($(e.currentTarget));
        });
        
        // Gestion des duplications
        $(document).on('click', '.duplicate-item', (e) => {
            e.preventDefault();
            this.duplicateItem($(e.currentTarget));
        });
        
        // Gestion des changements de modèle
        $(document).on('change', '#id_template', (e) => {
            this.changeTemplate($(e.target).val());
        });
        
        // Gestion des téléchargements
        $(document).on('click', '.download-cv', (e) => {
            e.preventDefault();
            this.downloadCV($(e.currentTarget).data('format'));
        });
        
        // Gestion des partages
        $(document).on('click', '.share-cv', (e) => {
            e.preventDefault();
            this.shareCV();
        });
        
        // Gestion des prévisualisations
        $(document).on('click', '.preview-cv', (e) => {
            e.preventDefault();
            this.previewCV();
        });
    }
    
    initializeAutoSave() {
        if (this.isAutoSaveEnabled) {
            this.autoSaveInterval = setInterval(() => {
                this.autoSave();
            }, this.autoSaveIntervalTime);
        }
    }
    
    initializeFormValidation() {
        // Validation des formulaires
        $('.cv-form').each(function() {
            $(this).validate({
                rules: {
                    title: {
                        required: true,
                        minlength: 3
                    },
                    'personal_info[first_name]': {
                        required: true,
                        minlength: 2
                    },
                    'personal_info[last_name]': {
                        required: true,
                        minlength: 2
                    },
                    'personal_info[email]': {
                        required: true,
                        email: true
                    }
                },
                messages: {
                    title: {
                        required: "Le titre du CV est requis",
                        minlength: "Le titre doit contenir au moins 3 caractères"
                    },
                    'personal_info[first_name]': {
                        required: "Le prénom est requis",
                        minlength: "Le prénom doit contenir au moins 2 caractères"
                    },
                    'personal_info[last_name]': {
                        required: "Le nom est requis",
                        minlength: "Le nom doit contenir au moins 2 caractères"
                    },
                    'personal_info[email]': {
                        required: "L'email est requis",
                        email: "Veuillez entrer un email valide"
                    }
                },
                errorElement: 'div',
                errorClass: 'invalid-feedback',
                highlight: function(element, errorClass, validClass) {
                    $(element).addClass('is-invalid').removeClass('is-valid');
                },
                unhighlight: function(element, errorClass, validClass) {
                    $(element).addClass('is-valid').removeClass('is-invalid');
                }
            });
        });
    }
    
    initializeDragAndDrop() {
        // Drag and drop pour réorganiser les sections
        $('.sortable-list').sortable({
            handle: '.drag-handle',
            placeholder: 'sortable-placeholder',
            update: function(event, ui) {
                CVBuilder.updateSectionOrder();
            }
        });
    }
    
    switchSection(sectionName) {
        // Masquer toutes les sections
        $('.cv-form-section').hide();
        
        // Afficher la section sélectionnée
        $(`#section-${sectionName}`).show();
        
        // Mettre à jour l'état actif
        $('.section-item').removeClass('active');
        $(`.section-item[data-section="${sectionName}"]`).addClass('active');
        
        // Mettre à jour l'URL
        history.pushState(null, null, `#${sectionName}`);
    }
    
    saveCV() {
        const formData = new FormData($('.cv-form')[0]);
        
        $.ajax({
            url: $('.cv-form').attr('action'),
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    CVBuilder.showNotification('CV sauvegardé avec succès', 'success');
                } else {
                    CVBuilder.showNotification('Erreur lors de la sauvegarde', 'error');
                }
            },
            error: function() {
                CVBuilder.showNotification('Erreur lors de la sauvegarde', 'error');
            }
        });
    }
    
    autoSave() {
        if (!this.isAutoSaveEnabled) return;
        
        const formData = new FormData($('.cv-form')[0]);
        
        $.ajax({
            url: '/cv-builder/api/auto-save/',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    console.log('Auto-sauvegarde réussie');
                }
            },
            error: function() {
                console.log('Erreur lors de l\'auto-sauvegarde');
            }
        });
    }
    
    addExperience() {
        const experienceHtml = this.getExperienceTemplate();
        $('#experiences-list').append(experienceHtml);
        this.initializeFormValidation();
    }
    
    addEducation() {
        const educationHtml = this.getEducationTemplate();
        $('#educations-list').append(educationHtml);
        this.initializeFormValidation();
    }
    
    addSkill() {
        const skillHtml = this.getSkillTemplate();
        $('#skills-list').append(skillHtml);
        this.initializeFormValidation();
    }
    
    addProject() {
        const projectHtml = this.getProjectTemplate();
        $('#projects-list').append(projectHtml);
        this.initializeFormValidation();
    }
    
    addLanguage() {
        const languageHtml = this.getLanguageTemplate();
        $('#languages-list').append(languageHtml);
        this.initializeFormValidation();
    }
    
    addCertification() {
        const certificationHtml = this.getCertificationTemplate();
        $('#certifications-list').append(certificationHtml);
        this.initializeFormValidation();
    }
    
    addReference() {
        const referenceHtml = this.getReferenceTemplate();
        $('#references-list').append(referenceHtml);
        this.initializeFormValidation();
    }
    
    removeItem(button) {
        if (confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) {
            button.closest('.item-container').fadeOut(300, function() {
                $(this).remove();
            });
        }
    }
    
    duplicateItem(button) {
        const item = button.closest('.item-container');
        const clonedItem = item.clone();
        
        // Réinitialiser les valeurs
        clonedItem.find('input, textarea, select').val('');
        
        // Insérer après l'élément original
        item.after(clonedItem);
        
        this.showNotification('Élément dupliqué avec succès', 'success');
    }
    
    changeTemplate(templateId) {
        if (confirm('Changer de modèle effacera les modifications non sauvegardées. Continuer ?')) {
            $.ajax({
                url: `/cv-builder/api/change-template/${this.currentCV}/`,
                method: 'POST',
                data: {
                    template_id: templateId,
                    csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                },
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        CVBuilder.showNotification('Erreur lors du changement de modèle', 'error');
                    }
                },
                error: function() {
                    CVBuilder.showNotification('Erreur lors du changement de modèle', 'error');
                }
            });
        }
    }
    
    downloadCV(format) {
        window.open(`/cv-builder/download/${this.currentCV}/${format}/`, '_blank');
    }
    
    shareCV() {
        $('#shareModal').modal('show');
    }
    
    previewCV() {
        window.open(`/cv-builder/preview/${this.currentCV}/`, '_blank');
    }
    
    updateSectionOrder() {
        const order = [];
        $('.sortable-list .item-container').each(function(index) {
            order.push($(this).data('id'));
        });
        
        $.ajax({
            url: '/cv-builder/api/update-order/',
            method: 'POST',
            data: {
                order: order,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    console.log('Ordre mis à jour');
                }
            }
        });
    }
    
    // Templates HTML
    getExperienceTemplate() {
        return `
            <div class="item-container" data-id="new">
                <div class="card">
                    <div class="card-header">
                        <h6>Nouvelle expérience</h6>
                        <div class="card-actions">
                            <button type="button" class="btn btn-sm btn-outline-secondary duplicate-item">
                                <i class="fas fa-copy"></i>
                            </button>
                            <button type="button" class="btn btn-sm btn-outline-danger remove-item">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label>Titre du poste</label>
                                    <input type="text" name="experience[][job_title]" class="form-control" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label>Entreprise</label>
                                    <input type="text" name="experience[][company]" class="form-control" required>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label>Date de début</label>
                                    <input type="date" name="experience[][start_date]" class="form-control" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label>Date de fin</label>
                                    <input type="date" name="experience[][end_date]" class="form-control">
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea name="experience[][description]" class="form-control" rows="4"></textarea>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    getEducationTemplate() {
        return `
            <div class="item-container" data-id="new">
                <div class="card">
                    <div class="card-header">
                        <h6>Nouvelle formation</h6>
                        <div class="card-actions">
                            <button type="button" class="btn btn-sm btn-outline-secondary duplicate-item">
                                <i class="fas fa-copy"></i>
                            </button>
                            <button type="button" class="btn btn-sm btn-outline-danger remove-item">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label>Diplôme</label>
                                    <input type="text" name="education[][degree]" class="form-control" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label>Établissement</label>
                                    <input type="text" name="education[][institution]" class="form-control" required>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label>Date de début</label>
                                    <input type="date" name="education[][start_date]" class="form-control" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label>Date de fin</label>
                                    <input type="date" name="education[][end_date]" class="form-control">
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea name="education[][description]" class="form-control" rows="3"></textarea>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    getSkillTemplate() {
        return `
            <div class="item-container" data-id="new">
                <div class="card">
                    <div class="card-header">
                        <h6>Nouvelle compétence</h6>
                        <div class="card-actions">
                            <button type="button" class="btn btn-sm btn-outline-secondary duplicate-item">
                                <i class="fas fa-copy"></i>
                            </button>
                            <button type="button" class="btn btn-sm btn-outline-danger remove-item">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label>Nom de la compétence</label>
                                    <input type="text" name="skills[][name]" class="form-control" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label>Niveau</label>
                                    <select name="skills[][level]" class="form-control" required>
                                        <option value="">Sélectionner</option>
                                        <option value="beginner">Débutant</option>
                                        <option value="intermediate">Intermédiaire</option>
                                        <option value="advanced">Avancé</option>
                                        <option value="expert">Expert</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    getProjectTemplate() {
        return `
            <div class="item-container" data-id="new">
                <div class="card">
                    <div class="card-header">
                        <h6>Nouveau projet</h6>
                        <div class="card-actions">
                            <button type="button" class="btn btn-sm btn-outline-secondary duplicate-item">
                                <i class="fas fa-copy"></i>
                            </button>
                            <button type="button" class="btn btn-sm btn-outline-danger remove-item">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="form-group">
                            <label>Nom du projet</label>
                            <input type="text" name="projects[][name]" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea name="projects[][description]" class="form-control" rows="3"></textarea>
                        </div>
                        <div class="form-group">
                            <label>Technologies</label>
                            <input type="text" name="projects[][technologies]" class="form-control" placeholder="Séparer par des virgules">
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    getLanguageTemplate() {
        return `
            <div class="item-container" data-id="new">
                <div class="card">
                    <div class="card-header">
                        <h6>Nouvelle langue</h6>
                        <div class="card-actions">
                            <button type="button" class="btn btn-sm btn-outline-secondary duplicate-item">
                                <i class="fas fa-copy"></i>
                            </button>
                            <button type="button" class="btn btn-sm btn-outline-danger remove-item">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label>Langue</label>
                                    <input type="text" name="languages[][name]" class="form-control" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label>Niveau</label>
                                    <select name="languages[][proficiency]" class="form-control" required>
                                        <option value="">Sélectionner</option>
                                        <option value="native">Langue maternelle</option>
                                        <option value="fluent">Courant</option>
                                        <option value="advanced">Avancé</option>
                                        <option value="intermediate">Intermédiaire</option>
                                        <option value="basic">Notions</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    getCertificationTemplate() {
        return `
            <div class="item-container" data-id="new">
                <div class="card">
                    <div class="card-header">
                        <h6>Nouvelle certification</h6>
                        <div class="card-actions">
                            <button type="button" class="btn btn-sm btn-outline-secondary duplicate-item">
                                <i class="fas fa-copy"></i>
                            </button>
                            <button type="button" class="btn btn-sm btn-outline-danger remove-item">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label>Nom de la certification</label>
                                    <input type="text" name="certifications[][name]" class="form-control" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label>Organisme émetteur</label>
                                    <input type="text" name="certifications[][issuer]" class="form-control" required>
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Date d'obtention</label>
                            <input type="date" name="certifications[][issue_date]" class="form-control" required>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    getReferenceTemplate() {
        return `
            <div class="item-container" data-id="new">
                <div class="card">
                    <div class="card-header">
                        <h6>Nouvelle référence</h6>
                        <div class="card-actions">
                            <button type="button" class="btn btn-sm btn-outline-secondary duplicate-item">
                                <i class="fas fa-copy"></i>
                            </button>
                            <button type="button" class="btn btn-sm btn-outline-danger remove-item">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label>Nom complet</label>
                                    <input type="text" name="references[][name]" class="form-control" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label>Poste</label>
                                    <input type="text" name="references[][position]" class="form-control" required>
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Entreprise</label>
                            <input type="text" name="references[][company]" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" name="references[][email]" class="form-control">
                        </div>
                    </div>
                </div>
            </div>
        `;
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

// Fonctions globales
function initCVBuilder() {
    window.cvBuilder = new CVBuilder();
}

function switchSection(sectionName) {
    if (window.cvBuilder) {
        window.cvBuilder.switchSection(sectionName);
    }
}

function addExperience() {
    if (window.cvBuilder) {
        window.cvBuilder.addExperience();
    }
}

function addEducation() {
    if (window.cvBuilder) {
        window.cvBuilder.addEducation();
    }
}

function addSkill() {
    if (window.cvBuilder) {
        window.cvBuilder.addSkill();
    }
}

function addProject() {
    if (window.cvBuilder) {
        window.cvBuilder.addProject();
    }
}

function addLanguage() {
    if (window.cvBuilder) {
        window.cvBuilder.addLanguage();
    }
}

function addCertification() {
    if (window.cvBuilder) {
        window.cvBuilder.addCertification();
    }
}

function addReference() {
    if (window.cvBuilder) {
        window.cvBuilder.addReference();
    }
}

function downloadCV(format) {
    if (window.cvBuilder) {
        window.cvBuilder.downloadCV(format);
    }
}

function shareCV() {
    if (window.cvBuilder) {
        window.cvBuilder.shareCV();
    }
}

function previewCV() {
    if (window.cvBuilder) {
        window.cvBuilder.previewCV();
    }
}

// Initialiser le constructeur de CV
$(document).ready(function() {
    initCVBuilder();
    
    // Gestion des onglets
    $('.nav-tabs a').click(function(e) {
        e.preventDefault();
        $(this).tab('show');
    });
    
    // Gestion des modales
    $('.modal').on('shown.bs.modal', function() {
        $(this).find('input:first').focus();
    });
    
    // Gestion des confirmations
    $('.btn-danger').click(function(e) {
        if (!confirm('Êtes-vous sûr de vouloir effectuer cette action ?')) {
            e.preventDefault();
        }
    });
    
    // Gestion des tooltips
    $('[data-toggle="tooltip"]').tooltip();
    
    // Gestion des popovers
    $('[data-toggle="popover"]').popover();
});


