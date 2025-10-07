// Tests System JavaScript

class TestsSystem {
    constructor() {
        this.currentTest = null;
        this.currentAttempt = null;
        this.timeRemaining = null;
        this.timer = null;
        this.autoSaveInterval = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeTest();
    }
    
    setupEventListeners() {
        // Gestion des réponses
        $(document).on('change', 'input[type="radio"], input[type="checkbox"]', (e) => {
            this.handleAnswerChange(e);
        });
        
        $(document).on('input', 'textarea, input[type="text"]', (e) => {
            this.handleTextAnswer(e);
        });
        
        // Gestion de la navigation
        $(document).on('click', '.next-question', (e) => {
            e.preventDefault();
            this.nextQuestion();
        });
        
        $(document).on('click', '.prev-question', (e) => {
            e.preventDefault();
            this.prevQuestion();
        });
        
        $(document).on('click', '.submit-test', (e) => {
            e.preventDefault();
            this.submitTest();
        });
        
        // Gestion de la sauvegarde automatique
        $(document).on('click', '.save-progress', (e) => {
            e.preventDefault();
            this.saveProgress();
        });
        
        // Gestion du plein écran
        $(document).on('click', '.toggle-fullscreen', (e) => {
            e.preventDefault();
            this.toggleFullscreen();
        });
        
        // Gestion de la sortie du plein écran
        $(document).on('keydown', (e) => {
            if (e.key === 'Escape' && this.isFullscreen()) {
                this.exitFullscreen();
            }
        });
        
        // Gestion de la perte de focus (détection de triche)
        $(document).on('blur', window, () => {
            this.handleWindowBlur();
        });
        
        $(document).on('focus', window, () => {
            this.handleWindowFocus();
        });
        
        // Gestion du clic droit (désactiver)
        $(document).on('contextmenu', (e) => {
            if (this.isTestActive()) {
                e.preventDefault();
                this.showWarning('Le clic droit est désactivé pendant le test.');
            }
        });
        
        // Gestion des raccourcis clavier
        $(document).on('keydown', (e) => {
            if (this.isTestActive()) {
                this.handleKeyboardShortcuts(e);
            }
        });
    }
    
    initializeTest() {
        // Initialiser le timer si nécessaire
        const timeElement = document.querySelector('.time-remaining');
        if (timeElement) {
            const timeText = timeElement.textContent;
            const minutes = parseInt(timeText.match(/(\d+)/)?.[1] || 0);
            if (minutes > 0) {
                this.startTimer(minutes * 60);
            }
        }
        
        // Démarrer la sauvegarde automatique
        this.startAutoSave();
        
        // Initialiser les réponses sauvegardées
        this.loadSavedAnswers();
    }
    
    startTimer(seconds) {
        this.timeRemaining = seconds;
        
        this.timer = setInterval(() => {
            this.timeRemaining--;
            this.updateTimerDisplay();
            
            if (this.timeRemaining <= 0) {
                this.timeExpired();
            }
        }, 1000);
    }
    
    updateTimerDisplay() {
        const timeElement = document.querySelector('.time-remaining');
        if (timeElement) {
            const minutes = Math.floor(this.timeRemaining / 60);
            const seconds = this.timeRemaining % 60;
            
            timeElement.innerHTML = `
                <i class="fas fa-clock"></i>
                ${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}
            `;
            
            // Changer la couleur quand il reste peu de temps
            if (this.timeRemaining <= 300) { // 5 minutes
                timeElement.style.color = '#dc3545';
            } else if (this.timeRemaining <= 600) { // 10 minutes
                timeElement.style.color = '#ffc107';
            }
        }
    }
    
    timeExpired() {
        clearInterval(this.timer);
        this.showWarning('Le temps imparti pour ce test a expiré. Le test sera soumis automatiquement.');
        
        setTimeout(() => {
            this.submitTest();
        }, 3000);
    }
    
    handleAnswerChange(e) {
        const questionId = e.target.dataset.questionId;
        const answer = this.getAnswerValue(e.target);
        
        this.saveAnswer(questionId, answer);
        this.updateAnswerVisual(e.target);
    }
    
