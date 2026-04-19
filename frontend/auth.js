// auth.js

// ============================================
// Login Function
// ============================================
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('login-error');
    const submitBtn = event.target.querySelector('button[type="submit"]');
    
    const originalBtnText = submitBtn.textContent;
    submitBtn.textContent = 'Logging in...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch(API_ENDPOINTS.login, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (data.access) localStorage.setItem('access_token', data.access);
            else if (data.tokens && data.tokens.access) localStorage.setItem('access_token', data.tokens.access);
            
            if (data.refresh) localStorage.setItem('refresh_token', data.refresh);
            else if (data.tokens && data.tokens.refresh) localStorage.setItem('refresh_token', data.tokens.refresh);
            
            localStorage.setItem('username', username);
            window.location.hash = 'dashboard';
        } else {
            errorDiv.textContent = data.detail || data.error || 'Login failed. Please check your credentials.';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.textContent = 'Connection error. Is the backend server running?';
        errorDiv.style.display = 'block';
    } finally {
        submitBtn.textContent = originalBtnText;
        submitBtn.disabled = false;
    }
}

// ============================================
// Registration Step 1: Submit Details & Request OTP
// ============================================
async function handleRegister(event) {
    event.preventDefault();
    
    const firstName = document.getElementById('reg-firstname').value;
    const lastName = document.getElementById('reg-lastname').value;
    const email = document.getElementById('reg-email').value;
    const username = document.getElementById('reg-username').value;
    const phone = document.getElementById('reg-phone').value;
    const grade = document.getElementById('reg-grade').value;
    const password = document.getElementById('reg-password').value;
    const passwordConfirm = document.getElementById('reg-password-confirm').value;
    
    const errorDiv = document.getElementById('register-error');
    const submitBtn = document.getElementById('reg-submit-btn');

    if (password !== passwordConfirm) {
        errorDiv.innerText = "Passwords do not match!";
        errorDiv.style.display = 'block';
        return;
    }

    errorDiv.style.display = 'none';
    submitBtn.innerText = "Sending Code...";
    submitBtn.disabled = true;

    try {
        // USE THE EXACT URL FROM YOUR CONFIG FILE
        // Assuming your api-config.js has API_ENDPOINTS.register
        // If not, we safely build it from the working login URL!
        let targetUrl = API_ENDPOINTS.register; 
        if (!targetUrl && API_ENDPOINTS.login) {
            targetUrl = API_ENDPOINTS.login.replace('login/', 'register/');
        }

        console.log("👉 TRYING TO SEND DATA TO:", targetUrl); // Debugging tool

        const response = await fetch(targetUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                username: username,
                email: email,
                phone_number: phone,
                grade: parseInt(grade),
                password: password,
                password2: passwordConfirm
            })
        });

        // Try to parse JSON. If Django crashed (500 error), this will fail safely.
        let data;
        try {
            data = await response.json();
        } catch (e) {
            console.error("Failed to parse Django response. Django likely crashed with a 500 error!");
            throw new Error("Backend server crashed. Check Django terminal.");
        }

        if (response.ok && data.requires_otp) {
            document.getElementById('register-step-1').style.display = 'none';
            document.getElementById('register-step-2').style.display = 'block';
            document.getElementById('otp-email-hidden').value = data.email;
        } else {
            const errorKeys = Object.keys(data);
            const firstErrorMsg = data[errorKeys[0]];
            errorDiv.innerText = Array.isArray(firstErrorMsg) ? firstErrorMsg[0] : "Registration failed.";
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        // CHANGED THIS TO PRINT THE REAL JAVASCRIPT ERROR
        console.error(" REAL JAVASCRIPT CRASH:", error);
        errorDiv.innerText = "JS Error: " + error.message;
        errorDiv.style.display = 'block';
    } finally {
        submitBtn.innerText = "Verify & Login";
        submitBtn.disabled = false;
    }
}

// ============================================
// Registration Step 2: Verify OTP (UPGRADED)
// ============================================
async function handleVerifyOTP(event) {
    event.preventDefault();
    
    const email = document.getElementById('otp-email-hidden').value;
    const otp = document.getElementById('reg-otp').value;
    const errorDiv = document.getElementById('otp-error');
    const submitBtn = document.getElementById('otp-submit-btn');

    errorDiv.style.display = 'none';
    submitBtn.innerText = "Verifying...";
    submitBtn.disabled = true;

    try {
        let verifyUrl = 'http://127.0.0.1:8000/accounts/verify-otp/';
        if (typeof API_ENDPOINTS !== 'undefined' && API_ENDPOINTS.login) {
            verifyUrl = API_ENDPOINTS.login.replace('login/', 'verify-otp/');
        }

        const response = await fetch(verifyUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, otp: otp })
        });

        // Read the raw text first so we can see exactly what Django sent back!
        const rawText = await response.text();
        console.log("👉 RAW DJANGO RESPONSE:", rawText);

        let data;
        try {
            data = JSON.parse(rawText);
        } catch (e) {
            throw new Error("Django crashed and didn't return JSON. Check your terminal!");
        }

        if (response.ok) {
            // BULLETPROOF TOKEN GRABBER
            const access = data.access || (data.tokens && data.tokens.access);
            const refresh = data.refresh || (data.tokens && data.tokens.refresh);
            const username = data.username || (data.user && data.user.username) || email.split('@')[0];
            
            if (access) localStorage.setItem('access_token', access);
            if (refresh) localStorage.setItem('refresh_token', refresh);
            localStorage.setItem('username', username);
            
            document.querySelector('#register-step-1 form').reset();
            resetRegistration();
            window.location.hash = 'dashboard';
            
            // Force a quick page reload to clear out the old dashboard errors
            setTimeout(() => window.location.reload(), 100);
        } else {
            errorDiv.innerText = data.error || "Invalid OTP.";
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        console.error("🚨 JAVASCRIPT CRASH:", error);
        errorDiv.innerText = "Error: " + error.message;
        errorDiv.style.display = 'block';
    } finally {
        submitBtn.innerText = "Verify & Login";
        submitBtn.disabled = false;
    }
}

// ============================================
// General App Functions
// ============================================
function handleLogout() {
    localStorage.clear();
    window.location.hash = 'auth';
}

function displayUsername() {
    const usernameElement = document.getElementById('username-display');
    if (usernameElement) {
        const username = localStorage.getItem('username') || 'Student';
        usernameElement.textContent = username;
    }
}

function checkIfAuthenticated() {
    const token = localStorage.getItem('access_token');
    if (token) displayUsername();
}

document.addEventListener('DOMContentLoaded', function() {
    checkIfAuthenticated();
});

// ============================================
// Helper to reset the UI back to Step 1
// ============================================
function resetRegistration() {
    const step2 = document.getElementById('register-step-2');
    const step1 = document.getElementById('register-step-1');
    const otpError = document.getElementById('otp-error');
    const regOtp = document.getElementById('reg-otp');

    if (step2) step2.style.display = 'none';
    if (step1) step1.style.display = 'block';
    if (otpError) otpError.style.display = 'none';
    if (regOtp) regOtp.value = '';
}