// background.js - Service Worker for Manifest V3

// Listen for extension installation
chrome.runtime.onInstalled.addListener(() => {
    console.log('PhishGuard extension installed');
});

// Cache to prevent duplicate scans on the same URL
const scanCache = new Map();

// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // Only scan when page is fully loaded and has a valid HTTP/HTTPS URL
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
        scanTab(tabId, tab.url);
    }
});

async function scanTab(tabId, url) {
    // Skip if recently scanned (simple debounce/cache)
    if (scanCache.has(url)) {
        const lastScan = scanCache.get(url);
        if (Date.now() - lastScan < 30000) { // 30 seconds cache
            console.log('Skipping recently scanned URL:', url);
            return;
        }
    }

    console.log('Initiating scan for:', url);
    scanCache.set(url, Date.now());

    try {
        // 1. Capture Screenshot
        // Note: This requires <all_urls> permission
        const screenshotUrl = await chrome.tabs.captureVisibleTab(null, { format: 'png' });

        // 2. Extract Page Text
        const execRes = await chrome.scripting.executeScript({
            target: { tabId: tabId },
            func: () => {
                try { return (document.body.innerText || "").replace(/\s+/g, " ").trim(); }
                catch (e) { return ""; }
            }
        });
        const text = (execRes && execRes[0] && execRes[0].result) || "";

        // 3. Send to Backend
        const API = 'http://127.0.0.1:8000/analyze';
        const payload = {
            url: url,
            text: text,
            screenshot: screenshotUrl,
            request_id: 'auto-' + Date.now()
        };

        const resp = await fetch(API, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!resp.ok) throw new Error('API Error ' + resp.status);

        const data = await resp.json();
        console.log('Scan result:', data);

        // 4. Handle Result
        updateIcon(tabId, data.verdict);

        // If dangerous, redirect or warn
        if (data.score >= 75 || data.verdict === 'phishing') {
            const warningUrl = chrome.runtime.getURL("warning.html") +
                `?score=${data.score}&verdict=${data.verdict}&ref=${encodeURIComponent(url)}`;
            chrome.tabs.update(tabId, { url: warningUrl });
        }

    } catch (err) {
        console.error('Scan failed:', err);
    }
}

function updateIcon(tabId, verdict) {
    let iconPath = "icons/icon_safe.png"; // You might need to add these icons
    let badgeText = "";
    let badgeColor = "#4CAF50";

    verdict = (verdict || "").toLowerCase();

    if (verdict === 'phishing') {
        badgeText = "!!!";
        badgeColor = "#F44336";
    } else if (verdict === 'suspicious') {
        badgeText = "?";
        badgeColor = "#FF9800";
    } else {
        badgeText = "OK";
        badgeColor = "#4CAF50";
    }

    // Since we might not have dynamic icons yet, just set badge
    chrome.action.setBadgeText({ text: badgeText, tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: badgeColor, tabId: tabId });
}
