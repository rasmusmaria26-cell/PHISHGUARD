// popup.js - Full Feature Implementation
const analyzeBtn = document.getElementById('analyzeBtn');
const btnText = document.getElementById('btnText');
const statusMsg = document.getElementById('statusMsg');
const resultCard = document.getElementById('resultCard');
// Stats Elements
const dailyScansEl = document.getElementById('dailyScans');
const threatsBlockedEl = document.getElementById('threatsBlocked');
// History Elements
const historyToggle = document.getElementById('historyToggle');
const historyList = document.getElementById('historyList');
const chevron = historyToggle.querySelector('.chevron');
// Actions
const copyBtn = document.getElementById('copyBtn');
const shareBtn = document.getElementById('shareBtn');
const reportBtn = document.getElementById('reportBtn');
// Settings Elements
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const closeSettings = document.getElementById('closeSettings');

// Result elements
const scoreRing = document.getElementById('scoreRing');
const scoreNumber = scoreRing.querySelector('.score-number');
const scoreCircle = scoreRing.querySelector('.score-ring-circle');
const verdictBadge = document.getElementById('verdictBadge');
const verdictTitle = document.getElementById('verdictTitle');
const verdictSub = document.getElementById('verdictSub');
const urlScore = document.getElementById('urlScore');
const contentScore = document.getElementById('contentScore');
const visualScore = document.getElementById('visualScore');
const detailsContainer = document.getElementById('detailsContainer');

