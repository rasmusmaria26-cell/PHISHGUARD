import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from .models import AnalyzeRequest, AnalyzeResponse, ReportRequest
from .heuristic import score_url
from .content_analyzer import analyze_content 
from .image_analyzer import analyze_screenshot 
import os
import csv
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Phishing Guard Backend")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Mount static files for brand logos
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "data")), name="static")

@app.get("/")
def health_check():
    return {"status": "running", "service": "Phishing Guard API"}

# Serve test pages
@app.get("/visual_trap.html", response_class=HTMLResponse)
async def serve_paypal():
    with open(os.path.join(BASE_DIR, "visual_trap.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/test_netflix.html", response_class=HTMLResponse)
async def serve_netflix():
    with open(os.path.join(BASE_DIR, "test_netflix.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/test_google.html", response_class=HTMLResponse)
async def serve_google():
    with open(os.path.join(BASE_DIR, "test_google.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/test_dashboard.html", response_class=HTMLResponse)
async def serve_dashboard():
    with open(os.path.join(BASE_DIR, "test_dashboard.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    logger.info(f"Analyzing URL: {req.url}")
    
    url_res = score_url(req.url)
    url_score = url_res.get("score", 0)
    
    content_res = analyze_content(req.text)
    content_score = content_res.get("score", 0)

    visual_score = 0
    visual_reason = None
    
    if req.screenshot:
        vis_res = analyze_screenshot(req.screenshot, req.url)
        visual_score = vis_res.get("score", 0)
        logger.info(f"Visual check: Score={visual_score}, Reason={vis_res.get('reason')}")
        if vis_res.get("reason") and visual_score > 50:
            visual_reason = f"Visuals: {vis_res['reason']}"

    original_visual_score = visual_score
    if content_score < 5 and 50 < original_visual_score < 80:
        logger.info("[VISUAL VETO] Reducing visual weight")
        visual_score = original_visual_score * 0.3
    
    if url_score > 80:
        final_score = max(url_score, content_score, visual_score) 
    else:
        final_score = (url_score * 0.2) + (content_score * 0.5) + (visual_score * 0.3)

    final_score = int(final_score)
    
    # sensitivity thresholds
    s = req.sensitivity.lower()
    if s == 'strict':
        p_thresh, s_thresh = 65, 35
    elif s == 'permissive':
        p_thresh, s_thresh = 85, 60
    else: # balanced
        p_thresh, s_thresh = 75, 45

    if final_score >= p_thresh:
        verdict = "phishing"
    elif final_score >= s_thresh:
        verdict = "suspicious"
    else:
        verdict = "safe"

    reasons = url_res.get("reasons", [])
    if content_res.get("keyword_hits") and content_res["keyword_hits"] != "No suspicious keywords":
        reasons.append(f"Suspicious keywords: {content_res['keyword_hits']}")
    if content_res.get("ml_probability", 0) > 70:
        reasons.append("AI Model recognized phishing writing style")
    if visual_reason and visual_score > 0: 
        reasons.append(visual_reason)

    logger.info(f"Analysis complete: Score={final_score}, Verdict={verdict}")

    # --- CSV LOGGING ---
    SCANS_FILE = os.path.join(BASE_DIR, "scans.csv")
    try:
        file_exists = os.path.isfile(SCANS_FILE)
        with open(SCANS_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header if new file
            if not file_exists:
                writer.writerow(["Timestamp", "URL", "Score", "Verdict", "Reasons", "Strategy"])
            
            # Write scan data
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                req.url,
                final_score,
                verdict,
                "; ".join(reasons),
                "Auto-Scan" if "auto" in req.request_id else "Manual"
            ])
    except Exception as e:
        logger.error(f"Failed to log to CSV: {e}")
    # -------------------

    return AnalyzeResponse(
        request_id=req.request_id,
        url=req.url,
        score=final_score,
        verdict=verdict,
        reasons=reasons,
        url_score=url_score,
        content_score=content_score,
        visual_score=int(visual_score)
    )

@app.post("/report")
async def report_issue(req: ReportRequest):
    logger.info(f"Received feedback report for: {req.url}")
    
    FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.csv")
    try:
        file_exists = os.path.isfile(FEEDBACK_FILE)
        with open(FEEDBACK_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "URL", "Reason", "Comments"])
            
            writer.writerow([
                req.timestamp,
                req.url,
                req.reason,
                req.comments
            ])
        return {"status": "success", "message": "Report logged"}
    except Exception as e:
        logger.error(f"Failed to log feedback: {e}")
        return {"status": "error", "message": str(e)}