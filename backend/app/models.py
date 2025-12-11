from pydantic import BaseModel
from typing import List, Optional

class AnalyzeRequest(BaseModel):
    url: str
    text: str
    screenshot: Optional[str] = None  # <--- THIS WAS MISSING!
    sensitivity: str = 'balanced'
    request_id: str = "default-id"

class AnalyzeResponse(BaseModel):
    request_id: str
    url: str
    score: int
    verdict: str
    reasons: List[str]
    url_score: int
    content_score: int
    visual_score: int = 0  # <--- Good to have this too

class ReportRequest(BaseModel):
    url: str
    reason: str
    comments: Optional[str] = ""
    timestamp: str