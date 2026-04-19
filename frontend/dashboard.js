// dashboard.js
// Dashboard functionality for EduSolve - Updated to use working endpoints

// ============================================
// Load User Profile (instead of stats)
// ============================================
async function loadUserProfile() {
    const statsContainer = document.getElementById('practice-stats');
    
    if (!statsContainer) return;
    
    try {
        statsContainer.innerHTML = '<p style="color: #888;">Loading your profile...</p>';
        
        const profile = await apiCall(API_ENDPOINTS.profile);
        
        const profileHTML = `
            <div class="glass-card" style="padding: 1.5rem; margin-bottom: 2rem; background: rgba(255,255,255,0.05); border-radius: 1rem;">
                <h3 style="margin-bottom: 1rem; font-size: 1.2rem;">📊 Your Profile</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                    <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 0.5rem;">
                        <p style="color: #888; font-size: 0.85rem; margin-bottom: 0.5rem;">Username</p>
                        <p style="font-weight: 600; font-size: 1.1rem;">${profile.username}</p>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 0.5rem;">
                        <p style="color: #888; font-size: 0.85rem; margin-bottom: 0.5rem;">Grade</p>
                        <p style="font-weight: 600; font-size: 1.1rem;">${profile.grade || 'N/A'}</p>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 0.5rem;">
                        <p style="color: #888; font-size: 0.85rem; margin-bottom: 0.5rem;">Email</p>
                        <p style="font-weight: 600; font-size: 1.1rem;">${profile.email || 'N/A'}</p>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 0.5rem;">
                        <p style="color: #888; font-size: 0.85rem; margin-bottom: 0.5rem;">🏆 Points</p>
                        <p style="font-weight: 600; font-size: 1.1rem; color: #a855f7;">${profile.points || 0}</p>
                    </div>
                </div>
            </div>
        `;
        
        statsContainer.innerHTML = profileHTML;
    } catch (error) {
        console.error('Failed to load profile:', error);
        statsContainer.innerHTML = `
            <div style="padding: 1rem; background: rgba(255,68,68,0.1); border-radius: 0.5rem; color: #ff4444;">
                <p>Unable to load profile. Please try refreshing the page.</p>
            </div>
        `;
    }
}

// ============================================
// Load Recent Practice Questions (Optional)
// ============================================
async function loadRecentQuestions() {
    const questionsContainer = document.getElementById('recent-questions');
    
    if (!questionsContainer) return;
    
    try {
        questionsContainer.innerHTML = '<p style="color: #888;">Loading recent questions...</p>';
        
        // Try to get questions - limit to 5
        const response = await apiCall(`${API_ENDPOINTS.practiceQuestions}?limit=5`);
        
        // Handle both paginated and non-paginated responses
        const questions = response.results || response;
        
        if (questions && questions.length > 0) {
            const questionsHTML = `
                <div class="glass-card" style="padding: 1.5rem; background: rgba(255,255,255,0.05); border-radius: 1rem;">
                    <h3 style="margin-bottom: 1rem; font-size: 1.2rem;">📚 Recent Practice Questions</h3>
                    <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                        ${questions.map((q, index) => `
                            <div onclick="openOldPracticeSession('${q.related_session || q.session || 'null'}')"
                                 style="padding: 0.75rem; background: rgba(255,255,255,0.03); border-radius: 0.5rem; border-left: 3px solid #a855f7; cursor: pointer; transition: background 0.2s;"
                                 onmouseover="this.style.background='rgba(107,76,230,0.1)'"
                                 onmouseout="this.style.background='rgba(255,255,255,0.03)'">
                                <p style="font-size: 0.9rem; margin-bottom: 0.25rem;">
                                    <strong>${index + 1}.</strong> ${q.question_text.substring(0, 80)}${q.question_text.length > 80 ? '...' : ''}
                                </p>
                                <div style="display: flex; gap: 0.5rem; font-size: 0.75rem; color: #888;">
                                    <span style="padding: 0.25rem 0.5rem; background: rgba(168,85,247,0.2); border-radius: 0.25rem; color: #a855f7;">
                                        ${q.difficulty || 'N/A'}
                                    </span>
                                    <span>${q.topic || 'General'}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            
            questionsContainer.innerHTML = questionsHTML;
        } else {
            questionsContainer.innerHTML = `
                <div class="glass-card" style="padding: 1.5rem; background: rgba(255,255,255,0.05); border-radius: 1rem;">
                    <p style="color: #888; text-align: center;">No practice questions available yet.</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Failed to load recent questions:', error);
        // Silently fail - just hide the section
        questionsContainer.innerHTML = '';
    }
}

// ============================================
// Initialize Dashboard
// ============================================
function initDashboard() {
    console.log('Initializing dashboard...');
    
    // Load profile (replaces stats)
    loadUserProfile();
    
    // Try to load recent questions (optional)
    loadRecentQuestions();
}

// ============================================
// Auto-run on page load
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    // Only run if we're on the dashboard view
    if (document.getElementById('practice-stats')) {
        console.log('Dashboard detected, loading data...');
        initDashboard();
    }
});

// ============================================
// Expose function globally for manual refresh
// ============================================
window.refreshDashboard = function() {
    console.log('Refreshing dashboard...');
    initDashboard();
};

// ============================================
// Navigate to specific old practice session
// ============================================
window.openOldPracticeSession = function(sessionId) {
    console.log("Attempting to load session ID:", sessionId);

    // If the question is from before our database fixes, alert the user
    if (!sessionId || sessionId === 'null' || sessionId === 'undefined') {
        alert("Oops! This is a legacy question that isn't linked to a specific Chat Session. Try asking a new doubt!");
        return;
    }

    // Set the global session ID so practice.js knows what to load
    window.currentSessionId = sessionId;
    
    // Trigger the router
    if (typeof window.navigateTo === 'function') {
        window.navigateTo('practice');
    } else {
        console.error("Router function not found!");
    }
};