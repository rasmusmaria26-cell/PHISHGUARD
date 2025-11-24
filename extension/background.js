// background.js - Service Worker for Manifest V3

// Listen for extension installation
chrome.runtime.onInstalled.addListener(() => {
    console.log('PhishGuard extension installed');
});

// Listen for messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'checkUrl') {
        // Future: Implement background URL checking
        console.log('Checking URL:', request.url);
        sendResponse({ status: 'ok' });
    }
    return true; // Keep channel open for async response
});

// Optional: Monitor tab updates for automatic scanning
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        // Future: Implement automatic scanning on page load
        console.log('Tab updated:', tab.url);
    }
});
