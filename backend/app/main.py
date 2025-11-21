import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

# Import your specific files
from .models import AnalyzeRequest, AnalyzeResponse
from .heuristic import score_url
from .content_analyzer import analyze_content  # <--- This uses your new code

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")
logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="Phishing Guard Backend")

# --- CORS SETUP ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "running", "service": "Phishing Guard API"}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    """
    Orchestrates the analysis:
    1. Checks URL (heuristic.py)
    2. Checks Content (content_analyzer.py - ML + Keywords)
    3. Combines them for a final verdict
    """
    
    # 1. Analyze URL
    # (Checks for IP addresses, length, weird domains)
    url_res = score_url(req.url)
    url_score = url_res.get("score", 0)
    
    # 2. Analyze Content
    # (Uses your new function that handles ML loading internally)
    # Your analyze_content function expects a string, so we pass req.text
    content_res = analyze_content(req.text)
    content_score = content_res.get("score", 0)

    # 3. Final Weighting
    # Logic: If URL is dangerous (score > 50), it counts for 60% of the verdict.
    # Otherwise, Content is king (counts for 70%).
    if url_score > 50:
        final_score = (url_score * 0.6) + (content_score * 0.4)
    else:
        final_score = (url_score * 0.3) + (content_score * 0.7)

    final_score = int(final_score)

    # 4. Aggregate Reasons
    reasons = url_res.get("reasons", [])
    
    # Add content reasons
    if content_res.get("keyword_hits") and content_res["keyword_hits"] != "No suspicious keywords":
        reasons.append(f"Suspicious keywords: {content_res['keyword_hits']}")
    
    if content_res.get("ml_probability", 0) > 70:
        reasons.append("AI Model recognized phishing writing style")

    # 5. Determine Verdict
    if final_score > 75:
        verdict = "Phishing"
    elif final_score > 45:
        verdict = "Suspicious"
    else:
        verdict = "Safe"

    logger.info(f"Analyzed {req.url} -> Score: {final_score} ({verdict})")

    return AnalyzeResponse(
        request_id=req.request_id,
        url=req.url,
        score=final_score,
        verdict=verdict,
        reasons=reasons,
        url_score=url_score,
        content_score=content_score
    )