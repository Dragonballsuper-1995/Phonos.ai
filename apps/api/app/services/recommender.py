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
from app.services.hardware_similarity import find_similar_phones, build_persona_query_vector

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
            print(f"[Ranker] Warning: Model not found at {MODEL_PATH}.")
    return _ranker_model

def parse_price(price_str) -> float:
    if not price_str:
        return 0.0
    numbers = re.findall(r'\d+', str(price_str).replace(',', ''))
    return float(numbers[0]) if numbers else 0.0

MAX_PRICE_NORM = 200000  # must match train_ranker.py

FEATURE_COLS = [
    'persona',
    'budget_ratio',
    'price_ratio',
    'battery_norm',
    'ram_norm',
    'hz_norm',
    'perf_tier',
]

def extract_features(phone: PhoneDetails, persona_idx: int, budget: float) -> list:
    """
    Canonical 7-feature vector for XGBoost inference.
    Schema, normalisation constants, and column order MUST match train_ranker.py.
    """
    price = phone.price_numeric if phone.price_numeric is not None else parse_price(phone.price)
    raw_html = str(phone.raw_specs).lower() if phone.raw_specs else ""
    
    battery = 5000
    if '7300' in raw_html or '7000' in raw_html: battery = 7000
    elif '6500' in raw_html or '6000' in raw_html: battery = 6000
    elif '5500' in raw_html: battery = 5500
    elif '4500' in raw_html: battery = 4500
    elif '4000' in raw_html: battery = 4000
    
    ram = 8
    if '24gb ram' in raw_html: ram = 24
    elif '16gb ram' in raw_html: ram = 16
    elif '12gb ram' in raw_html: ram = 12
    elif '4gb ram'  in raw_html: ram = 4
    
    hz = 60
    if '165hz' in raw_html: hz = 165
    elif '144hz' in raw_html: hz = 144
    elif '120hz' in raw_html: hz = 120
    elif '90hz'  in raw_html: hz = 90
    
    perf = 0.25
    if any(k in raw_html for k in ['snapdragon 8 elite', 'dimensity 9400', 'a18 pro', 'a18']): perf = 1.0
    elif any(k in raw_html for k in ['snapdragon 8 gen 3', 'dimensity 9300', 'a17 pro', 'a17']): perf = 0.75
    elif any(k in raw_html for k in ['snapdragon 7', 'dimensity 8']): perf = 0.5
    elif any(k in raw_html for k in ['snapdragon 6', 'dimensity 7']): perf = 0.25
    else: perf = 0.1
    
    budget_ratio = min(1.05, price / budget) if budget > 0 else 0.5
    price_ratio = min(1.0, price / MAX_PRICE_NORM)
    battery_norm = min(1.0, battery / 7000)
    ram_norm = min(1.0, ram / 24)
    hz_norm = min(1.0, hz / 165)
    
    return [float(persona_idx), budget_ratio, price_ratio, battery_norm, ram_norm, hz_norm, perf]

def persona_name_to_idx(name: str) -> int:
    name = (name or "").lower()
    if 'student' in name: return 0
    if 'gamer' in name: return 1
    if any(k in name for k in ['camera', 'creator', 'photo', 'video', 'reels', 'vlog']): return 2
    if any(k in name for k in ['pro', 'business', 'executive', 'work']): return 3
    return 4

# Strict list of China-exclusive or unreleased phantom models to exclude from Indian recommendations
EXCLUDED_MODELS = {
    "oppo find x8 ultra",
    "oppo find x7 ultra",
    "oppo find x6 pro",
    "oppo find x10 ultra",
    "vivo x200 plus",
    "vivo x200 ultra",
    "vivo x100 ultra",
    "vivo x300 ultra",
    "vivo x300 max",
    "vivo x500 ultra",
    "vivo v70e",
    "xiaomi 14 pro",
    "xiaomi 18",
    "xiaomi 18 ultra",
    "xiaomi 18 pro",
    "xiaomi 18 pro max",
    "xiaomi 17 max",
    "xiaomi 16 pro",
    "xiaomi 16",
    "iqoo z11 turbo",
    "iqoo z11 turbo pro",
    "iqoo z11 turbo plus",
    "samsung galaxy s27 ultra",
    "samsung galaxy s27",
    "oneplus 16",
    "oneplus 17",
    "motorola signature",
    "motorola razr 2026",
    "nothing phone 4",
    "honor magic 8 pro",
}

