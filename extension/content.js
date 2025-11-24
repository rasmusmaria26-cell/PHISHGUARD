// content.js - Content script injected into web pages

// This script runs on every page and can be used for:
// 1. Real-time DOM monitoring
// 2. Detecting suspicious form submissions
// 3. Highlighting suspicious elements

console.log('PhishGuard content script loaded');

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getPageInfo') {
        // Extract page information
        const pageInfo = {
            url: window.location.href,
            title: document.title,
            forms: document.querySelectorAll('form').length,
            inputs: document.querySelectorAll('input[type="password"]').length
        };
        sendResponse(pageInfo);
    }
    return true;
});

// Future: Add real-time phishing detection
// Example: Monitor for suspicious form submissions
document.addEventListener('submit', (event) => {
    // Future: Check if form is submitting to suspicious domain
    console.log('Form submission detected');
});
