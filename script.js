// Global variables
let currentSessionId = null;
let currentLanguage = 'en';
let isTyping = false;

// API Configuration
const API_BASE_URL = 'http://localhost:8000'; // Change this for production

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const languageSelect = document.getElementById('languageSelect');
const typingIndicator = document.getElementById('typingIndicator');
const statusIndicator = document.getElementById('statusIndicator');
const sessionInfo = document.getElementById('sessionInfo');
const sidebar = document.getElementById('sidebar');
const settingsModal = document.getElementById('settingsModal');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkServerStatus();
});

function initializeApp() {
    // Generate session ID
    currentSessionId = generateSessionId();
    updateSessionInfo();
    
    // Load user preferences
    loadUserPreferences();
    
    // Hide welcome message after first interaction
    hideWelcomeAfterFirstMessage();
    
    // Initialize language
    currentLanguage = languageSelect.value;
}

function setupEventListeners() {
    // Send message events
    sendButton.addEventListener('click', handleSendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    // Language change
    languageSelect.addEventListener('change', function(e) {
        currentLanguage = e.target.value;
        saveUserPreferences();
        updateWelcomeMessage();
    });
    
    // Quick action buttons
    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const message = this.dataset.message;
            sendMessage(message);
        });
    });
    
    // FAQ items
    document.querySelectorAll('.faq-item').forEach(btn => {
        btn.addEventListener('click', function() {
            const message = this.dataset.message;
            sendMessage(message);
            closeSidebar();
        });
    });
    
    // Action buttons
    document.getElementById('helpButton').addEventListener('click', toggleSidebar);
    document.getElementById('settingsButton').addEventListener('click', openSettings);
    document.getElementById('clearButton').addEventListener('click', clearChat);
    
    // Sidebar controls
    document.getElementById('closeSidebar').addEventListener('click', closeSidebar);
    
    // Settings modal controls
    document.getElementById('closeSettings').addEventListener('click', closeSettings);
    document.getElementById('themeSelect').addEventListener('change', changeTheme);
    document.getElementById('fontSizeSelect').addEventListener('change', changeFontSize);
    document.getElementById('soundToggle').addEventListener('change', toggleSound);
    
    // Close modal when clicking outside
    settingsModal.addEventListener('click', function(e) {
        if (e.target === settingsModal) {
            closeSettings();
        }
    });
    
    // Auto-resize input
    messageInput.addEventListener('input', autoResizeInput);
    
    // Focus management
    messageInput.focus();
}

async function handleSendMessage() {
    const message = messageInput.value.trim();
    if (!message || isTyping) return;
    
    // Clear input and disable send button
    messageInput.value = '';
    sendButton.disabled = true;
    
    try {
        await sendMessage(message);
    } catch (error) {
        console.error('Error sending message:', error);
        addErrorMessage('Failed to send message. Please try again.');
    } finally {
        sendButton.disabled = false;
        messageInput.focus();
    }
}

async function sendMessage(message) {
    // Hide welcome message on first interaction
    hideWelcomeMessage();
    
    // Add user message to chat
    addMessage('user', message);
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId,
                language: currentLanguage
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Add bot response
        addMessage('bot', data.response, {
            confidence: data.confidence,
            detectedLanguage: data.detected_language,
            needsHuman: data.needs_human,
            contact: data.suggested_contact
        });
        
        // Update session info
        updateSessionInfo();
        
        // Play notification sound
        playNotificationSound();
        
    } catch (error) {
        hideTypingIndicator();
        console.error('Error:', error);
        addErrorMessage('Sorry, I\'m having trouble connecting to the server. Please try again later.');
        updateServerStatus(false);
    }
}

