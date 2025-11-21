# backend/app/models.py
from pydantic import BaseModel, HttpUrl
from typing import Optional, List

class AnalyzeRequest(BaseModel):
    url: HttpUrl
    text: Optional[str] = None
    request_id: Optional[str] = None

class AnalyzeResponse(BaseModel):
    request_id: Optional[str] = None
    url: HttpUrl
    score: int
    verdict: str
    reasons: List[str]
    url_score: int
    content_score: int
