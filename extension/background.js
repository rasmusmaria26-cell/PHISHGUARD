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

async function scanTab(tabId, rawUrl) {
    // Normalize URL (remove hash fragments) to prevent duplicate scans on SPAs
    const url = rawUrl.split('#')[0];

    // Skip if recently scanned (simple debounce/cache)
    if (scanCache.has(url)) {
        const lastScan = scanCache.get(url);
        if (Date.now() - lastScan < 30000) { // 30 seconds cache
            console.log('Skipping recently scanned URL:', url);
            return;
        }
    }

    // LOCK: Set cache immediately to prevent race conditions
    scanCache.set(url, Date.now());
    console.log('Initiating scan for:', url);

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
        if (data.verdict === 'phishing') {
            await incrementThreatCount();
        }
        updateBadge(tabId, data.verdict);

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

async function incrementThreatCount() {
    const data = await chrome.storage.local.get(['threats today', 'lastReset']);
    let count = data['threats today'] || 0;
    const lastReset = data['lastReset'] || 0;

    // Reset if it's a new day
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();

    if (today > lastReset) {
        count = 0;
        chrome.storage.local.set({ 'lastReset': today });
    }

    count++;
    await chrome.storage.local.set({ 'threats today': count });

    // Update badge globally (optional, or per tab)
    chrome.action.setBadgeText({ text: count.toString() });
    chrome.action.setBadgeBackgroundColor({ color: '#ef4444' });
}

function updateBadge(tabId, verdict) {
    // We strictly show the threat count on the badge globally now, 
    // OR we could show the status of the current page.
    // User requested "Show number of threats blocked today".

    // So usually we don't overwrite the global badge with page status unless we use tabId specific badges.
    // Let's use tabId specific for status ("SAFE", "WARN") ONLY if the user is on that tab,
    // otherwise the default badge is the count.

    verdict = (verdict || "").toLowerCase();
    let text = "";
    let color = "#4CAF50";

    if (verdict === 'phishing') {
        text = "!";
        color = "#F44336";
    } else if (verdict === 'suspicious') {
        text = "?";
        color = "#FF9800";
    } else {
        // Safe pages don't need a badge, keeps it clean.
        // We want the global badge (threat count) to show through if possible, 
        // but chrome APIs make mixing difficult.
        // Let's prioritize the page status if it's dangerous.
        return;
    }

    chrome.action.setBadgeText({ text: text, tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: color, tabId: tabId });
}
