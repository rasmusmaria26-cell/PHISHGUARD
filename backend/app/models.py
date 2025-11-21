from pydantic import BaseModel
from typing import List, Optional

class AnalyzeRequest(BaseModel):
    url: str
    text: str            # main.py uses 'text', not 'html_text'
    request_id: str = "default-id"

class AnalyzeResponse(BaseModel):
    request_id: str
    url: str
    score: int
    verdict: str
    reasons: List[str]
    url_score: int
    content_score: int