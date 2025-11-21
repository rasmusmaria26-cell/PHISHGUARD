// popup.js - improved UI feedback
const analyzeBtn = document.getElementById('analyze');
const statusEl = document.getElementById('status');
const resultArea = document.getElementById('resultArea');
const scoreEl = document.getElementById('score');
const verdictEl = document.getElementById('verdict');
const barFill = document.getElementById('bar-fill');
const urlScoreEl = document.getElementById('url-score');
const contentScoreEl = document.getElementById('content-score');
const reasonsList = document.getElementById('reasonsList');
const errorEl = document.getElementById('error');
const rawEl = document.getElementById('raw');

function setStatus(txt){
  statusEl.textContent = txt;
  console.log('[popup] ', txt);
}

function colorForScore(s){
  if(s >= 70) return 'danger';
  if(s >= 35) return 'suspicious';
  return 'safe';
}

function setProgress(score){
  const pct = Math.max(0, Math.min(100, score));
  barFill.style.width = pct + '%';
  // color fill
  if(pct >= 70) barFill.style.background = getComputedStyle(document.documentElement).getPropertyValue('--danger');
  else if(pct >= 35) barFill.style.background = getComputedStyle(document.documentElement).getPropertyValue('--warn');
  else barFill.style.background = getComputedStyle(document.documentElement).getPropertyValue('--ok');
}

function showResult(data){
  resultArea.classList.remove('hidden');
  errorEl.classList.add('hidden');

  scoreEl.textContent = data.score ?? '—';
  urlScoreEl.textContent = data.url_score ?? 'n/a';
  contentScoreEl.textContent = data.content_score ?? 'n/a';
  setProgress(data.score ?? 0);

  // verdict styling
  const v = (data.verdict || 'neutral');
  verdictEl.textContent = v.toUpperCase();
  verdictEl.className = 'verdict ' + (v === 'safe' ? 'safe' : v === 'suspicious' ? 'suspicious' : v === 'danger' ? 'danger' : 'neutral');

  // reasons list
  const reasons = Array.isArray(data.reasons) ? data.reasons : (data.reasons ? [data.reasons] : []);
  reasonsList.innerHTML = '';
  if(reasons.length === 0) {
    reasonsList.innerHTML = '<li>None</li>';
  } else {
    for(const r of reasons) {
      const li = document.createElement('li');
      li.textContent = r;
      reasonsList.appendChild(li);
    }
  }

  // raw (hidden by default)
  rawEl.textContent = JSON.stringify(data, null, 2);
  rawEl.classList.add('hidden');
}

function showError(err){
  errorEl.textContent = String(err);
  errorEl.classList.remove('hidden');
  setStatus('Error — see console');
  resultArea.classList.remove('hidden'); // keep UI visible
  scoreEl.textContent = '—';
  verdictEl.textContent = 'ERROR';
  verdictEl.className = 'verdict neutral';
  barFill.style.width = '0%';
}

analyzeBtn.addEventListener('click', async () => {
  try {
    setStatus('Getting active tab...');
    resultArea.classList.add('hidden');
    errorEl.classList.add('hidden');

    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    const tab = tabs && tabs[0];
    if(!tab || !tab.id || !tab.url){
      setStatus('No active tab URL');
      return;
    }

    setStatus('Extracting page text...');
    const execRes = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        try {
          const body = document.body;
          if(!body) return "";
          return (body.innerText || "").replace(/\s+/g, " ").trim();
        } catch(e) {
          return "";
        }
      }
    });

    const text = (execRes && execRes[0] && execRes[0].result) || "";
    setStatus('Contacting backend...');

    const payload = { url: tab.url, text, request_id: 'ext-' + Date.now() };
    const API = 'http://localhost:8000/analyze';

    const resp = await fetch(API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if(!resp.ok){
      const body = await resp.text().catch(()=>'');
      throw new Error('HTTP ' + resp.status + ' ' + body);
    }

    const data = await resp.json();
    setStatus('Result received');
    showResult(data);

  } catch(err) {
    console.error(err);
    showError(err);
  }
});
