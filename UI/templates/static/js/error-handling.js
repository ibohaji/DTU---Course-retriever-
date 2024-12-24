window.onerror = function(msg, url, lineNo, columnNo, error) {
    // Show user-friendly error message
    showNotification('Something went wrong. Trying to recover...', 'error');
    return false;
}; 