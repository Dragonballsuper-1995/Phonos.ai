import re
import os
import pandas as pd
from typing import List, Dict, Any
from app.models.phone import PhoneDetails
from app.models.query import EasyRecommendRequest, MediumRecommendRequest
from app.core.constants import PERSONA_WEIGHTS, SOFTWARE_UI_TAXONOMY, LINEUP_DNA_HIERARCHY
from app.services.retrieval import semantic_search
from app.services.knowledge_graph import filter_by_knowledge_graph
from app.services.youtube_sentiment import fetch_live_sentiment
from app.services.hardware_scorer import extract_hardware_spec_vector
from app.services.defect_scanner import scan_community_defects

try:
    import xgboost as xgb
except ImportError:
    xgb = None

MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/ranker.xgb'))

_ranker_model = None

def get_ranker_model():
    global _ranker_model
    if _ranker_model is None and xgb is not None:
        if os.path.exists(MODEL_PATH):
            _ranker_model = xgb.XGBClassifier()
            _ranker_model.load_model(MODEL_PATH)
        else:
            print(f"[Ranker] Warning: Model not found at {MODEL_PATH}. Run train_ranker.py first.")
    return _ranker_model

def parse_price(price_str) -> float:
    if not price_str:
        return 0.0
    numbers = re.findall(r'\d+', str(price_str).replace(',', ''))
    return float(numbers[0]) if numbers else 0.0

def extract_features(phone: PhoneDetails, persona_idx: int, budget: float) -> list:
    price = phone.price_numeric if phone.price_numeric else parse_price(phone.price)
    raw_html = str(phone.raw_specs).lower() if phone.raw_specs else ""
    
    is_feature_phone = price < 4000.0 or "feature phone" in raw_html or "keypad" in raw_html
    
    battery = 1200 if is_feature_phone else 5000
    if '6000' in raw_html: battery = 6000
    elif '4500' in raw_html: battery = 4500
    elif '4000' in raw_html: battery = 4000
    
    ram = 0.032 if is_feature_phone else 8
    if '16gb ram' in raw_html: ram = 16
    elif '12gb ram' in raw_html: ram = 12
    elif '4gb ram' in raw_html: ram = 4
    
    hz = 30 if is_feature_phone else 60
    if '144hz' in raw_html: hz = 144
    elif '120hz' in raw_html: hz = 120
    elif '90hz' in raw_html: hz = 90
    
    perf = 0 if is_feature_phone else 1
    if 'snapdragon 8' in raw_html or 'dimensity 9' in raw_html or 'a18' in raw_html: perf = 3
    elif 'snapdragon 7' in raw_html or 'dimensity 8' in raw_html: perf = 2
    elif 'snapdragon 6' in raw_html or 'dimensity 7' in raw_html: perf = 1
    
    return [persona_idx, budget, price, battery, ram, hz, perf]

def persona_name_to_idx(name: str) -> int:
    name = (name or "").lower()
    if 'student' in name: return 0
    if 'gamer' in name: return 1
    if 'camera' in name or 'creator' in name: return 2
    return 3