def ml_score_phones(
    phones: List[PhoneDetails],
    persona: str,
    budget: float,
    semantic_ids: List[str] = None,
    weight_overrides: Dict[str, float] = None
) -> List[Dict[str, Any]]:
    scored = []
    persona_idx = persona_name_to_idx(persona)
    model = get_ranker_model()
    
    features_list = []
    valid_phones = []
    semantic_set = set(semantic_ids) if semantic_ids else set()
    
    for phone in phones:
        name_lower = str(phone.name or phone.fullName or "").lower().strip()
        brand_lower = str(phone.brand or "").lower().strip()
        
        # 1. Strict Exclusion of China-only & Phantom models
        if any(exc in name_lower for exc in EXCLUDED_MODELS):
            continue
            
        # Hard filter for dead/corrupted brands
        dead_brands = ["micromax", "tcl", "nokia", "gionee", "karbonn", "panasonic", "lg", "htc", "blackberry", "heemax", "ikall", "i kall", "forme", "blackzone"]
        if brand_lower in dead_brands:
            continue
            
        # 2. Launch Year evaluation (2026 context)
        year = phone.launch_year
        if year is None:
            raw_str = str(phone.raw_specs).lower()
            if "2026" in raw_str:   year = 2026
            elif "2025" in raw_str: year = 2025
            else:                   year = 2024
            
        # Exclude older than 2024 and far-future (>2026)
        if year < 2024 or year > 2026:
            continue
            
        # 3. Budget Filter with 5% tolerance buffer
        parsed_price = phone.price_numeric if phone.price_numeric is not None else parse_price(phone.price)
        if parsed_price > budget * 1.05 or parsed_price <= 0:
            continue
            
        # Dynamic Price Floor to ensure budget maximization
        min_price = max(4500.0, budget * 0.65)
        if parsed_price < min_price:
            continue
            
        phone.price_numeric = parsed_price
        phone.price = float(parsed_price)
        
        feats = extract_features(phone, persona_idx, budget)
        features_list.append(feats)
        valid_phones.append(phone)
        
    if not valid_phones:
        # Fallback to wider floor if tight window is empty
        for phone in phones:
            name_lower = str(phone.name or phone.fullName or "").lower().strip()
            if any(exc in name_lower for exc in EXCLUDED_MODELS):
                continue
            year = phone.launch_year or 2024
            if year < 2024 or year > 2026:
                continue
            parsed_price = phone.price_numeric if phone.price_numeric is not None else parse_price(phone.price)
            if 4500 <= parsed_price <= budget * 1.05:
                phone.price_numeric = parsed_price
                phone.price = float(parsed_price)
                feats = extract_features(phone, persona_idx, budget)
                features_list.append(feats)
                valid_phones.append(phone)

    if not valid_phones:
        return []
        
    if model:
        df_X = pd.DataFrame(features_list, columns=FEATURE_COLS)
        probs = model.predict_proba(df_X)[:, 1]
    else:
        probs = [0.5 for _ in valid_phones]

    p_lower = (persona or "").lower()
    is_creator = any(k in p_lower for k in ["creator", "camera", "photo", "video", "reels", "vlog"])
    is_gamer = any(k in p_lower for k in ["gamer", "game", "gaming", "fps", "bgmi", "performance"])
    is_student = "student" in p_lower

    for i, phone in enumerate(valid_phones):
        p_price = phone.price_numeric or budget
        budget_ratio = min(1.0, max(0.0, p_price / budget))
        name_l = str(phone.name or phone.fullName or "").lower().strip()
        raw_l = str(phone.raw_specs or "").lower()
        year = phone.launch_year or 2025
        
        # Multi-Attribute Hardware Utility with Gated ABSA Sentiment Modulation (Pattern 2)
        hw_vector = extract_hardware_spec_vector(phone)
        sentiment = fetch_live_sentiment(phone.name)

        effective_soc = min(100.0, max(0.0, hw_vector["soc_score"] * (1.0 + 0.10 * sentiment.get("performance", 0.0))))
        effective_cam = min(100.0, max(0.0, hw_vector["camera_score"] * (1.0 + 0.10 * sentiment.get("camera", 0.0))))
        effective_disp = min(100.0, max(0.0, hw_vector["display_score"] * (1.0 + 0.10 * sentiment.get("display", 0.0))))
        effective_bat = min(100.0, max(0.0, hw_vector["battery_charge_score"] * (1.0 + 0.10 * sentiment.get("battery", 0.0))))
        effective_build = min(100.0, max(0.0, hw_vector["build_score"] * (1.0 + 0.10 * sentiment.get("build", 0.0))))
        
        if is_gamer: p_key = "Gamer"
        elif is_student: p_key = "Student"
        elif is_creator: p_key = "Photography"
        elif any(k in p_lower for k in ["pro", "executive", "work"]): p_key = "Professional"
        else: p_key = "General"
        
        if weight_overrides and sum(weight_overrides.values()) > 0:
            total_w = sum(weight_overrides.values())
            w = {k: v / total_w for k, v in weight_overrides.items()}
        else:
            w = PERSONA_WEIGHTS.get(p_key, PERSONA_WEIGHTS["General"])
        
        hardware_utility = (
            w.get("performance", 0.20) * effective_soc +
            w.get("camera", 0.20) * effective_cam +
            w.get("display", 0.15) * effective_disp +
            w.get("battery", 0.20) * effective_bat +
            w.get("build", 0.10) * effective_build +
            w.get("value", 0.15) * (budget_ratio * 100.0)
        )
        
        base_score = (hardware_utility * 0.60) + (float(probs[i]) * 15.0)
        budget_squeeze_boost = (budget_ratio ** 1.3) * 12.0
        
        # Accumulate additive keyword bonuses and penalties separately
        raw_bonus = 0.0
        penalty = 0.0
        
        reasons = [f"Allocates {int(budget_ratio*100)}% of ₹{int(budget):,} budget with tier-1 specifications"]
        trade_offs = []
        
        # ── 4. RECENCY & GENERATION RELEVANCE IN 2026 ────────────────────────
        if getattr(phone, "is_current_catalogue", 0) == 1 or getattr(phone, "india_official_catalogue", 0) == 1:
            raw_bonus += 10.0
            reasons.append("Official Active Catalogue: Confirmed live selling generation from brand's official India portal")

        if year >= 2026:
            raw_bonus += 10.0
            reasons.append("Current 2026 Generation: Latest silicon & longest OS software support cycle")
        elif year == 2025:
            raw_bonus += 5.0
            reasons.append("Modern 2025 Generation: Proven flagship performance & stability")
        elif year <= 2024:
            if p_price > 70000:
                penalty += 12.0
                trade_offs.append("2024 Hardware Generation: Excellent optics but nearing mid-lifecycle at current price point")


        # ── 5. CREATOR / VIDEO WORKFLOW SPECIALIZATION ────────────────────────
        if is_creator:
            if "200 mp" in raw_l and "zeiss" in raw_l:
                raw_bonus += 18.0
                reasons.append("ZEISS APO 200MP Telephoto: Flagship portrait clarity & telephoto macro video")
            elif "zeiss" in raw_l or "hasselblad" in raw_l or "leica" in raw_l:
                raw_bonus += 12.0
                reasons.append("Pro Co-Engineered Optics: Cinematic color science & lens coating")
                
            if "dolby vision" in raw_l or "4k@120fps" in raw_l or "log video" in raw_l:
                raw_bonus += 14.0
                reasons.append("Pro Video Pipeline: 4K Dolby Vision / 10-bit Log recording for color grading")
                
            if "center stage" in raw_l or "4k front" in raw_l or "32 mp front" in raw_l:
                raw_bonus += 8.0
                reasons.append("Ultra-Clear Front Camera: Optimized for Reels, vlogs, and front-facing video")
                
            if "flip" in name_l or "razr" in name_l or "fold" in name_l:
                penalty += 6.0
                reasons.append("Hands-Free Flex Cam: Tripod-free vlogging from external display")
                trade_offs.append("Foldable Form Factor: Slightly smaller thermal envelope for sustained 4K video recording")

        # ── 6. GAMING WORKFLOW SPECIALIZATION ──────────────────────────────────
        elif is_gamer:
            if any(kw in name_l for kw in LINEUP_DNA_HIERARCHY["gaming"]) or "snapdragon 8 elite" in raw_l or "dimensity 9400" in raw_l:
                raw_bonus += 16.0
                reasons.append("Dedicated Gaming Silicon: High sustained framerates & vapor chamber cooling")
            if "144hz" in raw_l or "165hz" in raw_l:
                raw_bonus += 8.0
                reasons.append("Ultra-High Refresh Panel: Ultra-low touch latency for competitive gaming")

        # ── 7. STUDENT / BATTERY SPECIALIZATION ───────────────────────────────
        elif is_student:
            if "6000 mah" in raw_l or "7000 mah" in raw_l or "7300 mah" in raw_l:
                raw_bonus += 15.0
                reasons.append("Massive Battery Reserve: Multi-day stamina for lectures, socials, and travel")
            if "120w" in raw_l or "100w" in raw_l or "80w" in raw_l:
                raw_bonus += 8.0
                reasons.append("Flash Charge Tech: 0 to 100% in under 30 minutes")

        # ── 8. SOFTWARE UI CLEANLINESS & INTENT BOOST ──────────────────────────
        brand_l = str(phone.brand).lower().strip()
        ui_info = SOFTWARE_UI_TAXONOMY.get(brand_l, {"cleanliness": 0.70, "bloatware_free": 0.60, "name": "Custom OS"})
        
        if any(w in p_lower for w in ["clean", "stock", "bloat", "no ads", "simple", "hello ui", "nothing os"]):
            if ui_info["cleanliness"] >= 0.90:
                raw_bonus += 25.0
                reasons.append(f"Pure Clean Software: Zero bloatware experience ({ui_info['name']})")
            elif ui_info["cleanliness"] <= 0.68:
                penalty += 30.0
                trade_offs.append(f"Ad-Supported Interface: Skin includes promotional recommendations in {ui_info['name']}")
        else:
            if ui_info["cleanliness"] >= 0.90:
                reasons.append(f"Clean Software Experience: Ad-free {ui_info['name']} interface")
            elif ui_info["cleanliness"] <= 0.65:
                trade_offs.append(f"Pre-installed Apps: May require initial decluttering in {ui_info['name']}")

        # ── 9. REVIEWER SENTIMENT HIGHLIGHTS (ABSA) ───────────────────────────
        if sentiment.get("camera", 0) > 0.25:
            reasons.append("Reviewer Acclaim: Top-tier photo and video dynamic range confirmed in field tests")
        elif sentiment.get("camera", 0) < -0.20:
            trade_offs.append("Reviewer Caution: Low-light optic softness or aggressive post-processing flagged in tests")

        if sentiment.get("performance", 0) > 0.25:
            reasons.append("Reviewer Verified: Exceptional sustained framerate stability & thermal control")
        elif sentiment.get("performance", 0) < -0.20:
            trade_offs.append("Reviewer Caution: Heavy thermal throttling reported during extended gaming sessions")

        if sentiment.get("battery", 0) > 0.25:
            reasons.append("Reviewer Verified: Praised all-day screen-on time in real-world endurance tests")
        elif sentiment.get("battery", 0) < -0.20:
            trade_offs.append("Reviewer Caution: Faster-than-expected standby battery drain noted in user testing")

        if str(phone.id) in semantic_set:
            raw_bonus += 10.0

        # Cap the positive additive bonuses at 25.0 max
        bonus_score = min(25.0, raw_bonus) - penalty
        score = base_score + budget_squeeze_boost + bonus_score
        score = min(99.0, max(50.0, score))
        scored.append({
            "phone": phone,
            "score": score,
            "match_reasons": reasons,
            "trade_offs": trade_offs or ["Premium tier flagship with no critical hardware compromises flagged."]
        })
        
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored

