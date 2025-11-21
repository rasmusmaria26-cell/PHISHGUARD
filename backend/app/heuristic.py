# backend/app/heuristic.py
import re
from urllib.parse import urlparse

SUSPICIOUS_TOKENS = [
    "login", "verify", "secure", "account", "update",
    "paypal", "bank", "confirm", "signin", "authenticate"
]

def score_url(url: str) -> dict:
    """
    Simple lexical heuristic for URL scoring.
    Returns: {"score": int, "verdict": str, "reasons": [str,...]}
    """
    reasons = []
    try:
        parsed = urlparse(url)
        domain = (parsed.netloc or "").lower()
        path = (parsed.path or "").lower()
    except Exception:
        return {"score": 100, "verdict": "danger", "reasons": ["invalid url"]}

    score = 0

    # domain length
    if len(domain) > 40:
        score += 25
        reasons.append("very long domain")
    elif len(domain) > 25:
        score += 10
        reasons.append("long domain")

    # hyphens and odd chars
    if domain.count("-") >= 2:
        score += 15
        reasons.append("multiple hyphens")
    if re.search(r"[^a-z0-9\.\-:]", domain):
        score += 15
        reasons.append("odd characters in domain")

    # many subdomains
    if domain.count(".") >= 3:
        score += 15
        reasons.append("many subdomains")

    # suspicious tokens
    for t in SUSPICIOUS_TOKENS:
        if t in domain or t in path:
            score += 20
            reasons.append(f"contains token '{t}'")
            break

    # digits ratio
    digits = sum(c.isdigit() for c in domain)
    if len(domain) > 0 and digits / len(domain) > 0.25:
        score += 10
        reasons.append("many digits in domain")

    # clamp and verdict
    score = min(100, score)
    if score >= 70:
        verdict = "danger"
    elif score >= 35:
        verdict = "suspicious"
    else:
        verdict = "safe"

    return {"score": score, "verdict": verdict, "reasons": reasons}
