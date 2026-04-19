/**
 * Edusolve App Logic
 * ROUTING HAS BEEN MOVED TO INDEX.HTML TO PREVENT CONFLICTS!
 */

document.addEventListener('DOMContentLoaded', () => {
    // Add scroll listener for navbar glass effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if(window.scrollY > 50) {
                navbar.style.boxShadow = '0 10px 40px rgba(0,0,0,0.05)';
            } else {
                navbar.style.boxShadow = 'var(--glass-shadow)';
            }
        });
    }

    // Simulate AI Solve Button Animation
    window.simulateSolve = function(event) {
        const input = document.getElementById('solve-input');
        if (!input || !input.value.trim()) {
            alert("Please enter a question first.");
            return;
        }
        
        const btn = event.target;
        const originalText = btn.innerText;
        btn.innerText = "Analyzing...";
        btn.style.opacity = "0.7";
        btn.disabled = true;
        
        setTimeout(() => {
            const emptyEl = document.getElementById('solve-empty');
            if (emptyEl) emptyEl.style.display = 'none';
            
            const contentEl = document.getElementById('solve-content');
            if (contentEl) {
                contentEl.style.display = 'block';
                contentEl.classList.add('animate-up');
            }
            
            btn.innerText = "Solution Generated";
            btn.style.background = "#27c93f";
            
            setTimeout(() => {
                btn.innerText = originalText;
                btn.style.background = "";
                btn.style.opacity = "1";
                btn.disabled = false;
            }, 3000);
        }, 1200);
    };

    // Simulate PDF Upload Button Animation
    window.simulatePDFUpload = function() {
        const box = document.getElementById('pdf-upload-box');
        const text = document.getElementById('pdf-upload-text');
        
        if (box && text) {
            box.style.background = "rgba(39, 201, 63, 0.1)";
            box.style.borderColor = "#27c93f";
            text.innerHTML = "<b>Document.pdf</b> uploaded successfully! ✨";
        }
    };
});