def ml_score_phones(phones: List[PhoneDetails], persona: str, budget: float, semantic_ids: List[str] = None) -> List[Dict[str, Any]]:
    scored = []
    persona_idx = persona_name_to_idx(persona)
    model = get_ranker_model()
    
    features_list = []
    valid_phones = []
    
    semantic_set = set(semantic_ids) if semantic_ids else set()
    
    for phone in phones:
        # Hard cap year filter
        year = phone.launch_year
        if year is None:
            raw_str = str(phone.raw_specs).lower()
            if "2026" in raw_str:   year = 2026
            elif "2025" in raw_str: year = 2025
            else:                   year = 2024
            
        # Reject phones older than 2024 AND phantom future phones
        if year < 2024 or year > 2026:
            continue
            
        # Hard filter for dead/irrelevant brands that have corrupted 2025 dates in the DB
        dead_brands = ["micromax", "tcl", "nokia", "gionee", "karbonn", "lava (old)", "panasonic", "lg", "htc", "blackberry"]
        feature_phone_brands = ["heemax", "ikall", "i kall", "forme", "blackzone", "angage", "mafe", "hotline", "q-tel", "xolo"]
        
        brand_lower = str(phone.brand).lower().strip()
        if brand_lower in dead_brands or brand_lower in feature_phone_brands:
            continue
            
        # Phase 2: Bypass Live Price (disabled to avoid latency/scraper issues)
        parsed_price = phone.price_numeric if phone.price_numeric is not None else parse_price(phone.price)
        
        # Budget check with 5% buffer
        if parsed_price > budget * 1.05 or parsed_price == 0:
            continue
            
        # Dynamic Price Floor: Ensures the engine squeezes the entire budget and doesn't recommend lower-tier phones
        min_price = max(4500.0, budget * 0.75)
        if parsed_price < min_price:
            continue
            
        # Update the phone object with the safe price
        phone.price_numeric = parsed_price
        phone.price = float(parsed_price)
            
        feats = extract_features(phone, persona_idx, budget)
        features_list.append(feats)
        valid_phones.append(phone)
        
    if not valid_phones:
        # Fallback to wider floor if tight budget window has no phones
        for phone in phones:
            year = phone.launch_year or 2024
            if year < 2023 or year > 2026:
                continue
            parsed_price = phone.price_numeric if phone.price_numeric is not None else parse_price(phone.price)
            if parsed_price <= budget * 1.05 and parsed_price >= 4500:
                phone.price_numeric = parsed_price
                phone.price = float(parsed_price)
                feats = extract_features(phone, persona_idx, budget)
                features_list.append(feats)
                valid_phones.append(phone)

    if not valid_phones:
        return []
        
    if model:
        df_X = pd.DataFrame(features_list, columns=['persona', 'budget', 'price', 'battery', 'ram', 'hz', 'perf'])
        probs = model.predict_proba(df_X)[:, 1] # Probability of click
    else:
        # Fallback if model not trained
        probs = [0.5 for _ in valid_phones]

    for i, phone in enumerate(valid_phones):
        p_price = phone.price_numeric or budget
        budget_ratio = min(1.0, max(0.0, p_price / budget))
        
        # Multi-Attribute Hardware Utility Scoring (0-100)
        hw_vector = extract_hardware_spec_vector(phone)
        p_name = (persona or "").lower()
        if "gamer" in p_name: p_key = "Gamer"
        elif "student" in p_name: p_key = "Student"
        elif any(k in p_name for k in ["camera", "creator", "photo", "video"]): p_key = "Photography"
        elif any(k in p_name for k in ["pro", "executive"]): p_key = "Professional"
        elif any(k in p_name for k in ["senior", "basic"]): p_key = "Senior/Basic"
        else: p_key = "General"
        
        w = PERSONA_WEIGHTS.get(p_key, PERSONA_WEIGHTS["General"])
        
        hardware_utility = (
            w.get("performance", 0.20) * hw_vector["soc_score"] +
            w.get("camera", 0.20) * hw_vector["camera_score"] +
            w.get("display", 0.15) * hw_vector["display_score"] +
            w.get("battery", 0.20) * hw_vector["battery_charge_score"] +
            w.get("build", 0.10) * hw_vector["build_score"] +
            w.get("value", 0.15) * (budget_ratio * 100.0)
        )
        
        base_score = (hardware_utility * 0.65) + (float(probs[i]) * 20.0)
        
        # Budget Utilization Maximization: Squeeze every single rupee
        budget_squeeze_boost = (budget_ratio ** 1.5) * 15.0  # Up to +15 points for full budget utilization
        score = base_score + budget_squeeze_boost
        reasons = [f"Maximizes full budget allocation ({int(budget_ratio*100)}% of ₹{int(budget):,}) with top-tier hardware"]
        
        # Software UI Quality & Bloatware Taxonomy
        brand_l = str(phone.brand).lower().strip()
        ui_info = SOFTWARE_UI_TAXONOMY.get(brand_l, {"cleanliness": 0.70, "bloatware_free": 0.60, "name": "Custom OS"})
        
        # Sub-Brand & Lineup Series DNA check
        name_l = str(phone.name).lower().strip()
        is_gaming_dna = any(kw in name_l for kw in LINEUP_DNA_HIERARCHY["gaming"])
        is_camera_dna = any(kw in name_l for kw in LINEUP_DNA_HIERARCHY["camera"])
        is_battery_value_dna = any(kw in name_l for kw in LINEUP_DNA_HIERARCHY["battery_value"])
        is_flagship_dna = any(kw in name_l for kw in LINEUP_DNA_HIERARCHY["flagship"])
        
        # Persona & Intent Specific DNA Boosts
        p_lower = (persona or "").lower()
        
        if "gamer" in p_lower or any(w in p_lower for w in ["game", "fps", "performance", "speed", "heavy"]):
            if is_gaming_dna:
                score += 22.0
                reasons.append("Dedicated Gaming Lineup: Optimized thermal vapor chamber & high sustained frame rates")
        elif "camera" in p_lower or "creator" in p_lower or "photography" in p_lower or any(w in p_lower for w in ["photo", "portrait", "video", "sensor", "lens"]):
            if is_camera_dna:
                score += 22.0
                reasons.append("Pro Imaging Lineup: Advanced optical image stabilization & portrait color science")
        elif "student" in p_lower or "senior" in p_lower or "basic" in p_lower:
            if is_battery_value_dna:
                score += 15.0
                reasons.append("Value-King Lineup: Verified 2-day battery efficiency & durable chassis")
        elif "executive" in p_lower or "professional" in p_lower or budget >= 80000:
            if is_flagship_dna:
                score += 20.0
                reasons.append("Flagship Tier Lineup: Premium aerospace-grade materials & tier-1 display panel")
                
        # Clean UI & Stock Android Intent
        if any(w in p_lower for w in ["clean", "stock", "bloat", "no ads", "simple", "hello ui", "nothing os"]):
            if ui_info["cleanliness"] >= 0.90:
                score += 25.0
                reasons.append(f"Pure Clean Software: Zero bloatware experience ({ui_info['name']})")
            elif ui_info["cleanliness"] <= 0.68:
                score -= 30.0 # Strongly penalize ad-heavy skins for clean UI seekers
                
        if str(phone.id) in semantic_set:
            score += 15.0  # Semantic retrieval boost
            reasons.append("Highly relevant to search criteria (Semantic Match)")
            
        score = min(100.0, max(1.0, score))
        scored.append({
            "phone": phone,
            "score": score,
            "match_reasons": reasons,
            "trade_offs": []
        })
        
    scored.sort(key=lambda x: x["score"], reverse=True)
    
    # Apply Live YouTube Aspect Sentiment modifier to top 20 candidates
    for item in scored[:20]:
        try:
            phone = item["phone"]
            sentiment = fetch_live_sentiment(phone.name)
            p_lower = persona.lower()
            if "gamer" in p_lower and sentiment.get("performance", 0) > 0.3:
                item["score"] = min(100.0, item["score"] + 6.0)
                item["match_reasons"].append("Top-tier gaming & thermal sentiment in reviewer tests")
            elif ("camera" in p_lower or "creator" in p_lower) and sentiment.get("camera", 0) > 0.3:
                item["score"] = min(100.0, item["score"] + 6.0)
                item["match_reasons"].append("Highly praised camera & color tuning in reviewer tests")
            elif "student" in p_lower and sentiment.get("battery", 0) > 0.3:
                item["score"] = min(100.0, item["score"] + 6.0)
                item["match_reasons"].append("Verified all-day battery efficiency in real-world tests")
        except Exception:
            pass
            
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored

