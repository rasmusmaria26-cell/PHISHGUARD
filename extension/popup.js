// popup.js - Enhanced UI with Loading States
const analyzeBtn = document.getElementById('analyze');
const statusEl = document.getElementById('status');
const resultArea = document.getElementById('resultArea');
const scoreEl = document.getElementById('score');
const verdictEl = document.getElementById('verdict');
const barFill = document.getElementById('bar-fill');
const urlScoreEl = document.getElementById('url-score');
const contentScoreEl = document.getElementById('content-score');
const visualScoreEl = document.getElementById('visual-score');
const reasonsList = document.getElementById('reasonsList');
const errorEl = document.getElementById('error');
const rawEl = document.getElementById('raw');

function setStatus(txt) {
  const statusEmojis = {
    'Capturing': '📸',
    'Scanning': '🔍',
    'Analyzing': '🧠',
    'Complete': '✅',
    'Error': '❌',
    'Ready': '🟢'
  };

  const emoji = Object.keys(statusEmojis).find(key => txt.includes(key));
  const prefix = emoji ? statusEmojis[emoji] + ' ' : '';

  statusEl.textContent = prefix + txt;
  console.log('[popup] ', txt);
}

function setProgress(score) {
  const pct = Math.max(0, Math.min(100, score));
  barFill.style.width = pct + '%';
  if (pct >= 70) barFill.style.background = getComputedStyle(document.documentElement).getPropertyValue('--danger');
  else if (pct >= 35) barFill.style.background = getComputedStyle(document.documentElement).getPropertyValue('--warn');
  else barFill.style.background = getComputedStyle(document.documentElement).getPropertyValue('--safe');
}

function showResult(data) {
  resultArea.classList.remove('hidden');
  errorEl.classList.add('hidden');

  scoreEl.textContent = data.score ?? '—';
  urlScoreEl.textContent = data.url_score ?? '0';
  contentScoreEl.textContent = data.content_score ?? '0';
  visualScoreEl.textContent = data.visual_score ?? '0';
  setProgress(data.score ?? 0);

  const v = (data.verdict || 'neutral').toLowerCase();
  verdictEl.textContent = v.toUpperCase();
  verdictEl.className = 'verdict ' + (v === 'safe' ? 'safe' : v === 'suspicious' ? 'suspicious' : v === 'phishing' ? 'danger' : 'neutral');

  const reasons = Array.isArray(data.reasons) ? data.reasons : (data.reasons ? [data.reasons] : []);
  reasonsList.innerHTML = '';

  if (reasons.length === 0) {
    reasonsList.innerHTML = '<li>✅ No suspicious indicators found.</li>';
  } else {
    for (const r of reasons) {
      const li = document.createElement('li');
      if (typeof r === 'string' && (r.includes("Suspicious keywords:") || r.includes("Suspicious text:"))) {
        const titleDiv = document.createElement("div");
        titleDiv.className = "reason-title";
        titleDiv.textContent = "⚠️ DETECTED TRIGGERS:";
        li.appendChild(titleDiv);

        const chipContainer = document.createElement("div");
        chipContainer.className = "chip-container";

        let cleanText = r.replace("Suspicious keywords:", "").replace("Suspicious text:", "").trim();
        let keywords = cleanText.split(",");

        keywords.forEach(word => {
          word = word.trim();
          if (word && word !== "none") {
            const span = document.createElement("span");
            span.className = "keyword-chip";
            span.textContent = word;
            chipContainer.appendChild(span);
          }
        });
        li.appendChild(chipContainer);
      } else {
        li.textContent = '• ' + r;
      }
      reasonsList.appendChild(li);
    }
  }

  // KILL SWITCH LOGIC (fixed casing)
  if (data.score >= 75 || data.verdict.toLowerCase() === 'phishing') {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      if (tabs[0]) {
        const safePage = chrome.runtime.getURL("warning.html") +
          `?score=${data.score}&verdict=${data.verdict}&ref=${encodeURIComponent(tabs[0].url)}`;
        chrome.tabs.update(tabs[0].id, { url: safePage });
      }
    });
  }
}

function showError(err) {
  errorEl.textContent = '❌ ' + String(err);
  errorEl.classList.remove('hidden');
  setStatus('System Error');
  resultArea.classList.remove('hidden');
  scoreEl.textContent = 'ERR';
  verdictEl.textContent = 'ERROR';
  verdictEl.className = 'verdict neutral';
  barFill.style.width = '0%';
}

analyzeBtn.addEventListener('click', async () => {
  try {
    analyzeBtn.classList.add('loading');
    analyzeBtn.disabled = true;

    setStatus('Capturing Snapshot...');
    resultArea.classList.add('hidden');
    errorEl.classList.add('hidden');

    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    const tab = tabs && tabs[0];
    if (!tab || !tab.id || !tab.url) {
      setStatus('Error: No active tab');
      return;
    }

    const screenshotUrl = await chrome.tabs.captureVisibleTab(null, { format: 'png' });

    setStatus('Scanning content...');
    const execRes = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        try { return (document.body.innerText || "").replace(/\s+/g, " ").trim(); }
        catch (e) { return ""; }
      }
    });
    const text = (execRes && execRes[0] && execRes[0].result) || "";

    setStatus('Analyzing...');
    const API = 'http://127.0.0.1:8000/analyze';
    const payload = {
      url: tab.url,
      text: text,
      screenshot: screenshotUrl,
      request_id: 'ext-' + Date.now()
    };

    const resp = await fetch(API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!resp.ok) throw new Error('Server Error ' + resp.status);

    const data = await resp.json();
    setStatus('Analysis Complete');
    showResult(data);

  } catch (err) {
    console.error(err);
    showError("Is the Backend Running?");
  } finally {
    analyzeBtn.classList.remove('loading');
    analyzeBtn.disabled = false;
  }
});