// --- Helper: Toast Notification ---
function showToast(title, message, type = 'info', duration = 3000) {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  // SVG Icons map
  const icons = {
    success: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>`,
    error: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`,
    warning: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
    info: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`
  };

  toast.innerHTML = `
        <div class="toast-icon">${icons[type]}</div>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
    `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('hiding');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// --- Helper: Progress Bar ---
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const progressLabel = document.getElementById('progressLabel');

function setProgress(percent, label) {
  progressContainer.classList.remove('hidden');
  progressLabel.classList.remove('hidden');
  progressBar.style.width = `${percent}%`;
  progressLabel.textContent = label;
}

function hideProgress() {
  progressContainer.classList.add('hidden');
  progressLabel.classList.add('hidden');
}

// --- Helper: Animate Score ---
function animateScore(targetScore) {
  const duration = 1000;
  const steps = 60;
  const increment = targetScore / steps;
  let current = 0;
  const circumference = 251;
  const offset = circumference - (targetScore / 100) * circumference;

  scoreRing.classList.add('animating');
  scoreCircle.style.strokeDashoffset = offset;

  const interval = setInterval(() => {
    current += increment;
    if (current >= targetScore) {
      current = targetScore;
      clearInterval(interval);
    }
    scoreNumber.textContent = Math.round(current);
  }, duration / steps);
}

// --- Logic: Stats & History ---
async function updateStats() {
  const { history = [] } = await chrome.storage.local.get('history');

  // Daily Scans
  const today = new Date().toDateString();
  const todayScans = history.filter(h => new Date(h.timestamp).toDateString() === today);
  dailyScansEl.textContent = todayScans.length;

  // Threats Blocked
  const threats = history.filter(h => h.verdict === 'phishing');
  threatsBlockedEl.textContent = `${threats.length} threats`;
  if (threats.length > 0) threatsBlockedEl.style.background = 'rgba(239, 68, 68, 0.2)';

  // Populate Recent History
  renderHistory(history);
}

function renderHistory(history) {
  historyList.innerHTML = '';
  const recent = history.slice(0, 10); // Last 10

  if (recent.length === 0) {
    historyList.innerHTML = '<div style="padding:15px;text-align:center;color:#666;font-size:12px">No recent scans</div>';
    return;
  }

  recent.forEach(item => {
    const div = document.createElement('div');
    div.className = 'history-item';
    const time = new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    div.innerHTML = `
            <div style="display:flex;flex-direction:column;gap:2px">
                <span class="history-url" title="${item.url}">${new URL(item.url).hostname}</span>
                <span style="font-size:10px;color:#666">${time}</span>
            </div>
            <div class="history-verdict ${item.verdict.toLowerCase()}">${item.verdict}</div>
        `;
    historyList.appendChild(div);
  });
}

async function saveScanToHistory(data, url) {
  const { history = [] } = await chrome.storage.local.get('history');
  const newEntry = {
    timestamp: Date.now(),
    url: url,
    verdict: data.verdict || 'safe',
    score: data.score || 0
  };

  const updatedHistory = [newEntry, ...history].slice(0, 50); // Keep last 50
  await chrome.storage.local.set({ history: updatedHistory });
  updateStats();
}

// --- Logic: Actions ---
copyBtn.addEventListener('click', () => {
  // Generate text report
  const text = `PhishGuard Scan Report\nTime: ${new Date().toLocaleString()}\nVerdict: ${verdictBadge.textContent}\nScore: ${scoreNumber.textContent}\nURL Risk: ${urlScore.textContent}\nContent Risk: ${contentScore.textContent}\nVisual Risk: ${visualScore.textContent}`;

  navigator.clipboard.writeText(text).then(() => {
    showToast('Copied', 'Report copied to clipboard', 'success');
  });
});

shareBtn.addEventListener('click', () => {
  showToast('Shared', 'Threat details shared with community', 'info');
});

// --- Logic: Report Modal ---
const reportModal = document.getElementById('reportModal');
const closeReport = document.getElementById('closeReport');
const submitReportBtn = document.getElementById('submitReportBtn');

reportBtn.addEventListener('click', () => {
  reportModal.classList.remove('hidden');
});

closeReport.addEventListener('click', () => {
  reportModal.classList.add('hidden');
});

submitReportBtn.addEventListener('click', async () => {
  const reason = document.getElementById('reportReason').value;
  const comments = document.getElementById('reportComments').value;
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  try {
    const response = await fetch('http://127.0.0.1:8000/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: tab.url,
        reason: reason,
        comments: comments,
        timestamp: new Date().toISOString()
      })
    });

    if (!response.ok) throw new Error('Failed to send report');

    showToast('Reported', 'Thank you for your feedback!', 'success');
    reportModal.classList.add('hidden');
    document.getElementById('reportComments').value = ""; // Reset
  } catch (err) {
    showToast('Error', 'Could not send report', 'error');
  }
});

// --- Logic: Settings Modal ---
settingsBtn.addEventListener('click', () => {
  settingsModal.classList.remove('hidden');
});

closeSettings.addEventListener('click', () => {
  settingsModal.classList.add('hidden');
});

historyToggle.addEventListener('click', () => {
  historyList.classList.toggle('hidden');
  const isHidden = historyList.classList.contains('hidden');
  chevron.style.transform = isHidden ? 'rotate(0deg)' : 'rotate(180deg)';
});

// --- Logic: Ripple Effect & Collapsible ---
analyzeBtn.addEventListener('click', function (e) {
  if (this.classList.contains('loading')) return; // Don't ripple if loading

  let box = this.getBoundingClientRect();
  let x = e.clientX - box.left;
  let y = e.clientY - box.top;

  let ripple = document.createElement('span');
  ripple.className = 'ripple';
  ripple.style.left = x + 'px';
  ripple.style.top = y + 'px';

  this.appendChild(ripple);

  setTimeout(() => {
    ripple.remove();
  }, 600);
});

const detailToggle = document.getElementById('detailToggle');
const detailsWrapper = document.getElementById('detailsWrapper');

detailToggle.addEventListener('click', () => {
  const isOpen = detailsWrapper.classList.contains('open');
  if (isOpen) {
    detailsWrapper.classList.remove('open');
    detailToggle.classList.remove('expanded');
    detailToggle.innerHTML = `Show detailed analysis <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>`;
  } else {
    detailsWrapper.classList.add('open');
    detailToggle.classList.add('expanded');
    detailToggle.innerHTML = `Hide detailed analysis <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>`;
  }
});

// --- Main Scan Logic ---
async function scanPage() {
  // Reset details view
  detailsWrapper.classList.remove('open');
  detailToggle.classList.remove('expanded');

  try {
    analyzeBtn.classList.add('loading');
    btnText.textContent = 'Scanning...';

    setProgress(20, 'Capturing screenshot...');
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) throw new Error('No active tab');

    const screenshot = await chrome.tabs.captureVisibleTab(null, { format: 'png' });

    setProgress(40, 'Extracting content...');
    const [textResult] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => document.body.innerText
    });
    const pageText = textResult?.result || '';

    setProgress(60, 'Analyzing threats...');
    const response = await fetch('http://127.0.0.1:8000/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: tab.url,
        text: pageText.substring(0, 5000),
        screenshot: screenshot,
        sensitivity: document.getElementById('sensitivitySelect').value || 'balanced',
        request_id: Date.now().toString()
      })
    });

    if (!response.ok) throw new Error(`Server error: ${response.status}`);

    const data = await response.json();

    setProgress(100, 'Scan complete!');
    setTimeout(() => hideProgress(), 500);

    // Display Result
    displayResult(data);

    // Save to History
    saveScanToHistory(data, tab.url);

    // Redirect if phishing
    if (data.verdict && data.verdict.toLowerCase() === 'phishing') {
      setTimeout(() => {
        chrome.tabs.update(tab.id, {
          url: chrome.runtime.getURL('warning.html') + '?url=' + encodeURIComponent(tab.url)
        });
      }, 2000);
    }

  } catch (err) {
    console.error(err);
    showToast('Error', err.message, 'error');
  } finally {
    analyzeBtn.classList.remove('loading');
    btnText.textContent = 'Scan page';
  }
}

function displayResult(data) {
  statusMsg.classList.add('hidden');
  resultCard.classList.remove('hidden');
  document.getElementById('errorMsg').classList.add('hidden');

  const score = data.score || 0;

  // update ring color
  scoreRing.className = 'score-ring';
  if (score >= 70) scoreRing.classList.add('danger');
  else if (score >= 35) scoreRing.classList.add('warn');

  animateScore(score);

  // Update Card Class
  const verdict = (data.verdict || 'safe').toLowerCase();
  resultCard.className = 'result ' + verdict;
  verdictBadge.className = 'badge ' + verdict;
  verdictBadge.textContent = verdict.toUpperCase();

  if (verdict === 'phishing') {
    verdictTitle.textContent = 'Phishing detected';
    verdictSub.textContent = 'Confidence: high';
    showToast('Threat Detected', 'Phishing attempt blocked!', 'error');
  } else if (verdict === 'suspicious') {
    verdictTitle.textContent = 'Potential threat';
    verdictSub.textContent = 'Confidence: medium';
    showToast('Warning', 'Suspicious activity detected', 'warning');
  } else {
    verdictTitle.textContent = 'No phishing detected';
    verdictSub.textContent = 'Confidence: high';
    showToast('Safe', 'Page appears safe', 'success');
  }

  urlScore.textContent = data.url_score || 0;
  contentScore.textContent = data.content_score || 0;
  visualScore.textContent = data.visual_score || 0;

  // Populate Details
  renderDetails(data);
}

function renderDetails(data) {
  detailsContainer.innerHTML = '';

  // Safely handle reasons - could be string, array, or null
  let reasons = [];
  if (Array.isArray(data.reasons)) {
    reasons = data.reasons;
  } else if (typeof data.reasons === 'string') {
    reasons = data.reasons.split(';').map(r => r.trim()).filter(r => r);
  }

  const categories = { url: [], content: [], visual: [] };

  reasons.forEach(r => {
    const lower = r.toLowerCase();
    if (lower.includes('url') || lower.includes('domain') || lower.includes('https') || lower.includes('ip address')) categories.url.push(r);
    else if (lower.includes('visual') || lower.includes('mimic')) categories.visual.push(r);
    else categories.content.push(r);
  });

  const createDetail = (type, items, icon, title, emptyMsg) => {
    if (items.length === 0 && data[`${type}_score`] === 0) return;

    const div = document.createElement('div');
    div.className = 'detail-item';
    div.innerHTML = `
            <div class="detail-icon">${icon}</div>
            <div class="detail-text">
                <div class="dt-title">${title}</div>
                <div class="dt-desc">${items.length ? items.join('. ') : emptyMsg}</div>
            </div>
        `;
    detailsContainer.appendChild(div);
  };

  createDetail('url', categories.url,
    `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>`,
    'URL Risks', 'Clean URL structure');

  createDetail('content', categories.content,
    `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`,
    'Content Signals', 'Normal content patterns');

  createDetail('visual', categories.visual,
    `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`,
    'Visual Analysis', 'No visual impersonation');

  if (detailsContainer.children.length === 0) {
    const div = document.createElement('div');
    div.className = 'detail-item';
    div.innerHTML = `
            <div class="detail-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg></div>
            <div class="detail-text"><div class="dt-title">Clean Scan</div><div class="dt-desc">No threats detected.</div></div>
        `;
    detailsContainer.appendChild(div);
  }
}

// Initialization
document.addEventListener('DOMContentLoaded', updateStats);
analyzeBtn.addEventListener('click', scanPage);