    handleTextAnswer(e) {
        const questionId = e.target.dataset.questionId;
        const answer = e.target.value;
        
        this.saveAnswer(questionId, answer);
    }
    
    getAnswerValue(element) {
        if (element.type === 'radio') {
            return element.value;
        } else if (element.type === 'checkbox') {
            const checkboxes = document.querySelectorAll(`input[name="${element.name}"]:checked`);
            return Array.from(checkboxes).map(cb => cb.value);
        } else if (element.type === 'text' || element.tagName === 'TEXTAREA') {
            return element.value;
        }
        return null;
    }
    
    saveAnswer(questionId, answer) {
        if (!this.currentAttempt) return;
        
        // Sauvegarder localement
        const savedAnswers = this.getSavedAnswers();
        savedAnswers[questionId] = answer;
        localStorage.setItem(`test_answers_${this.currentAttempt}`, JSON.stringify(savedAnswers));
        
        // Marquer la question comme répondue
        this.markQuestionAnswered(questionId);
    }
    
    getSavedAnswers() {
        if (!this.currentAttempt) return {};
        
        const saved = localStorage.getItem(`test_answers_${this.currentAttempt}`);
        return saved ? JSON.parse(saved) : {};
    }
    
    loadSavedAnswers() {
        const savedAnswers = this.getSavedAnswers();
        
        Object.keys(savedAnswers).forEach(questionId => {
            const answer = savedAnswers[questionId];
            this.setAnswerValue(questionId, answer);
            this.markQuestionAnswered(questionId);
        });
    }
    
    setAnswerValue(questionId, answer) {
        if (Array.isArray(answer)) {
            // Réponse multiple (checkboxes)
            answer.forEach(value => {
                const checkbox = document.querySelector(`input[data-question-id="${questionId}"][value="${value}"]`);
                if (checkbox) checkbox.checked = true;
            });
        } else {
            // Réponse simple (radio, text)
            const element = document.querySelector(`input[data-question-id="${questionId}"][value="${answer}"], textarea[data-question-id="${questionId}"], input[type="text"][data-question-id="${questionId}"]`);
            if (element) {
                if (element.type === 'radio' || element.type === 'checkbox') {
                    element.checked = true;
                } else {
                    element.value = answer;
                }
            }
        }
    }
    
    markQuestionAnswered(questionId) {
        const questionElement = document.querySelector(`[data-question-id="${questionId}"]`);
        if (questionElement) {
            questionElement.closest('.question-container').classList.add('answered');
        }
    }
    
    updateAnswerVisual(element) {
        // Mettre à jour l'apparence de la réponse sélectionnée
        const option = element.closest('.answer-option');
        if (option) {
            // Désélectionner les autres options pour les questions à choix unique
            if (element.type === 'radio') {
                const otherOptions = option.parentElement.querySelectorAll('.answer-option');
                otherOptions.forEach(opt => opt.classList.remove('selected'));
            }
            
            option.classList.toggle('selected', element.checked);
        }
    }
    
    nextQuestion() {
        const form = document.getElementById('test-form');
        if (form) {
            form.submit();
        }
    }
    
    prevQuestion() {
        // Logique pour revenir à la question précédente
        // À implémenter selon les besoins
    }
    
    submitTest() {
        if (!confirm('Êtes-vous sûr de vouloir soumettre ce test ? Vous ne pourrez plus modifier vos réponses.')) {
            return;
        }
        
        this.showLoading('Soumission du test en cours...');
        
        // Collecter toutes les réponses
        const answers = this.getSavedAnswers();
        
        // Soumettre via AJAX
        $.ajax({
            url: window.location.href,
            type: 'POST',
            data: {
                'answers': JSON.stringify(answers),
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: (response) => {
                this.hideLoading();
                if (response.success) {
                    window.location.href = response.redirect_url;
                } else {
                    this.showError('Erreur lors de la soumission du test.');
                }
            },
            error: () => {
                this.hideLoading();
                this.showError('Erreur lors de la soumission du test.');
            }
        });
    }
    
    saveProgress() {
        const answers = this.getSavedAnswers();
        
        $.ajax({
            url: '/tests/api/save-progress/',
            type: 'POST',
            data: {
                'attempt_id': this.currentAttempt,
                'answers': JSON.stringify(answers),
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: () => {
                this.showSuccess('Progrès sauvegardé.');
            },
            error: () => {
                this.showError('Erreur lors de la sauvegarde.');
            }
        });
    }
    
    startAutoSave() {
        // Sauvegarder automatiquement toutes les 30 secondes
        this.autoSaveInterval = setInterval(() => {
            this.saveProgress();
        }, 30000);
    }
    
    stopAutoSave() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }
    }
    
