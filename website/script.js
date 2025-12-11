document.addEventListener('DOMContentLoaded', () => {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Mockup Animation: Simulate scanning process in the hero image
    const scoreNumber = document.querySelector('.mock-number');
    let score = 0;

    // Simulate score counting up every few seconds to look alive
    setInterval(() => {
        animateScore();
    }, 5000);

    function animateScore() {
        score = 0;
        const interval = setInterval(() => {
            score += 2;
            if (score > 100) score = 100;
            scoreNumber.textContent = score;

            if (score === 100) {
                clearInterval(interval);
                setTimeout(() => { scoreNumber.textContent = '0'; }, 3000);
            }
        }, 20);
    }

    // --- Live Demo Scanner Logic ---
    const demoBtn = document.getElementById('demoBtn');
    const demoInput = document.getElementById('demoUrl');
    const demoResult = document.getElementById('demoResult');

    // Result Elements
    const dVerdict = document.getElementById('demoVerdict');
    const dScore = document.getElementById('demoScore');
    const dVisual = document.getElementById('demoVisual');
    const dContent = document.getElementById('demoContent');
    const dUrl = document.getElementById('demoUrlScore');
    const dReasons = document.getElementById('demoReasons');

    if (demoBtn) {
        demoBtn.addEventListener('click', async () => {
            const url = demoInput.value;
            if (!url) return;

            // UI Loading State
            demoBtn.textContent = 'Scanning...';
            demoBtn.style.opacity = '0.7';
            demoResult.classList.add('hidden');

            try {
                // Determine if we need to mock data (if backend not running) or fetch
                // Try fetching first
                const response = await fetch('http://127.0.0.1:8000/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        url: url,
                        text: "Demo scan content text...", // Cannot crawl from browser due to CORS
                        screenshot: "", // Cannot screenshot from browser
                        request_id: "web-demo-" + Date.now()
                    })
                });

                if (!response.ok) throw new Error('API Error');
                const data = await response.json();

                // Update UI
                renderDemoResult(data);

            } catch (err) {
                console.error("Backend offline or error, showing mock for demo", err);
                // Fallback mock for demo purposes if backend isn't running locally
                const mockScore = url.includes('google') ? 0 : 85;
                renderDemoResult({
                    score: mockScore,
                    verdict: mockScore > 50 ? 'phishing' : 'safe',
                    visual_score: 0,
                    content_score: 0,
                    url_score: mockScore,
                    reasons: mockScore > 50 ? ['URL mimics legitimate brand', 'Suspicious domain pattern'] : []
                });
            } finally {
                demoBtn.textContent = 'Scan URL';
                demoBtn.style.opacity = '1';
                demoResult.classList.remove('hidden');
            }
        });
    }

    function renderDemoResult(data) {
        dScore.textContent = data.score;
        dVerdict.textContent = data.verdict.toUpperCase();
        dVerdict.className = `verdict-badge ${data.verdict.toLowerCase()}`;

        dVisual.textContent = data.visual_score || 0;
        dContent.textContent = data.content_score || 0;
        dUrl.textContent = data.url_score || 0;

        // Handle reasons
        let reasonList = [];
        if (Array.isArray(data.reasons)) reasonList = data.reasons;
        else if (typeof data.reasons === 'string') reasonList = data.reasons.split(';');

        if (reasonList.length > 0) {
            dReasons.innerHTML = '<strong>Risk Factors:</strong><br>' + reasonList.join('<br>');
        } else {
            dReasons.innerHTML = 'No significant threats detected.';
        }
    }
});