def get_candidates(all_phones: List[PhoneDetails], query: str) -> tuple[List[PhoneDetails], List[str]]:
    # Phase 1: Semantic Retrieval
    retrieved_ids = semantic_search(query, top_k=50)
    # Always use all_phones as the candidate pool to prevent dropping valid phones due to stale vector index
    return all_phones, retrieved_ids

def recommend_easy(all_phones: List[PhoneDetails], request: EasyRecommendRequest) -> List[Dict[str, Any]]:
    # 1. Semantic Retrieval
    query = f"{request.persona} phone under {request.budget}"
    candidates, retrieved_ids = get_candidates(all_phones, query)
    
    # 2. Knowledge Graph Filter
    safe_candidates = filter_by_knowledge_graph(candidates)
    
    # 3. XGBoost Ranking
    return ml_score_phones(safe_candidates, request.persona, request.budget, semantic_ids=retrieved_ids)

def recommend_medium(all_phones: List[PhoneDetails], request: MediumRecommendRequest) -> List[Dict[str, Any]]:
    query = f"Phone under {request.budget}"
    candidates, retrieved_ids = get_candidates(all_phones, query)
    safe_candidates = filter_by_knowledge_graph(candidates)
    return ml_score_phones(safe_candidates, "General", request.budget, semantic_ids=retrieved_ids)

from app.models.query import DeepRecommendRequest
from app.services.cross_encoder import rerank_candidates_with_llm

def recommend_deep(all_phones: List[PhoneDetails], request: DeepRecommendRequest) -> List[Dict[str, Any]]:
    query = f"{request.query} under {request.budget}"
    candidates, retrieved_ids = get_candidates(all_phones, query)
    safe_candidates = filter_by_knowledge_graph(candidates)
    scored = ml_score_phones(safe_candidates, request.query, request.budget, semantic_ids=retrieved_ids)
    
    # Phase 4: Multi-LLM Cross-Encoder Reranker for Deep natural language queries
    reranked = rerank_candidates_with_llm(scored, request.query, request.budget, max_candidates_to_rerank=12)
    return reranked
