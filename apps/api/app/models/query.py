from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class EasyRecommendRequest(BaseModel):
    persona: str = Field(..., description="E.g., Student, Gamer, Professional")
    budget: float = Field(..., description="Maximum budget in INR")
    
class MediumRecommendRequest(BaseModel):
    budget: float
    priorities: Dict[str, float] = Field(
        default_factory=dict, 
        description="Aspect weights adding up to 1.0 (e.g. {'camera': 0.4, 'battery': 0.6})"
    )
    preferences: List[str] = Field(default_factory=list, description="E.g., ['5G', 'Compact', 'Fast Charging']")
    preferred_brands: List[str] = Field(default_factory=list)
    avoid_brands: List[str] = Field(default_factory=list)

class PhoneSearchRequest(BaseModel):
    query: str
