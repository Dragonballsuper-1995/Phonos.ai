from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from .phone import PhoneDetails


class RecommendedPhone(BaseModel):
    phone: PhoneDetails
    score: float
    match_reasons: List[str]
    trade_offs: List[str]
    ai_verified: bool = False
    verify_reason: Optional[str] = None
    ai_explanation: Optional[str] = None


class RecommendationResponse(BaseModel):
    recommendations: List[RecommendedPhone]
    persona_detected: Optional[str] = None
    budget_used: float


class CompareResponse(BaseModel):
    phones: List[PhoneDetails]
    differences: Dict[str, Any] = {}