function addMessage(sender, text, metadata = {}) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const messageText = document.createElement('p');
    messageText.className = 'message-text';
    messageText.textContent = text;
    
    content.appendChild(messageText);
    
    // Add metadata for bot messages
    if (sender === 'bot' && metadata) {
        const meta = document.createElement('div');
        meta.className = 'message-meta';
        
        const leftMeta = document.createElement('div');
        if (metadata.confidence !== undefined) {
            const confidenceBadge = document.createElement('span');
            confidenceBadge.className = 'confidence-badge';
            confidenceBadge.textContent = `${Math.round(metadata.confidence * 100)}%`;
            leftMeta.appendChild(confidenceBadge);
        }
        
        const rightMeta = document.createElement('div');
        if (metadata.detectedLanguage) {
            const langBadge = document.createElement('span');
            langBadge.className = 'language-badge';
            langBadge.textContent = getLanguageName(metadata.detectedLanguage);
            rightMeta.appendChild(langBadge);
        }
        
        meta.appendChild(leftMeta);
        meta.appendChild(rightMeta);
        content.appendChild(meta);
        
        // Add human handoff suggestion if needed
        if (metadata.needsHuman && metadata.contact) {
            const contactDiv = document.createElement('div');
            contactDiv.style.marginTop = '0.5rem';
            contactDiv.style.fontSize = '0.875rem';
            contactDiv.style.opacity = '0.8';
            contactDiv.innerHTML = `
                <p><strong>Need more help?</strong> Contact us:</p>
                <p><i class="fas fa-phone"></i> ${metadata.contact.phone || 'N/A'}</p>
                <p><i class="fas fa-envelope"></i> ${metadata.contact.email || 'N/A'}</p>
            `;
            content.appendChild(contactDiv);
        }
    }
    
    // Add timestamp
    const timestamp = document.createElement('div');
    timestamp.className = 'message-meta';
    timestamp.style.marginTop = '0.25rem';
    timestamp.style.fontSize = '0.75rem';
    timestamp.style.opacity = '0.6';
    timestamp.textContent = new Date().toLocaleTimeString();
    content.appendChild(timestamp);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function addErrorMessage(text) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message bot error';
    errorDiv.innerHTML = `
        <div class="message-avatar" style="background: var(--danger-color);">
            <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="message-content" style="border-color: var(--danger-color); background: rgba(239, 68, 68, 0.1);">
            <p class="message-text">${text}</p>
        </div>
    `;
    chatMessages.appendChild(errorDiv);
    scrollToBottom();
}

function showTypingIndicator() {
    isTyping = true;
    typingIndicator.style.display = 'flex';
    scrollToBottom();
}

function hideTypingIndicator() {
    isTyping = false;
    typingIndicator.style.display = 'none';
}

function scrollToBottom() {
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

function hideWelcomeMessage() {
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.style.display = 'none';
    }
}

function hideWelcomeAfterFirstMessage() {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                // Check if a message was added
                for (let node of mutation.addedNodes) {
                    if (node.classList && node.classList.contains('message')) {
                        hideWelcomeMessage();
                        observer.disconnect();
                        break;
                    }
                }
            }
        });
    });
    
    observer.observe(chatMessages, { childList: true });
}

function updateWelcomeMessage() {
    const welcomeContent = document.querySelector('.welcome-content');
    if (!welcomeContent) return;
    
    const welcomeMessages = {
        'en': {
            title: 'Welcome to Campus Assistant!',
            description: 'I can help you with information about:',
            helpText: 'Type your question in any supported language!'
        },
        'hi': {
            title: 'कैंपस सहायक में आपका स्वागत है!',
            description: 'मैं इन चीजों के बारे में जानकारी दे सकता हूं:',
            helpText: 'किसी भी समर्थित भाषा में अपना प्रश्न टाइप करें!'
        },
        'gu': {
            title: 'કેમ્પસ સહાયકમાં આપનું સ્વાગત છે!',
            description: 'હું આ વિશે માહિતી આપી શકું છું:',
            helpText: 'કોઈપણ સમર્થિત ભાષામાં તમારો પ્રશ્ન ટાઈપ કરો!'
        },
        'mr': {
            title: 'कॅम्पस सहाय्यकामध्ये आपले स्वागत!',
            description: 'मी याबद्दल माहिती देऊ शकतो:',
            helpText: 'कोणत्याही समर्थित भाषेत तुमचा प्रश्न टाइप करा!'
        },
        'raj': {
            title: 'कैंपस सहायक में थारो स्वागत है!',
            description: 'मैं इन चीजां रे बारे में जानकारी दे सकूं:',
            helpText: 'कोई भी समर्थित भाषा में अपनो सवाल टाइप करो!'
        }
    };
    
    const messages = welcomeMessages[currentLanguage] || welcomeMessages['en'];
    
    const titleElement = welcomeContent.querySelector('h2');
    const descElement = welcomeContent.querySelector('p');
    const helpElement = welcomeContent.querySelector('.help-text');
    
    if (titleElement) titleElement.textContent = messages.title;
    if (descElement) descElement.textContent = messages.description;
    if (helpElement) helpElement.textContent = messages.helpText;
}

