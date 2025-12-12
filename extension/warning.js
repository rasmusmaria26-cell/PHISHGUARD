// warning.js
document.addEventListener('DOMContentLoaded', () => {
    // Extract URL from query parameter
    const urlParams = new URLSearchParams(window.location.search);
    const blockedUrl = urlParams.get('url') || 'Unknown URL';
    const threatScore = urlParams.get('score') || '90';
    const visualScore = parseInt(urlParams.get('visual') || '0');

    const blockedUrlEl = document.getElementById('blockedUrl');
    const threatScoreEl = document.getElementById('threatScore');
    const visualMatchEl = document.getElementById('visualMatch');

    if (blockedUrlEl) blockedUrlEl.textContent = blockedUrl;
    if (threatScoreEl) threatScoreEl.textContent = 'HIGH RISK';
    if (visualMatchEl) {
        visualMatchEl.textContent = visualScore > 50 ? 'YES' : 'NO';
        // Optional: color it red if YES
        if (visualScore > 50 && visualMatchEl.nextElementSibling) {
            visualMatchEl.nextElementSibling.style.color = '#ef4444';
        }
    }

    // Buttons
    document.querySelector('.btn-primary')?.addEventListener('click', goBack);
    document.querySelector('.btn-secondary')?.addEventListener('click', proceedAnyway);

    function goBack() {
        if (window.history.length > 1) {
            window.history.back();
        } else {
            window.close(); // Close tab if no history
        }
    }

    function proceedAnyway() {
        if (confirm('⚠️ WARNING: This page was flagged as a phishing attempt.\n\nAre you absolutely sure you want to continue?')) {
            // Note: Decoding the URL is important if it was encoded
            const target = decodeURIComponent(blockedUrl);
            window.location.href = target;
        }
    }
});