// Constants
const API_URL = "http://localhost:1234/v1/chat/completions";
const API_KEY = "not-needed";

// Initialize messages array
if (!window.messages) {
    window.messages = [];
}

let controller = null;

// The rest of your JavaScript functions...
// (generate, stop, clearInput functions remain the same) 

document.addEventListener('htmx:afterRequest', function(evt) {
    if (evt.detail.successful) {
        // Add message with animation
        Alpine.store('messages').push({
            id: Date.now(),
            content: evt.detail.xhr.response,
            timestamp: new Date(),
            type: 'assistant'
        });
    } else {
        // Show error
        Alpine.store('error', 'Failed to send message. Please try again.');
        setTimeout(() => {
            Alpine.store('error', null);
        }, 3000);
    }
});

// Handle user messages
document.getElementById('promptInput').addEventListener('keyup', function(evt) {
    if (evt.key === 'Enter' && this.value.trim()) {
        Alpine.store('messages').push({
            id: Date.now(),
            content: this.value,
            timestamp: new Date(),
            type: 'user'
        });
    }
}); 