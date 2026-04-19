// community.js
// Handles the live community forum and channels

let currentChannelId = null;

// ============================================
// Load Channels for the Sidebar
// ============================================
async function loadCommunityChannels() {
    const channelList = document.querySelector('.channel-list');
    if (!channelList) return;

    try {
        channelList.innerHTML = '<li style="color: var(--color-text-muted);">Loading channels...</li>';
        
        const response = await apiCall(API_ENDPOINTS.communityChannels);
        const channels = response.results || response;

        if (!channels || channels.length === 0) {
            channelList.innerHTML = '<li style="color: var(--color-text-muted);">No channels found.</li>';
            return;
        }

        channelList.innerHTML = ''; // Clear loading
        
        channels.forEach((channel, index) => {
            const li = document.createElement('li');
            li.textContent = `# ${channel.name.toLowerCase()}`;
            li.id = `channel-tab-${channel.id}`;
            li.style.cursor = 'pointer';
            
            li.onclick = () => loadChannelFeed(channel.id, channel.name, channel.description);
            
            channelList.appendChild(li);

            // Auto-load the very first channel by default
            if (index === 0 && !currentChannelId) {
                loadChannelFeed(channel.id, channel.name, channel.description);
            }
        });

    } catch (error) {
        console.error('Failed to load channels:', error);
        channelList.innerHTML = '<li style="color: #ff4444;">Connection error.</li>';
    }
}

// ============================================
// Load Messages for a Specific Channel
// ============================================
async function loadChannelFeed(channelId, channelName, channelDesc) {
    currentChannelId = channelId;
    
    // Update active UI state on the sidebar
    document.querySelectorAll('.channel-list li').forEach(li => li.classList.remove('active'));
    const activeTab = document.getElementById(`channel-tab-${channelId}`);
    if (activeTab) activeTab.classList.add('active');

    // Update Header
    const header = document.querySelector('.community-header');
    if (header) {
        header.innerHTML = `
            <h3># ${channelName.toLowerCase()}</h3>
            <p>${channelDesc || 'Discuss anything related to this topic.'}</p>
        `;
    }

    // Fetch and render posts
    const feed = document.querySelector('.community-feed');
    if (!feed) return;
    
    feed.innerHTML = `
        <div style="text-align: center; color: var(--color-text-muted); padding: 2rem;">
            Loading messages...
        </div>`;

    try {
        // Fetch posts specific to this channel
        const response = await apiCall(`${API_ENDPOINTS.communityPosts}?channel=${channelId}`);
        const posts = response.results || response;

        feed.innerHTML = ''; // Clear loading

        // ==========================================
        // THE FIX: Activate the Send button BEFORE we check if the feed is empty!
        // ==========================================
        setupMessageInput();

        if (!posts || posts.length === 0) {
            feed.innerHTML = `
                <div style="text-align: center; color: var(--color-text-muted); padding: 2rem;">
                    <strong>No messages yet!</strong><br>Be the first to say hello in #${channelName}.
                </div>`;
            return; // Now it's safe to stop early!
        }

        // Render posts (reverse order so newest is at the bottom)
        posts.slice().reverse().forEach(post => {
            const initial = post.author_name ? post.author_name.charAt(0).toUpperCase() : '?';
            const timeStr = new Date(post.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            
            const postDiv = document.createElement('div');
            postDiv.className = 'post-card';
            postDiv.innerHTML = `
                <div class="post-avatar" style="background: var(--color-gradient-1);">${initial}</div>
                <div class="post-content">
                    <div class="post-meta"><strong>${post.author_name || 'Student'}</strong> <span class="time">${timeStr}</span></div>
                    <p style="margin-top: 0.25rem;">${post.content}</p>
                </div>
            `;
            feed.appendChild(postDiv);
        });

        // Scroll feed to the bottom automatically
        feed.scrollTop = feed.scrollHeight;

    } catch (error) {
        console.error('Failed to load feed:', error);
        feed.innerHTML = `<div style="color: #ff4444; padding: 1rem;">Failed to load messages.</div>`;
    }
}

// ============================================
// Setup Input Box & Send Message
// ============================================
function setupMessageInput() {
    const input = document.querySelector('.community-input input');
    const sendBtn = document.querySelector('.community-input button');
    const channelNameEl = document.querySelector('.community-header h3');

    if (!input || !sendBtn) {
        console.error("Could not find input box or send button in the HTML.");
        return;
    }

    // Set placeholder
    if (channelNameEl) {
        input.placeholder = `Message ${channelNameEl.innerText}...`;
    }
    
    // Safely attach the click event
    sendBtn.onclick = submitCommunityMessage;
    
    // Attach the Enter key event
    input.onkeypress = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Stop default form submission if any
            submitCommunityMessage();
        }
    };
}

async function submitCommunityMessage() {
    console.log("Send button triggered. Active Channel ID:", currentChannelId);

    // 1. Check if a channel is actually selected!
    if (!currentChannelId) {
        alert("Please select a channel from the sidebar on the left before sending a message!");
        return;
    }

    const input = document.querySelector('.community-input input');
    const content = input.value.trim();

    if (!content) return;

    input.disabled = true;

    try {
        console.log("Sending message to Django...");
        
        const response = await apiCall(API_ENDPOINTS.communityPosts, 'POST', {
            channel: currentChannelId,
            content: content
        });
        
        console.log("Django Response:", response);

        if (response.id) {
            input.value = ''; // Clear input
            
            // Refresh the feed to show the new message
            const currentName = document.querySelector('.community-header h3').innerText.replace('# ', '');
            loadChannelFeed(currentChannelId, currentName, ''); 
        }
    } catch (error) {
        console.error('Failed to post message:', error);
        alert(`Failed to send: ${error.message || 'Check your internet or backend server.'}`);
    } finally {
        input.disabled = false;
        input.focus();
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
        
        // Fetch channels when user clicks the Community tab
        if (viewId === 'community') {
            loadCommunityChannels();
        }
    };

    if (window.location.hash === '#community') {
        loadCommunityChannels();
    }
});