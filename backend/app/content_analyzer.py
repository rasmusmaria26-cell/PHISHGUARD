import joblib
# Trigger reload for new model
import os
import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../models/content_model.joblib")
LOADED_MODEL = None

# Attempt to load model on startup
try:
    if os.path.exists(MODEL_PATH):
        LOADED_MODEL = joblib.load(MODEL_PATH)
        logger.info(f"ML Model loaded successfully from {MODEL_PATH}")
    else:
        logger.warning("Model file not found. Running in Heuristic-only mode.")
except (FileNotFoundError, EOFError, ValueError) as e:
    logger.error(f"Error loading model: {e}")

SUSPICIOUS_PHRASES = [
    "verify your account", "update your information", "confirm your identity",
    "your account has been suspended", "unauthorized login", "verify payment",
    "urgent action required", "password expired", "enter your credentials",
    "package delivery", "delivery failure", "tracking number", "unsuccessful delivery",
    "shipping address", "shipment pending", "payment declin", "account limit"
]

def analyze_content(text: str) -> dict:
    """
    Main entry point. Returns a dictionary with detailed scoring.
    """
    # 1. Clean text (remove extra whitespace)
    clean_text = " ".join(text.split())
    
    if not clean_text or len(clean_text) < 20:
        return {"score": 0, "verdict": "Safe (Insufficient Content)", "method": "None"}

    # 2. Run ML Prediction (Primary)
    ml_score = 0
    ml_verdict = "Safe"
    
    if LOADED_MODEL:
        # predict_proba returns [[prob_safe, prob_phishing]]
        # We take the second value (index 1) for phishing probability
        probability = LOADED_MODEL.predict_proba([clean_text])[0][1]
        ml_score = int(probability * 100)
    
    # 3. Run Keyword Heuristic (Secondary/Explanation)
    keyword_score, keyword_note = score_text_heuristic(clean_text)
    
    # 4. Fusion Logic
    # If ML is available, it carries 80% weight. Keywords carry 20%.
    # If ML is missing, Keywords carry 100%.
    if LOADED_MODEL:
        # If Heuristic detected strong signals (>= 50), trust it over ML (which might fail on short text)
        if keyword_score >= 50:
             final_score = max(ml_score, keyword_score)
             method = "Hybrid (Heuristic Priority)"
        else:
            final_score = (ml_score * 0.8) + (keyword_score * 0.2)
            method = "Hybrid (ML Priority)"
    else:
        final_score = keyword_score
        method = "Heuristic Only"

    return {
        "score": int(final_score),
        "ml_probability": ml_score,
        "keyword_hits": keyword_note,
        "verdict": "Phishing" if final_score > 60 else "Safe",
        "method": method
    }

def score_text_heuristic(text: str) -> Tuple[int, str]:
    """
    Your original keyword logic, slightly optimized.
    """
    lower = text.lower()
    hits = [phrase for phrase in SUSPICIOUS_PHRASES if phrase in lower]

    # Check specific keywords using Regex boundaries to avoid partial matches
    # e.g., prevent matching "crossword" when looking for "password"
    verify_count = len(re.findall(r"\bverify\b", lower))
    password_count = len(re.findall(r"\bpassword\b", lower))
    urgent_count = len(re.findall(r"\burgent\b", lower))
    delivery_count = len(re.findall(r"\bdelivery\b", lower))
    suspend_count = len(re.findall(r"\bsuspend", lower))
    package_count = len(re.findall(r"\bpackage", lower))
    failure_count = len(re.findall(r"\bfailure", lower))

    count = len(hits)
    if verify_count > 1: count += 1
    if password_count > 0: count += 1
    if urgent_count > 0: count += 1
    if delivery_count > 0: count += 1
    if suspend_count > 0: count += 1
    if package_count > 0: count += 1
    if failure_count > 0: count += 1

    score = min(100, count * 25)
    note = ", ".join(hits) if hits else "No suspicious keywords"
    
    return score, note