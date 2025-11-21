# backend/app/main.py
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from .models import AnalyzeRequest, AnalyzeResponse
from .heuristic import score_url
from .content_analyzer import score_text_simple
from .content_model import ContentModel

# ensure logger visible in uvicorn output
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")
logger = logging.getLogger("uvicorn.error")

# single FastAPI app (only one)
app = FastAPI(title="Brain - URL Analyzer (Phase 3)")

# DEV only: allow extension (localhost) to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# global placeholder for ML model
content_model = None

# reliable startup loader (runs inside worker)
@app.on_event("startup")
async def load_ml_model():
    global content_model
    try:
        content_model = ContentModel()   # loads backend/models/content_model.joblib
        logger.info("Loaded ML content model")
        print("Loaded ML content model")
    except Exception as e:
        content_model = None
        logger.exception("ML content model not loaded:")
        print("ML content model not loaded:", e)

# dev-only simple CORS fallback (keep alongside CORSMiddleware)
@app.middleware("http")
async def _dev_cors_fallback(request, call_next):
    # respond to preflight immediately
    if request.method == "OPTIONS":
        resp = PlainTextResponse("ok")
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        return resp

    # normal requests: call downstream and attach CORS headers
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return response

# health (reports ML status)
@app.get("/health")
async def health():
    return {"status": "ok", "ml_loaded": bool(content_model)}

# main analyze endpoint
# tuning constants (change these easily)
MIN_TEXT_LEN = 10   # minimum characters to run ML
ML_WEIGHT = 0.7     # content weight (0..1); URL weight = 1 - ML_WEIGHT
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    # URL scoring
    url_str = str(req.url)
    url_res = score_url(url_str)
    url_score = int(url_res.get("score", 0))
    reasons = url_res.get("reasons", []).copy()

    # Content scoring (use ML if available and text long enough; fallback to heuristic)
    content_score = 0
    content_note = "none"
    text = getattr(req, "text", None)

    if text and len(text.strip()) >= MIN_TEXT_LEN:
        if content_model:
            cs, note = content_model.score(text)
            content_score = int(cs)
            content_note = f"content_ml: {note}"
            reasons.append(content_note)
        else:
            cs, note = score_text_simple(text)
            content_score = int(cs)
            content_note = f"content_heur: {note}"
            reasons.append(content_note)
    else:
        if text:
            reasons.append("content: too short")
        else:
            reasons.append("content: none")

    # Combine with weights
    final_score = int((url_score * (1 - ML_WEIGHT)) + (content_score * ML_WEIGHT))

    # Detailed logging so you can see exactly what contributed
    logger.info(
        f"ANALYZE url={url_str} url_score={url_score} content_score={content_score} final={final_score}"
    )
    print(f"ANALYZE url={url_str} url_score={url_score} content_score={content_score} final={final_score}")

    # Map to verdict
    if final_score >= 70:
        verdict = "danger"
    elif final_score >= 35:
        verdict = "suspicious"
    else:
        verdict = "safe"

    return {
        "request_id": req.request_id,
    "url": req.url,
    "score": final_score,
    "verdict": verdict,
    "reasons": reasons,
    "url_score": url_score,
    "content_score": content_score
    }