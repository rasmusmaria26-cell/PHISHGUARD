# backend/app/content_analyzer.py
from typing import Tuple
import re

SUSPICIOUS_PHRASES = [
    "verify your account",
    "update your information",
    "confirm your identity",
    "your account has been suspended",
    "your account will be closed",
    "unauthorized login",
    "verify payment",
    "click below to verify",
    "urgent action required",
    "password expired",
    "transfer funds",
    "provide your password",
    "enter your credentials",
    " Click Image"
]

def score_text_simple(text: str) -> Tuple[int, str]:
    if not text or len(text.strip()) < 20:
        return 0, "no substantial text"

    lower = text.lower()
    hits = []
    for phrase in SUSPICIOUS_PHRASES:
        if phrase in lower:
            hits.append(phrase)

    verify_count = len(re.findall(r"\bverify\b", lower))
    password_count = len(re.findall(r"\bpassword\b", lower))

    # base count from phrase hits
    count = len(hits)
    if verify_count > 1:
        count += 1
    if password_count > 0:
        count += 1

    score = min(100, count * 20)  # each count ≈ 20 points
    note = "hits: " + ", ".join(hits) if hits else "no suspicious phrases"
    return score, note
