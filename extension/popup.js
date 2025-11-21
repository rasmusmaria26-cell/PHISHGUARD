// popup.js - Cyberpunk UI Logic + Kill Switch
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
  
  // Dynamic color fill based on score
  if(pct >= 70) barFill.style.background = getComputedStyle(document.documentElement).getPropertyValue('--danger');
  else if(pct >= 35) barFill.style.background = getComputedStyle(document.documentElement).getPropertyValue('--warn');
  else barFill.style.background = getComputedStyle(document.documentElement).getPropertyValue('--safe');
}

function showResult(data){
  resultArea.classList.remove('hidden');
  errorEl.classList.add('hidden');

  scoreEl.textContent = data.score ?? '—';
  urlScoreEl.textContent = data.url_score ?? '0';
  contentScoreEl.textContent = data.content_score ?? '0';
  setProgress(data.score ?? 0);

  // Verdict styling
  const v = (data.verdict || 'neutral');
  verdictEl.textContent = v.toUpperCase();
  verdictEl.className = 'verdict ' + (v === 'safe' ? 'safe' : v === 'suspicious' ? 'suspicious' : v === 'danger' ? 'danger' : 'neutral');

  // --- IMPROVED REASONS LOGIC (The Chips) ---
  const reasons = Array.isArray(data.reasons) ? data.reasons : (data.reasons ? [data.reasons] : []);
  reasonsList.innerHTML = '';

  if(reasons.length === 0) {
    reasonsList.innerHTML = '<li>No suspicious indicators found.</li>';
  } else {
    for(const r of reasons) {
      const li = document.createElement('li');

      // Check if this is the keyword list that needs formatting
      // Matches "Suspicious keywords: ..." or "Suspicious text: ..."
      if (typeof r === 'string' && (r.includes("Suspicious keywords:") || r.includes("Suspicious text:"))) {
        
        // 1. Create Title Label
        const titleDiv = document.createElement("div");
        titleDiv.className = "reason-title";
        titleDiv.textContent = "DETECTED TRIGGERS:";
        li.appendChild(titleDiv);

        // 2. Create Container for Chips
        const chipContainer = document.createElement("div");
        chipContainer.className = "chip-container";

        // 3. Clean the string and split by comma
        let cleanText = r.replace("Suspicious keywords:", "").replace("Suspicious text:", "").trim();
        let keywords = cleanText.split(",");

        // 4. Create a chip for each word
        keywords.forEach(word => {
            word = word.trim();
            if(word && word !== "none") {
                const span = document.createElement("span");
                span.className = "keyword-chip";
                span.textContent = word;
                chipContainer.appendChild(span);
            }
        });

        li.appendChild(chipContainer);

      } else {
        // Regular text reason
        li.textContent = r;
      }

      reasonsList.appendChild(li);
    }
  }

  // Raw debug info (hidden)
  rawEl.textContent = JSON.stringify(data, null, 2);
  rawEl.classList.add('hidden');

  // --- KILL SWITCH LOGIC (Redirect to Warning Page) ---
  if (data.score >= 60 || data.verdict === 'Phishing') {
      chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
          if(tabs[0]) {
              // Redirect to local warning.html with parameters
              const safePage = chrome.runtime.getURL("warning.html") + 
                               `?score=${data.score}&verdict=${data.verdict}&ref=${encodeURIComponent(tabs[0].url)}`;
              
              chrome.tabs.update(tabs[0].id, { url: safePage });
          }
      });
  }
}

function showError(err){
  errorEl.textContent = String(err);
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
    setStatus('Accessing page content...');
    resultArea.classList.add('hidden');
    errorEl.classList.add('hidden');

    // 1. Get Active Tab
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    const tab = tabs && tabs[0];
    if(!tab || !tab.id || !tab.url){
      setStatus('Error: No active tab');
      return;
    }

    // 2. Extract Text
    setStatus('Scanning page structure...');
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
    
    // 3. Send to AI Brain
    setStatus('Analyzing patterns...');
    
    const API = 'http://127.0.0.1:8000/analyze'; 
    const payload = { url: tab.url, text, request_id: 'ext-' + Date.now() };

    const resp = await fetch(API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if(!resp.ok){
      const body = await resp.text().catch(()=>'');
      throw new Error('Server Error ' + resp.status);
    }

    const data = await resp.json();
    setStatus('Analysis Complete');
    showResult(data);

  } catch(err) {
    console.error(err);
    showError("Is the Backend Running?");
  }
});