    toggleFullscreen() {
        if (this.isFullscreen()) {
            this.exitFullscreen();
        } else {
            this.enterFullscreen();
        }
    }
    
    enterFullscreen() {
        const element = document.documentElement;
        if (element.requestFullscreen) {
            element.requestFullscreen();
        } else if (element.webkitRequestFullscreen) {
            element.webkitRequestFullscreen();
        } else if (element.msRequestFullscreen) {
            element.msRequestFullscreen();
        }
    }
    
    exitFullscreen() {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    }
    
    isFullscreen() {
        return !!(document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement);
    }
    
    handleWindowBlur() {
        if (this.isTestActive()) {
            this.blurCount = (this.blurCount || 0) + 1;
            
            if (this.blurCount > 3) {
                this.showWarning('Attention : Vous avez quitté la fenêtre plusieurs fois. Cela peut être considéré comme de la triche.');
            }
        }
    }
    
    handleWindowFocus() {
        if (this.isTestActive()) {
            this.blurCount = 0;
        }
    }
    
    handleKeyboardShortcuts(e) {
        // Désactiver certains raccourcis clavier
        const disabledKeys = ['F12', 'F5', 'Ctrl+R', 'Ctrl+Shift+I', 'Ctrl+U', 'Ctrl+S'];
        const keyCombo = e.ctrlKey ? `Ctrl+${e.key}` : e.key;
        
        if (disabledKeys.includes(keyCombo) || disabledKeys.includes(e.key)) {
            e.preventDefault();
            this.showWarning('Ce raccourci clavier est désactivé pendant le test.');
        }
    }
    
    isTestActive() {
        return document.querySelector('.test-container') !== null;
    }
    
    showLoading(message) {
        const loadingHtml = `
            <div class="loading-overlay">
                <div class="loading-content">
                    <div class="spinner"></div>
                    <p>${message}</p>
                </div>
            </div>
        `;
        
        $('body').append(loadingHtml);
    }
    
    hideLoading() {
        $('.loading-overlay').remove();
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
        if (this.timer) {
            clearInterval(this.timer);
        }
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }
    }
}

// Initialiser le système de tests
let testsSystem;
$(document).ready(function() {
    testsSystem = new TestsSystem();
    
    // Nettoyer lors de la fermeture de la page
    $(window).on('beforeunload', function() {
        if (testsSystem) {
            testsSystem.destroy();
        }
    });
});

// Fonctions globales pour les templates
function startTest(testId) {
    if (confirm('Êtes-vous prêt à commencer ce test ?')) {
        window.location.href = `/tests/test/${testId}/start/`;
    }
}

function viewTestResult(attemptId) {
    window.location.href = `/tests/attempt/${attemptId}/result/`;
}

function downloadCertificate(certificateId) {
    window.open(`/tests/certificate/${certificateId}/download/`, '_blank');
}

function shareTestResult(attemptId) {
    if (navigator.share) {
        navigator.share({
            title: 'Mon résultat de test',
            text: 'Regardez mon résultat de test !',
            url: window.location.origin + `/tests/attempt/${attemptId}/result/`
        });
    } else {
        // Fallback : copier le lien
        const url = window.location.origin + `/tests/attempt/${attemptId}/result/`;
        navigator.clipboard.writeText(url).then(() => {
            testsSystem.showSuccess('Lien copié dans le presse-papiers !');
        });
    }
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
    
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
    }
    
    .loading-content {
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .loading-content .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #007bff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;

// Ajouter les styles au document
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);


