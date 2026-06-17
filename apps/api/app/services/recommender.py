import re

def parse_price(price_str):
    if not price_str:
        return 0.0
    # Try to extract numbers from price string
    numbers = re.findall(r'\d+', str(price_str).replace(',', ''))
    if numbers:
        return float(numbers[0])
    return 0.0

def _get_spec_value(phone, aspect):
    # Fallback heuristics for scoring based on new dataset
    if not phone.raw_specs:
        return 50.0
        
    raw_str = str(phone.raw_specs).lower()
    
    if aspect == "camera":
        if "108 mp" in raw_str: return 90.0
        elif "64 mp" in raw_str: return 80.0
        elif "50 mp" in raw_str: return 75.0
        return 60.0
    elif aspect == "battery":
        if "5000 mah" in raw_str: return 90.0
        elif "4500 mah" in raw_str: return 80.0
        return 60.0
    elif aspect == "performance":
        if "snapdragon 8" in raw_str or "a17" in raw_str: return 95.0
        elif "snapdragon 7" in raw_str: return 80.0
        return 65.0
    
    return 70.0 # Default fallback score

from typing import List, Dict, Any
from app.models.phone import PhoneDetails
from app.models.query import EasyRecommendRequest, MediumRecommendRequest
from app.core.constants import PERSONA_WEIGHTS

def score_phones(phones: List[PhoneDetails], weights: Dict[str, float], budget: float) -> List[Dict[str, Any]]:
    scored = []
    
    for phone in phones:
        parsed_price = parse_price(phone.price)
        if parsed_price > budget * 1.05 or parsed_price == 0:
            continue
            
        # Smart Age Scoring: Heavily prioritize 2025/2026 phones.
        raw_str = str(phone.raw_specs).lower()
        if "2026" in raw_str:
            age_multiplier = 1.3  # Huge boost for newest phones
        elif "2025" in raw_str:
            age_multiplier = 1.1  # Solid boost for recent phones
        elif "2024" in raw_str:
            age_multiplier = 0.8  # Slight penalty
        else:
            age_multiplier = 0.3  # Massive penalty for 2023 or older
            
        final_score = 0.0
        match_reasons = []
        trade_offs = []
        
        for aspect, weight in weights.items():
            spec_val = _get_spec_value(phone, aspect)
            final_score += weight * (spec_val / 100.0)
            
            if spec_val > 80:
                match_reasons.append(f"Great {aspect}")
            elif spec_val < 65:
                trade_offs.append(f"Average {aspect}")
                
        # Price Utilization Factor:
        price_utilization = min(parsed_price / budget, 1.0)
        
        # Multiply final score by age multiplier and premiumness.
        final_score = final_score * age_multiplier * (0.5 + (0.5 * price_utilization))
        
        if parsed_price < budget * 0.6:
            final_score *= 0.5 # Strongly penalize extremely cheap phones

        # Ensure score doesn't exceed 100
        final_score = min(final_score, 1.0)

        scored.append({
            "phone": phone,
            "score": final_score * 100, 
            "match_reasons": match_reasons[:3],
            "trade_offs": trade_offs[:2]
        })
        
    return sorted(scored, key=lambda x: x["score"], reverse=True)

def recommend_easy(phones: List[PhoneDetails], request: EasyRecommendRequest) -> List[Dict[str, Any]]:
    weights = PERSONA_WEIGHTS.get(request.persona, PERSONA_WEIGHTS.get("General", {"camera":0.3, "performance":0.4, "battery":0.3}))
    return score_phones(phones, weights, request.budget)

def recommend_medium(phones: List[PhoneDetails], request: MediumRecommendRequest) -> List[Dict[str, Any]]:
    filtered = phones
    if request.preferred_brands:
        filtered = [p for p in filtered if p.brand in request.preferred_brands]
    if request.avoid_brands:
        filtered = [p for p in filtered if p.brand not in request.avoid_brands]
        
    weights = request.priorities if request.priorities else PERSONA_WEIGHTS.get("General", {"camera":0.3, "performance":0.4, "battery":0.3})
    return score_phones(filtered, weights, request.budget)