def get_candidates(all_phones: List[PhoneDetails], query: str) -> tuple[List[PhoneDetails], List[str]]:
    retrieved_ids = semantic_search(query, top_k=50)
    return all_phones, retrieved_ids

def persona_to_weights_key(persona: str) -> str:
    n = (persona or "").lower()
    if 'student' in n: return 'Student'
    if 'gamer' in n or 'gaming' in n or 'fps' in n: return 'Gamer'
    if any(k in n for k in ['camera', 'creator', 'photo', 'video', 'reels', 'vlog', 'optics']): return 'Photography'
    if any(k in n for k in ['pro', 'executive', 'work', 'business']): return 'Professional'
    if 'senior' in n or 'basic' in n: return 'Senior/Basic'
    return 'General'

def recommend_easy(all_phones: List[PhoneDetails], request: EasyRecommendRequest) -> List[Dict[str, Any]]:
    query = f"{request.persona} phone under {request.budget}"
    candidates, retrieved_ids = get_candidates(all_phones, query)
    safe_candidates = filter_by_knowledge_graph(candidates)

    # ── Persona-weighted hardware similarity augmentation ─────────────────────
    try:
        p_key = persona_to_weights_key(request.persona)
        weights = PERSONA_WEIGHTS.get(p_key, PERSONA_WEIGHTS["General"])
        hw_vec = build_persona_query_vector(weights)
        hw_hits = find_similar_phones(hw_vec, top_k=30, max_budget=request.budget)
        hw_ids = {str(h["id"]) for h in hw_hits}
    except Exception:
        hw_ids = set()

    all_retrieved = list(set(retrieved_ids) | hw_ids)
    return ml_score_phones(safe_candidates, request.persona, request.budget, semantic_ids=all_retrieved)

