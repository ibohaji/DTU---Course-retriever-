document.addEventListener('keydown', (e) => {
    // Cmd/Ctrl + / to toggle sidebar
    if ((e.metaKey || e.ctrlKey) && e.key === '/') {
        Alpine.store('sidebar').toggle();
    }
    // Cmd/Ctrl + K to focus input
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        document.getElementById('promptInput').focus();
    }
    // Esc to clear input
    if (e.key === 'Escape') {
        document.getElementById('promptInput').value = '';
    }
}); 