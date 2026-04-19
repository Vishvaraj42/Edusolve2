// api-config.js
// Backend API Configuration for EduSolve

// 1. Detect if the user is on localhost or the live internet

// 2. Dynamically switch the backend URL!
const API_BASE_URL = 'https://edusolve2.onrender.com';

const API_ENDPOINTS = {
    // Authentication
    register: `${API_BASE_URL}/api/auth/register/`,
    login: `${API_BASE_URL}/api/auth/login/`,
    logout: `${API_BASE_URL}/api/auth/logout/`,
    profile: `${API_BASE_URL}/api/auth/profile/`,
    changePassword: `${API_BASE_URL}/api/auth/change-password/`,
    
    // Doubts & Chat
    doubtSessions: `${API_BASE_URL}/api/doubts/sessions/`,
    chatMessages: `${API_BASE_URL}/api/doubts/messages/`,
    doubtStats: `${API_BASE_URL}/api/doubts/stats/`,
    
    // Practice Questions
    practiceQuestions: `${API_BASE_URL}/api/practice/questions/`,
    submitAnswer: `${API_BASE_URL}/api/practice/answers/`,
    myAnswers: `${API_BASE_URL}/api/practice/answers/`,
    practiceStats: `${API_BASE_URL}/api/practice/answers/stats/`,
    
    // Community Forum (UPDATED TO MATCH NEW DJANGO APP)
    communityChannels: `${API_BASE_URL}/api/community/channels/`,
    communityPosts: `${API_BASE_URL}/api/community/posts/`,
};

// ============================================
// Helper Functions
// ============================================

// Get auth token from localStorage
function getAuthToken() {
    return localStorage.getItem('access_token');
}

// Get headers with authentication
function getAuthHeaders() {
    const token = getAuthToken();
    return {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
    };
}

// Make API calls with error handling
async function apiCall(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: getAuthHeaders(),
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        
        // Handle unauthorized (token expired)
        if (response.status === 401) {
            console.log('Token expired, redirecting to login...');
            localStorage.clear();
            // Use navigateTo instead of window.location
            if (typeof navigateTo === 'function') {
                navigateTo('auth');
            }
            throw new Error('Unauthorized - please login again');
        }
        
        // Handle other HTTP errors
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            // Throws the exact detail string we programmed into our backend
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Check if user is authenticated
function isAuthenticated() {
    return !!getAuthToken();
}

// Redirect to auth view if not authenticated
function requireAuth() {
    if (!isAuthenticated()) {
        if (typeof navigateTo === 'function') {
            navigateTo('auth');
        }
    }
}