def recommend_medium(all_phones: List[PhoneDetails], request: MediumRecommendRequest) -> List[Dict[str, Any]]:
    query = f"Phone under {request.budget}"
    candidates, retrieved_ids = get_candidates(all_phones, query)
    safe_candidates = filter_by_knowledge_graph(candidates)

    weights = request.priorities or PERSONA_WEIGHTS["General"]
    try:
        hw_vec = build_persona_query_vector(weights)
        hw_hits = find_similar_phones(hw_vec, top_k=30, max_budget=request.budget)
        hw_ids = {str(h["id"]) for h in hw_hits}
    except Exception:
        hw_ids = set()

    all_retrieved = list(set(retrieved_ids) | hw_ids)
    return ml_score_phones(
        safe_candidates,
        "General",
        request.budget,
        semantic_ids=all_retrieved,
        weight_overrides=request.priorities or None
    )

from app.models.query import DeepRecommendRequest
from app.services.cross_encoder import rerank_candidates_with_llm

def recommend_deep(all_phones: List[PhoneDetails], request: DeepRecommendRequest) -> List[Dict[str, Any]]:
    query = f"{request.query} under {request.budget}"
    candidates, retrieved_ids = get_candidates(all_phones, query)
    safe_candidates = filter_by_knowledge_graph(candidates)
    scored = ml_score_phones(safe_candidates, request.query, request.budget, semantic_ids=retrieved_ids)
    reranked = rerank_candidates_with_llm(scored, request.query, request.budget, max_candidates_to_rerank=12)
    return reranked
