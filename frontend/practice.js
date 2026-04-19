// practice.js
// Handles fetching and answering practice questions

// ============================================
// Load Practice Questions
// ============================================
async function loadPracticeQuestions() {
    const container = document.getElementById('practice-container');
    if (!container) return;

    // =========================================================
    // FIX 3: THE "GHOST DATA" WIPER
    // Instantly clear the screen before doing anything else!
    // =========================================================
    container.innerHTML = `
        <div style="text-align: center; color: var(--color-text-muted); padding: 2rem;">
            <div class="typing-indicator" style="justify-content: center; margin-bottom: 1rem;">
                <span></span><span></span><span></span>
            </div>
            Loading your personal practice questions...
        </div>`;

    // 1. Check if we actually have an active chat session!
    if (!window.currentSessionId) {
        container.innerHTML = `
            <div class="empty-state">   
                <div class="empty-icon">💬</div>
                <h3>No Active Session</h3>
                <p>Please go to the 'Solve' tab and ask a doubt first. I will generate practice questions based on our chat!</p>
            </div>`;
        return;
    }

    try {
        // 2. Fetch questions specifically linked to this session!
        const timestamp = new Date().getTime();
        const url = `${API_ENDPOINTS.practiceQuestions}?session=${window.currentSessionId}&t=${timestamp}`;
        
        const response = await apiCall(url);
        const questions = response.results || response;

        // 3. Handle empty state if the AI hasn't finished generating them yet
        if (!questions || questions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">⏳</div>
                    <h3>Questions Generating...</h3>
                    <p>Your practice questions are being created in the background. Please click back to this tab in a few seconds!</p>
                </div>`;
            return;
        }

        renderQuestions(questions, container);

    } catch (error) {
        console.error('Failed to load practice questions:', error);
        container.innerHTML = `
            <div style="padding: 1.5rem; background: rgba(255, 68, 68, 0.1); border-left: 4px solid #ff4444; border-radius: 8px;">
                <h4 style="color: #ff4444; margin-bottom: 0.5rem;">Connection Error</h4>
                <p>Could not load questions. Make sure your Django backend is running.</p>
            </div>`;
    }
}

// ============================================
// Render Questions to the DOM
// ============================================
function renderQuestions(questions, container) {
    container.innerHTML = ''; // Clear loading state

    questions.forEach((q, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.style.cssText = `
            background: rgba(255, 255, 255, 0.5);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.02);
            margin-bottom: 1.5rem;
        `;

        const optA = q.option_a || 'True';
        const optB = q.option_b || 'False';
        const optC = q.option_c || 'Not enough information';
        const optD = q.option_d || 'None of the above';

        questionDiv.innerHTML = `
            <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                <span style="font-weight: 600; color: var(--color-accent);">Question ${index + 1}</span>
                <span style="font-size: 0.8rem; background: rgba(107, 76, 230, 0.1); padding: 0.2rem 0.6rem; border-radius: 99px; color: var(--color-accent);">${q.topic || 'General'}</span>
            </div>
            <p style="font-size: 1.1rem; margin-bottom: 1.5rem; color: var(--color-text-main);">${q.question_text || q.question}</p>
            
            <div id="options-${q.id}" style="display: flex; flex-direction: column; gap: 0.8rem; margin-bottom: 1.5rem;">
                <label style="display: flex; gap: 0.5rem; cursor: pointer; padding: 0.8rem; border: 1px solid var(--glass-border); border-radius: 8px; background: rgba(255,255,255,0.8);">
                    <input type="radio" name="q-${q.id}" value="A"> <span><strong>A)</strong> ${optA}</span>
                </label>
                <label style="display: flex; gap: 0.5rem; cursor: pointer; padding: 0.8rem; border: 1px solid var(--glass-border); border-radius: 8px; background: rgba(255,255,255,0.8);">
                    <input type="radio" name="q-${q.id}" value="B"> <span><strong>B)</strong> ${optB}</span>
                </label>
                <label style="display: flex; gap: 0.5rem; cursor: pointer; padding: 0.8rem; border: 1px solid var(--glass-border); border-radius: 8px; background: rgba(255,255,255,0.8);">
                    <input type="radio" name="q-${q.id}" value="C"> <span><strong>C)</strong> ${optC}</span>
                </label>
                <label style="display: flex; gap: 0.5rem; cursor: pointer; padding: 0.8rem; border: 1px solid var(--glass-border); border-radius: 8px; background: rgba(255,255,255,0.8);">
                    <input type="radio" name="q-${q.id}" value="D"> <span><strong>D)</strong> ${optD}</span>
                </label>
            </div>

            <button onclick="submitAnswer(${q.id})" id="btn-${q.id}" class="btn btn-primary" style="align-self: flex-start;">
                Submit Answer
            </button>
            <div id="feedback-${q.id}" style="margin-top: 1rem; display: none; padding: 1rem; border-radius: 8px;"></div>
        `;
        
        container.appendChild(questionDiv);
    });
}

// ============================================
// Submit Answer to API
// ============================================
async function submitAnswer(questionId) {
    const selectedOption = document.querySelector(`input[name="q-${questionId}"]:checked`);
    const feedbackDiv = document.getElementById(`feedback-${questionId}`);
    const submitBtn = document.getElementById(`btn-${questionId}`);

    if (!selectedOption) {
        alert("Please select an option before submitting.");
        return;
    }

    const answerLetter = selectedOption.value;

    const allRadios = document.querySelectorAll(`input[name="q-${questionId}"]`);
    allRadios.forEach(r => r.disabled = true);
    submitBtn.disabled = true;
    
    feedbackDiv.style.display = 'block';
    feedbackDiv.style.background = 'rgba(107, 76, 230, 0.1)';
    feedbackDiv.innerHTML = '<p style="color: var(--color-accent);">Evaluating...</p>';

    try {
        const response = await apiCall(API_ENDPOINTS.submitAnswer, 'POST', {
            question: questionId,
            selected_answer: answerLetter 
        });

        if (response.is_correct) {
            feedbackDiv.style.background = 'rgba(39, 201, 63, 0.1)';
            feedbackDiv.style.borderLeft = '4px solid #27c93f';
            feedbackDiv.innerHTML = `<strong>✅ Correct!</strong><p style="margin-top: 0.5rem;">${response.explanation || 'Great job!'}</p>`;
        } else {
            feedbackDiv.style.background = 'rgba(255, 68, 68, 0.1)';
            feedbackDiv.style.borderLeft = '4px solid #ff4444';
            feedbackDiv.innerHTML = `<strong>❌ Not quite.</strong><p style="margin-top: 0.5rem;">The correct answer was <strong>${response.correct_answer || 'different'}</strong>. ${response.explanation || 'Keep practicing!'}</p>`;
            
            allRadios.forEach(r => r.disabled = false);
            submitBtn.disabled = false;
        }

   } catch (error) {
        console.error('Submit answer error:', error);
        feedbackDiv.style.background = 'rgba(255, 68, 68, 0.1)';
        feedbackDiv.style.borderLeft = '4px solid #ff4444';
        
        feedbackDiv.innerHTML = `<p style="color: #ff4444;"><strong>Error:</strong> ${error.message}</p>`;
        
        allRadios.forEach(r => r.disabled = false);
        submitBtn.disabled = false;
    }
}

// ============================================
// Hook into Navigation
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    const originalNavigateTo = window.navigateTo;
    
    window.navigateTo = function(viewId) {
        if (typeof originalNavigateTo === 'function') {
            originalNavigateTo(viewId); 
        }
        
        if (viewId === 'practice') {
            loadPracticeQuestions();
        }
    };

    if (window.location.hash === '#practice') {
        loadPracticeQuestions();
    }
});