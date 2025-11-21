from urllib.parse import urlparse
import socket
import re

def score_url(url: str) -> dict:
    score = 0
    reasons = []
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
    except:
        return {"score": 0, "reasons": ["Invalid URL format"]}

    # 1. IP Check
    try:
        socket.inet_aton(domain)
        score += 60
        reasons.append("IP address used as domain")
    except socket.error:
        pass

    # 2. Length Check
    if len(url) > 75:
        score += 10
        reasons.append("URL suspiciously long")

    # 3. Keyword Check
    suspicious = ['login', 'verify', 'update', 'account', 'banking', 'secure']
    # Check if keywords appear in the path (not the domain itself usually)
    path = parsed.path + parsed.query
    if any(s in path.lower() for s in suspicious):
        score += 10
        reasons.append("Suspicious keywords in URL path")

    return {
        "score": min(100, score),
        "reasons": reasons
    }