document.addEventListener('htmx:afterRequest', function(evt) {
    if (evt.detail.path === '/chat') {
        const chatHistory = document.getElementById('chat-history');
        const userInput = document.getElementById('promptInput');
        const message = userInput.value;
        
        // Add user message immediately
        const userMessage = document.createElement('div');
        userMessage.className = 'message user';
        userMessage.innerHTML = `
            <div class="message-content">
                <div class="message-bubble">
                    <p>${message}</p>
                    <span class="timestamp">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
            </div>
        `;
        chatHistory.appendChild(userMessage);
        
        // Clear input
        userInput.value = '';
        
        // Scroll to bottom
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
}); 