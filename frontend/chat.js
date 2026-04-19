// chat.js
// AI Chat functionality for EduSolve

let currentSessionId = null;

// ============================================
// Create New Doubt Session
// ============================================
async function createDoubtSession(subject) {
    try {
        const validSubject = subject || 'mathematics'; 
        
        const response = await apiCall(API_ENDPOINTS.doubtSessions, 'POST', {
            subject: validSubject,
            title: 'AI Chat Session' 
        });
        
        currentSessionId = response.id;
        
        window.currentSessionId = response.id;

        console.log('Session created:', currentSessionId);
        
        return response;
    } catch (error) {
        console.error('Failed to create session:', error);
        // We removed the annoying alert() box here. We will handle the error in the chat UI instead.
        return null; 
    }
}

// ============================================
// Send Message to AI
// ============================================
async function sendMessageToAI(message) {
    // 1. Show user message immediately! (Don't wait for the backend)
    displayMessage(message, 'student');
    
    // 2. Show the typing indicator
    showAITyping();

    // 3. Ensure we have a valid session before sending the message
    if (!currentSessionId) {
        const session = await createDoubtSession('mathematics');
        if (!session) {
            // If session creation fails, hide typing and show a clear error in the chat
            hideAITyping();
            displayMessage('Failed to connect. Is your Django server running?', 'ai', true);
            return;
        }
    }
    
    // 4. Send the actual message to the AI
    try {
        const response = await apiCall(API_ENDPOINTS.chatMessages, 'POST', {
            session: currentSessionId,
            sender_type: 'student',
            content: message
        });
        
        hideAITyping();
        
        if (response.success && response.ai_message) {
            displayMessage(response.ai_message.content, 'ai');
        } else {
            displayMessage('Sorry, the AI engine encountered an error. Please try again.', 'ai', true);
        }
        
    } catch (error) {
        hideAITyping();
        console.error('Send message error:', error);
        displayMessage('Connection error. Please check your internet or backend server.', 'ai', true);
    }
}

// ============================================
// Display Message in Chat UI
// ============================================
function displayMessage(content, senderType, isError = false) {
    const chatContainer = document.getElementById('chat-messages');
    if (!chatContainer) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${senderType}-message`;
    
    if (isError) {
        messageDiv.classList.add('error-message');
    }
    
    // Format AI messages with proper styling
    if (senderType === 'ai') {
        messageDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="message-text">${formatAIResponse(content)}</div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${content}</div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            </div>
            <div class="message-avatar">👤</div>
        `;
    }
    
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// ============================================
// Format AI Response
// ============================================
function formatAIResponse(content) {
    // Convert line breaks to <br>
    let formatted = content.replace(/\n/g, '<br>');
    
    // Bold section headers (EXPLANATION:, KEY FORMULA:, etc.)
    formatted = formatted.replace(/([A-Z\s]+:)/g, '<strong>$1</strong>');
    
    return formatted;
}

// ============================================
// Show/Hide AI Typing Indicator
// ============================================
function showAITyping() {
    const chatContainer = document.getElementById('chat-messages');
    if (!chatContainer) return;
    
    const typingDiv = document.createElement('div');
    typingDiv.id = 'ai-typing';
    typingDiv.className = 'chat-message ai-message typing';
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hideAITyping() {
    const typingDiv = document.getElementById('ai-typing');
    if (typingDiv) {
        typingDiv.remove();
    }
}

// ============================================
// Handle Chat Form Submission
// ============================================
function handleChatSubmit(event) {
    event.preventDefault();
    
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Send message
    sendMessageToAI(message);
    
    // Clear input
    input.value = '';
}

// ============================================
// Load Chat History
// ============================================
async function loadChatHistory(sessionId) {
    try {
        const response = await apiCall(`${API_ENDPOINTS.doubtSessions}${sessionId}/messages/`);
        
        const chatContainer = document.getElementById('chat-messages');
        chatContainer.innerHTML = ''; // Clear existing
        
        if (response.messages && response.messages.length > 0) {
            response.messages.forEach(msg => {
                displayMessage(msg.content, msg.sender_type);
            });
        } else {
            // Show welcome message
            displayMessage(
                'Hi! I\'m your AI tutor. Ask me anything about Science or Maths!',
                'ai'
            );
        }
        
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

// ============================================
// Initialize Chat
// ============================================
function initializeChat() {
    // Check if on chat page
    if (!document.getElementById('chat-messages')) return;
    
    console.log('Initializing chat...');
    
    // Show welcome message
    displayMessage(
        'Hi! I\'m your AI tutor for Class 9 & 10. Ask me anything about Science or Maths!',
        'ai'
    );
    
    // Set up form handler
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatSubmit);
    }
}

// Auto-initialize on page load
document.addEventListener('DOMContentLoaded', initializeChat);