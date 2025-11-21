document.addEventListener('DOMContentLoaded', () => {
    // 1. Parse URL Parameters to fill the data
    const params = new URLSearchParams(window.location.search);
    
    const score = params.get('score');
    const verdict = params.get('verdict');
    const refUrl = params.get('ref');

    // Update UI
    if (score) document.getElementById('score').innerText = score;
    if (verdict) document.querySelector('h1').innerText = verdict;
    if (refUrl) document.getElementById('url').innerText = refUrl;

    // 2. Button Logic (Event Listeners instead of onclick)
    
    // SAFE BUTTON: Go to Google (Safety)
    const safeBtn = document.getElementById('btn-safe');
    if (safeBtn) {
        safeBtn.addEventListener('click', () => {
            // Try to go back, otherwise go to Google
            if (window.history.length > 1) {
                window.history.back();
            } else {
                window.location.href = "https://www.google.com";
            }
        });
    }

    // DANGER BUTTON: Proceed to the bad site
    const dangerBtn = document.getElementById('btn-danger');
    if (dangerBtn) {
        dangerBtn.addEventListener('click', () => {
            if (refUrl) {
                // Decode the URL and go there
                window.location.href = decodeURIComponent(refUrl);
            } else {
                alert("Target URL not found.");
            }
        });
    }
});