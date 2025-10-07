// Chat System JavaScript

class ChatSystem {
    constructor() {
        this.currentRoomId = null;
        this.messageInterval = null;
        this.notificationInterval = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.startAutoRefresh();
        this.setupWebSocket();
    }
    
    setupEventListeners() {
        // Gestion de l'envoi de messages
        $(document).on('submit', '#message-form', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
        
        // Gestion de la touche Entrée
        $(document).on('keypress', 'input[name="content"]', (e) => {
            if (e.which === 13) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Gestion des clics sur les conversations
        $(document).on('click', '.conversation-item', (e) => {
            e.preventDefault();
            const roomId = $(e.currentTarget).data('room-id');
            if (roomId) {
                window.location.href = `/chat/room/${roomId}/`;
            }
        });
        
        // Gestion des réactions
        $(document).on('click', '.reaction', (e) => {
            e.preventDefault();
            const messageId = $(e.currentTarget).data('message-id');
            const emoji = $(e.currentTarget).data('emoji');
            this.toggleReaction(messageId, emoji);
        });
        
        // Gestion du sélecteur d'emoji
        $(document).on('click', '.emoji-item', (e) => {
            e.preventDefault();
            const emoji = $(e.currentTarget).text();
            this.insertEmoji(emoji);
        });
        
        // Gestion du téléchargement de fichiers
        $(document).on('change', '#file-upload', (e) => {
            this.handleFileUpload(e.target.files[0]);
        });
    }
    
    setupWebSocket() {
        // Configuration WebSocket pour les messages en temps réel
        if (typeof WebSocket !== 'undefined') {
            this.connectWebSocket();
        }
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat/`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connecté');
                this.isConnected = true;
                this.reconnectAttempts = 0;
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket fermé');
                this.isConnected = false;
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('Erreur WebSocket:', error);
            };
        } catch (error) {
            console.error('Erreur de connexion WebSocket:', error);
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`Tentative de reconnexion ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
                this.connectWebSocket();
            }, 2000 * this.reconnectAttempts);
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'new_message':
                this.handleNewMessage(data.message);
                break;
            case 'message_updated':
                this.handleMessageUpdated(data.message);
                break;
            case 'message_deleted':
                this.handleMessageDeleted(data.message_id);
                break;
            case 'reaction_added':
                this.handleReactionAdded(data.message_id, data.emoji, data.count);
                break;
            case 'reaction_removed':
                this.handleReactionRemoved(data.message_id, data.emoji, data.count);
                break;
            case 'typing':
                this.handleTyping(data.user_id, data.room_id);
                break;
            case 'user_online':
                this.handleUserOnline(data.user_id);
                break;
            case 'user_offline':
                this.handleUserOffline(data.user_id);
                break;
        }
    }
    