// Utility functions
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function updateSessionInfo() {
    if (sessionInfo) {
        const messageCount = chatMessages.children.length;
        sessionInfo.textContent = `Session: ${currentSessionId.substr(-8)} | Messages: ${messageCount}`;
    }
}

function getLanguageName(langCode) {
    const languageNames = {
        'en': 'EN',
        'hi': 'HI',
        'gu': 'GU',
        'mr': 'MR',
        'raj': 'RAJ'
    };
    return languageNames[langCode] || langCode.toUpperCase();
}

async function checkServerStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        updateServerStatus(response.ok);
    } catch (error) {
        updateServerStatus(false);
    }
}

function updateServerStatus(isOnline) {
    if (statusIndicator) {
        statusIndicator.textContent = isOnline ? '🟢 Online' : '🔴 Offline';
        statusIndicator.style.color = isOnline ? 'var(--accent-color)' : 'var(--danger-color)';
    }
}

// UI Controls
function toggleSidebar() {
    sidebar.classList.toggle('active');
}

function closeSidebar() {
    sidebar.classList.remove('active');
}

function openSettings() {
    settingsModal.classList.add('active');
}

function closeSettings() {
    settingsModal.classList.remove('active');
}

function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        chatMessages.innerHTML = '';
        updateSessionInfo();
        
        // Show welcome message again
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'block';
        }
    }
}

// Settings functions
function changeTheme(e) {
    const theme = e.target.value;
    document.body.setAttribute('data-theme', theme);
    saveUserPreferences();
}

function changeFontSize(e) {
    const fontSize = e.target.value;
    document.body.setAttribute('data-font-size', fontSize);
    saveUserPreferences();
}

function toggleSound(e) {
    const soundEnabled = e.target.checked;
    localStorage.setItem('soundEnabled', soundEnabled);
}

function autoResizeInput() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
}

function playNotificationSound() {
    const soundEnabled = localStorage.getItem('soundEnabled') !== 'false';
    if (soundEnabled) {
        // Create a simple beep sound
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
        
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.3);
    }
}

// Local storage functions
function saveUserPreferences() {
    const preferences = {
        language: currentLanguage,
        theme: document.body.getAttribute('data-theme') || 'light',
        fontSize: document.body.getAttribute('data-font-size') || 'medium',
        soundEnabled: document.getElementById('soundToggle')?.checked !== false
    };
    
    localStorage.setItem('chatbotPreferences', JSON.stringify(preferences));
}

function loadUserPreferences() {
    try {
        const preferences = JSON.parse(localStorage.getItem('chatbotPreferences') || '{}');
        
        // Set language
        if (preferences.language) {
            languageSelect.value = preferences.language;
            currentLanguage = preferences.language;
        }
        
        // Set theme
        if (preferences.theme) {
            document.body.setAttribute('data-theme', preferences.theme);
            const themeSelect = document.getElementById('themeSelect');
            if (themeSelect) themeSelect.value = preferences.theme;
        }
        
        // Set font size
        if (preferences.fontSize) {
            document.body.setAttribute('data-font-size', preferences.fontSize);
            const fontSizeSelect = document.getElementById('fontSizeSelect');
            if (fontSizeSelect) fontSizeSelect.value = preferences.fontSize;
        }
        
        // Set sound preference
        const soundToggle = document.getElementById('soundToggle');
        if (soundToggle) {
            soundToggle.checked = preferences.soundEnabled !== false;
        }
        
        updateWelcomeMessage();
    } catch (error) {
        console.error('Error loading user preferences:', error);
    }
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    updateServerStatus(false);
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    updateServerStatus(false);
});

// Periodic health check
setInterval(checkServerStatus, 30000); // Check every 30 seconds

// Export for potential embedding
window.CampusChatbot = {
    sendMessage,
    clearChat,
    updateLanguage: (lang) => {
        languageSelect.value = lang;
        currentLanguage = lang;
        updateWelcomeMessage();
    },
    getCurrentSession: () => currentSessionId,
    isOnline: () => statusIndicator?.textContent.includes('Online')
};