    sendMessage() {
        const form = document.getElementById('message-form');
        if (!form) return;
        
        const formData = new FormData(form);
        const content = formData.get('content').trim();
        
        if (!content && !formData.get('attachment')) {
            return;
        }
        
        // Désactiver le formulaire pendant l'envoi
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        submitBtn.disabled = true;
        
        $.ajax({
            url: form.action || `/chat/room/${this.currentRoomId}/send/`,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: (data) => {
                if (data.success) {
                    this.addMessageToChat(data.message);
                    form.reset();
                    this.scrollToBottom();
                    this.hideEmojiPicker();
                } else {
                    this.showError('Erreur lors de l\'envoi du message');
                }
            },
            error: (xhr) => {
                this.showError('Erreur lors de l\'envoi du message');
                console.error('Erreur AJAX:', xhr);
            },
            complete: () => {
                // Réactiver le formulaire
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
    }
    
    addMessageToChat(message) {
        const messageHtml = this.createMessageHtml(message);
        const chatMessages = document.getElementById('chat-messages');
        
        if (chatMessages) {
            chatMessages.insertAdjacentHTML('beforeend', messageHtml);
            this.scrollToBottom();
        }
    }
    
    createMessageHtml(message) {
        const isOwn = message.is_own;
        const messageClass = isOwn ? 'own-message' : '';
        const senderName = message.sender.name || 'Utilisateur';
        const avatar = message.sender.avatar || '';
        const avatarHtml = avatar ? 
            `<img src="${avatar}" alt="${senderName}">` : 
            `<div class="avatar-placeholder">${senderName.charAt(0)}</div>`;
        
        const time = new Date(message.created_at).toLocaleTimeString('fr-FR', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        return `
            <div class="message-item ${messageClass} new-message" data-message-id="${message.id}">
                <div class="message-avatar">
                    ${avatarHtml}
                </div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="sender-name">${senderName}</span>
                        <span class="message-time">${time}</span>
                    </div>
                    <div class="message-text">
                        ${this.formatMessageContent(message.content)}
                    </div>
                    ${message.attachment ? this.createAttachmentHtml(message.attachment) : ''}
                    <div class="message-reactions" id="reactions-${message.id}">
                        <!-- Réactions seront ajoutées ici -->
                    </div>
                </div>
                <div class="message-actions">
                    <div class="dropdown">
                        <button class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                                type="button" data-toggle="dropdown">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                        <div class="dropdown-menu">
                            <a class="dropdown-item" href="#" onclick="chatSystem.replyToMessage(${message.id})">
                                <i class="fas fa-reply"></i> Répondre
                            </a>
                            <a class="dropdown-item" href="#" onclick="chatSystem.addReaction(${message.id}, '👍')">
                                <i class="fas fa-thumbs-up"></i> 👍
                            </a>
                            <a class="dropdown-item" href="#" onclick="chatSystem.addReaction(${message.id}, '❤️')">
                                <i class="fas fa-heart"></i> ❤️
                            </a>
                            ${isOwn ? `
                                <div class="dropdown-divider"></div>
                                <a class="dropdown-item text-danger" href="#" onclick="chatSystem.deleteMessage(${message.id})">
                                    <i class="fas fa-trash"></i> Supprimer
                                </a>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    createAttachmentHtml(attachment) {
        const fileName = attachment.name || 'Fichier';
        const fileUrl = attachment.url || '#';
        
        return `
            <div class="message-attachment">
                <a href="${fileUrl}" target="_blank">
                    <i class="fas fa-paperclip"></i>
                    ${fileName}
                </a>
            </div>
        `;
    }
    
    formatMessageContent(content) {
        // Convertir les sauts de ligne en <br>
        content = content.replace(/\n/g, '<br>');
        
        // Détecter et formater les URLs
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        content = content.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener">$1</a>');
        
        // Détecter et formater les mentions (@username)
        const mentionRegex = /@(\w+)/g;
        content = content.replace(mentionRegex, '<span class="mention">@$1</span>');
        
        return content;
    }
    
    scrollToBottom() {
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    startAutoRefresh() {
        // Actualiser les messages toutes les 30 secondes
        this.messageInterval = setInterval(() => {
            this.loadNewMessages();
        }, 30000);
        
        // Actualiser les notifications toutes les 60 secondes
        this.notificationInterval = setInterval(() => {
            this.updateNotifications();
        }, 60000);
    }
    
    loadNewMessages() {
        if (!this.currentRoomId) return;
        
        const lastMessage = document.querySelector('.message-item:last-child');
        const lastMessageId = lastMessage ? lastMessage.dataset.messageId : null;
        
        $.get(`/chat/api/room/${this.currentRoomId}/messages/`, {
            after: lastMessageId
        }, (data) => {
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(message => {
                    this.addMessageToChat(message);
                });
            }
        });
    }
    
    updateNotifications() {
        $.get('/chat/api/notifications/', (data) => {
            if (data.unread_count > 0) {
                this.updateNotificationBadge(data.unread_count);
            }
        });
    }
    
    updateNotificationBadge(count) {
        let badge = document.querySelector('.notification-badge');
        if (!badge) {
            badge = document.createElement('span');
            badge.className = 'notification-badge';
            document.querySelector('.chat-sidebar-header h4').appendChild(badge);
        }
        badge.textContent = count;
    }
    
    addReaction(messageId, emoji) {
        $.post(`/chat/message/${messageId}/reaction/add/`, {
            emoji: emoji,
            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
        }, (data) => {
            if (data.success) {
                this.updateReactionDisplay(messageId, emoji, data.reaction_count, data.has_user_reacted);
            }
        });
    }
    
    removeReaction(messageId, emoji) {
        $.post(`/chat/message/${messageId}/reaction/remove/`, {
            emoji: emoji,
            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
        }, (data) => {
            if (data.success) {
                this.updateReactionDisplay(messageId, emoji, data.reaction_count, data.has_user_reacted);
            }
        });
    }
    
    toggleReaction(messageId, emoji) {
        const reactionElement = document.querySelector(`[data-message-id="${messageId}"] .reaction[data-emoji="${emoji}"]`);
        const hasReacted = reactionElement && reactionElement.classList.contains('user-reacted');
        
        if (hasReacted) {
            this.removeReaction(messageId, emoji);
        } else {
            this.addReaction(messageId, emoji);
        }
    }
    
    updateReactionDisplay(messageId, emoji, count, hasUserReacted) {
        const reactionsContainer = document.getElementById(`reactions-${messageId}`);
        if (!reactionsContainer) return;
        
        let reactionElement = reactionsContainer.querySelector(`[data-emoji="${emoji}"]`);
        
        if (count > 0) {
            if (!reactionElement) {
                reactionElement = document.createElement('span');
                reactionElement.className = 'reaction';
                reactionElement.dataset.emoji = emoji;
                reactionElement.dataset.messageId = messageId;
                reactionElement.textContent = emoji;
                reactionsContainer.appendChild(reactionElement);
            }
            
            reactionElement.textContent = `${emoji} ${count}`;
            reactionElement.classList.toggle('user-reacted', hasUserReacted);
        } else if (reactionElement) {
            reactionElement.remove();
        }
    }
    
    deleteMessage(messageId) {
        if (!confirm('Êtes-vous sûr de vouloir supprimer ce message ?')) {
            return;
        }
        
        $.post(`/chat/api/message/${messageId}/delete/`, {
            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
        }, (data) => {
            if (data.success) {
                const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
                if (messageElement) {
                    messageElement.remove();
                }
            } else {
                this.showError('Erreur lors de la suppression du message');
            }
        });
    }
    
    replyToMessage(messageId) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            const content = messageElement.querySelector('.message-text').textContent;
            const input = document.querySelector('input[name="content"]');
            if (input) {
                input.value = `@${messageId} ${content.substring(0, 50)}... `;
                input.focus();
            }
        }
    }
    
    toggleEmojiPicker() {
        const picker = document.querySelector('.emoji-picker');
        if (picker) {
            picker.style.display = picker.style.display === 'none' ? 'block' : 'none';
        } else {
            this.createEmojiPicker();
        }
    }
    
    createEmojiPicker() {
        const emojis = ['😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇', 
                       '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚',
                       '👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉',
                       '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔'];
        
        const picker = document.createElement('div');
        picker.className = 'emoji-picker';
        
        const grid = document.createElement('div');
        grid.className = 'emoji-grid';
        
        emojis.forEach(emoji => {
            const item = document.createElement('div');
            item.className = 'emoji-item';
            item.textContent = emoji;
            grid.appendChild(item);
        });
        
        picker.appendChild(grid);
        
        const inputContainer = document.querySelector('.chat-input');
        inputContainer.appendChild(picker);
    }
    
    hideEmojiPicker() {
        const picker = document.querySelector('.emoji-picker');
        if (picker) {
            picker.style.display = 'none';
        }
    }
    
    insertEmoji(emoji) {
        const input = document.querySelector('input[name="content"]');
        if (input) {
            const cursorPos = input.selectionStart;
            const textBefore = input.value.substring(0, cursorPos);
            const textAfter = input.value.substring(cursorPos);
            input.value = textBefore + emoji + textAfter;
            input.selectionStart = input.selectionEnd = cursorPos + emoji.length;
            input.focus();
        }
        this.hideEmojiPicker();
    }
    
    toggleFileUpload() {
        const fileInput = document.getElementById('file-upload');
        if (fileInput) {
            fileInput.click();
        }
    }
    
    handleFileUpload(file) {
        if (!file) return;
        
        // Vérifier la taille du fichier (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            this.showError('Le fichier est trop volumineux (max 10MB)');
            return;
        }
        
        // Vérifier le type de fichier
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'video/mp4', 'application/pdf'];
        if (!allowedTypes.includes(file.type)) {
            this.showError('Type de fichier non autorisé');
            return;
        }
        
        // Le fichier sera envoyé avec le prochain message
        this.showSuccess(`Fichier "${file.name}" prêt à être envoyé`);
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.innerHTML = `
            ${message}
            <button type="button" class="close" data-dismiss="alert">
                <span>&times;</span>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        // Supprimer automatiquement après 5 secondes
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    // Méthodes pour gérer les événements WebSocket
    handleNewMessage(message) {
        if (message.room_id === this.currentRoomId) {
            this.addMessageToChat(message);
        } else {
            // Mettre à jour le badge de notification
            this.updateNotificationBadge(1);
        }
    }
    
    handleMessageUpdated(message) {
        const messageElement = document.querySelector(`[data-message-id="${message.id}"]`);
        if (messageElement) {
            const contentElement = messageElement.querySelector('.message-text');
            if (contentElement) {
                contentElement.innerHTML = this.formatMessageContent(message.content);
            }
        }
    }
    
    handleMessageDeleted(messageId) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            messageElement.remove();
        }
    }
    
    handleReactionAdded(messageId, emoji, count) {
        this.updateReactionDisplay(messageId, emoji, count, false);
    }
    
    handleReactionRemoved(messageId, emoji, count) {
        this.updateReactionDisplay(messageId, emoji, count, false);
    }
    
    handleTyping(userId, roomId) {
        if (roomId === this.currentRoomId) {
            // Afficher l'indicateur de frappe
            this.showTypingIndicator(userId);
        }
    }
    
    handleUserOnline(userId) {
        // Mettre à jour le statut de l'utilisateur
        const userElement = document.querySelector(`[data-user-id="${userId}"]`);
        if (userElement) {
            userElement.classList.add('online');
        }
    }
    
    handleUserOffline(userId) {
        // Mettre à jour le statut de l'utilisateur
        const userElement = document.querySelector(`[data-user-id="${userId}"]`);
        if (userElement) {
            userElement.classList.remove('online');
        }
    }
    
    showTypingIndicator(userId) {
        // Afficher l'indicateur de frappe
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = '<span>Quelqu'un est en train d'écrire...</span>';
        
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            chatMessages.appendChild(indicator);
            this.scrollToBottom();
            
            // Supprimer après 3 secondes
            setTimeout(() => {
                if (indicator.parentNode) {
                    indicator.parentNode.removeChild(indicator);
                }
            }, 3000);
        }
    }
    
    destroy() {
        if (this.messageInterval) {
            clearInterval(this.messageInterval);
        }
        if (this.notificationInterval) {
            clearInterval(this.notificationInterval);
        }
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Initialiser le système de chat
let chatSystem;
$(document).ready(function() {
    chatSystem = new ChatSystem();
    
    // Nettoyer lors de la fermeture de la page
    $(window).on('beforeunload', function() {
        if (chatSystem) {
            chatSystem.destroy();
        }
    });
});

// Fonctions globales pour les templates
function toggleEmojiPicker() {
    if (chatSystem) {
        chatSystem.toggleEmojiPicker();
    }
}

function toggleFileUpload() {
    if (chatSystem) {
        chatSystem.toggleFileUpload();
    }
}

function addReaction(messageId, emoji) {
    if (chatSystem) {
        chatSystem.addReaction(messageId, emoji);
    }
}

function deleteMessage(messageId) {
    if (chatSystem) {
        chatSystem.deleteMessage(messageId);
    }
}

function replyToMessage(messageId) {
    if (chatSystem) {
        chatSystem.replyToMessage(messageId);
    }
}



