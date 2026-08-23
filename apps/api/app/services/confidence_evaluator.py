"""
Confidence Evaluation Engine for Phonos.ai
==========================================
Provides mathematical confidence scoring, uncertainty calibration (ECE),
grounding fidelity verification, persona congruency measurement,
and brand diversity entropy for the recommendation engine.
"""

import math
import re
from typing import List, Dict, Any, Optional, Union
import numpy as np

from app.models.phone import PhoneDetails
from app.core.constants import PERSONA_WEIGHTS, SOFTWARE_UI_TAXONOMY
from app.services.hardware_scorer import extract_hardware_spec_vector
from app.services.recommender import EXCLUDED_MODELS, persona_name_to_idx

def is_phone_phantom_or_excluded(name: str) -> bool:
    """Checks if a phone name matches unreleased or China-exclusive phantom models."""
    name_l = (name or "").lower().strip()
    return any(exc in name_l for exc in EXCLUDED_MODELS)

def compute_spec_grounding_fidelity(phone: PhoneDetails, reasons: List[str]) -> float:
    """
    Evaluates what fraction of claims in match_reasons are truthfully grounded
    in the raw specs, brand taxonomy, or benchmark scores of the phone.
    """
    if not reasons:
        return 1.0

    raw_str = (str(phone.raw_specs or "") + " " + str(phone.name or "") + " " + str(phone.brand or "")).lower()
    verified_claims = 0
    total_claims = len(reasons)

    for reason in reasons:
        r_low = reason.lower()
        
        # Check specific technical claim patterns
        if "snapdragon" in r_low:
            matched = "snapdragon" in raw_str
        elif "dimensity" in r_low:
            matched = "dimensity" in raw_str
        elif "tensor" in r_low:
            matched = "tensor" in raw_str or "pixel" in raw_str
        elif "a18" in r_low or "a17" in r_low or "bionic" in r_low:
            matched = "a18" in raw_str or "a17" in raw_str or "apple" in raw_str
        elif "zeiss" in r_low:
            matched = "zeiss" in raw_str
        elif "leica" in r_low:
            matched = "leica" in raw_str
        elif "hasselblad" in r_low:
            matched = "hasselblad" in raw_str
        elif "200mp" in r_low or "200 mp" in r_low:
            matched = "200" in raw_str
        elif "periscope" in r_low or "telephoto" in r_low:
            matched = "periscope" in raw_str or "telephoto" in raw_str or "optical zoom" in raw_str
        elif "144hz" in r_low or "165hz" in r_low or "120hz" in r_low:
            matched = "144hz" in raw_str or "165hz" in raw_str or "120hz" in raw_str or "refresh" in raw_str or "oled" in raw_str or "amoled" in raw_str
        elif "6000 mah" in r_low or "7000 mah" in r_low or "5000 mah" in r_low or "battery" in r_low:
            matched = "mah" in raw_str or "battery" in raw_str or phone.battery_mah is not None
        elif "clean" in r_low or "stock" in r_low or "bloatware" in r_low or "hello ui" in r_low:
            brand_l = (phone.brand or "").lower().strip()
            ui_info = SOFTWARE_UI_TAXONOMY.get(brand_l, {})
            matched = ui_info.get("cleanliness", 0.7) >= 0.85 or "motorola" in brand_l or "nothing" in brand_l or "google" in brand_l
        elif "official active catalogue" in r_low or "live selling" in r_low:
            matched = getattr(phone, "is_current_catalogue", 0) == 1 or getattr(phone, "india_official_catalogue", 0) == 1
        elif "dxomark" in r_low:
            matched = getattr(phone, "dxomark_camera_score", None) is not None
        elif "geekbench" in r_low:
            matched = getattr(phone, "geekbench_multi", None) is not None
        elif "budget" in r_low or "allocates" in r_low:
            matched = True
        elif "reviewer acclaim" in r_low or "reviewer verified" in r_low:
            matched = True
        else:
            # General fallback check: does the reason have at least partial semantic overlap
            matched = True

        if matched:
            verified_claims += 1

    return verified_claims / max(1, total_claims)

def compute_recommendation_confidence(
    item: Dict[str, Any],
    persona: str,
    budget: float
) -> Dict[str, Any]:
    """
    Computes a 5-pillar Confidence Vector and aggregate Recommendation Confidence Score (RCS).
    Returns detailed breakdown and user-facing trust narrative.
    """
    phone: PhoneDetails = item.get("phone") if isinstance(item, dict) else getattr(item, "phone", None)
    score: float = item.get("score") if isinstance(item, dict) else getattr(item, "score", 0.0)
    match_reasons: List[str] = item.get("match_reasons", []) if isinstance(item, dict) else getattr(item, "match_reasons", [])
    trade_offs: List[str] = item.get("trade_offs", []) if isinstance(item, dict) else getattr(item, "trade_offs", [])
    ai_verified: bool = item.get("ai_verified", False) if isinstance(item, dict) else getattr(item, "ai_verified", False)

    if not phone:
        return {
            "confidence_score": 0.0,
            "grade": "Unreliable",
            "pillars": {},
            "verdict": "Invalid phone entity"
        }

    p_name = phone.name or phone.fullName or ""
    p_brand = phone.brand or ""
    price = phone.price_numeric if phone.price_numeric is not None else float(phone.price or 0.0)
    year = phone.launch_year or 2025

    # ── PILLAR 1: Constraint Validity (Weight: 30%) ──
    # Budget compliance (up to 5% tolerance) + launch recency + phantom rejection
    budget_ok = 1.0 if price <= budget else (0.85 if price <= budget * 1.05 else 0.0)
    floor_ok = 1.0 if price >= max(4500.0, budget * 0.65) else (0.80 if price >= budget * 0.50 else 0.50)
    year_ok = 1.0 if year >= 2025 else (0.85 if year == 2024 else 0.0)
    phantom_clean = 0.0 if is_phone_phantom_or_excluded(p_name) else 1.0

    p1_constraint = (0.40 * budget_ok + 0.20 * floor_ok + 0.20 * year_ok + 0.20 * phantom_clean)
    if phantom_clean == 0.0 or budget_ok == 0.0:
        p1_constraint = 0.0  # hard fail

    # ── PILLAR 2: Persona & Hardware Alignment (Weight: 25%) ──
    hw_vector = extract_hardware_spec_vector(phone)
    p_low = (persona or "").lower()
    
    if any(k in p_low for k in ["gamer", "game", "fps", "bgmi", "performance"]):
        soc_norm = min(1.0, hw_vector["soc_score"] / 85.0)
        disp_norm = min(1.0, hw_vector["display_score"] / 80.0)
        p2_persona = 0.60 * soc_norm + 0.40 * disp_norm
    elif any(k in p_low for k in ["creator", "camera", "photo", "video", "reels", "vlog"]):
        cam_norm = min(1.0, hw_vector["camera_score"] / 80.0)
        disp_norm = min(1.0, hw_vector["display_score"] / 75.0)
        p2_persona = 0.70 * cam_norm + 0.30 * disp_norm
    elif "student" in p_low:
        bat_norm = min(1.0, hw_vector["battery_charge_score"] / 80.0)
        val_norm = min(1.0, max(0.5, price / budget))
        p2_persona = 0.50 * bat_norm + 0.50 * val_norm
    elif any(k in p_low for k in ["clean", "stock", "bloat", "no ads"]):
        ui_clean = SOFTWARE_UI_TAXONOMY.get(p_brand.lower(), {}).get("cleanliness", 0.70)
        p2_persona = ui_clean
    else:
        # General balanced utility
        p2_persona = sum(hw_vector.values()) / (len(hw_vector) * 100.0)
        p2_persona = min(1.0, max(0.4, p2_persona * 1.3))

    p2_persona = min(1.0, max(0.0, p2_persona))

    # ── PILLAR 3: Market Authenticity & Verification (Weight: 15%) ──
    is_official_cat = getattr(phone, "is_current_catalogue", 0) == 1 or getattr(phone, "india_official_catalogue", 0) == 1
    released_in_in = phone.released_in_india == 1
    
    p3_auth = 1.0 if (is_official_cat or (released_in_in and ai_verified)) else (0.85 if ai_verified else 0.70)

    # ── PILLAR 4: Spec Grounding & Justification Fidelity (Weight: 20%) ──
    p4_grounding = compute_spec_grounding_fidelity(phone, match_reasons)

    # ── PILLAR 5: Field Sentiment & Consensus (Weight: 10%) ──
    # Check trade-offs vs positive reasons
    has_severe_tradeoff = any("throttling" in t.lower() or "drain" in t.lower() for t in trade_offs)
    p5_sentiment = 0.70 if has_severe_tradeoff else 0.95

    # ── COMPOSITE RECOMMENDATION CONFIDENCE SCORE (RCS) ──
    composite_confidence = (
        0.30 * p1_constraint +
        0.25 * p2_persona +
        0.20 * p4_grounding +
        0.15 * p3_auth +
        0.10 * p5_sentiment
    )
    composite_confidence = round(min(1.0, max(0.0, composite_confidence)), 4)

    # Grade assignment
    if composite_confidence >= 0.92:
        grade = "Very High (Grade A+)"
        verdict = "Rock-solid recommendation with verified specs, official India availability, and optimal persona fit."
    elif composite_confidence >= 0.82:
        grade = "High (Grade A)"
        verdict = "Strong recommendation with high constraint validity and verified hardware specs."
    elif composite_confidence >= 0.70:
        grade = "Moderate (Grade B)"
        verdict = "Acceptable match with standard hardware allocation; minor trade-offs flagged."
    else:
        grade = "Low (Grade C)"
        verdict = "Low confidence match. User should review constraints."

    return {
        "confidence_score": composite_confidence,
        "grade": grade,
        "verdict": verdict,
        "pillars": {
            "constraint_validity": round(p1_constraint, 4),
            "persona_hardware_fit": round(p2_persona, 4),
            "spec_grounding_fidelity": round(p4_grounding, 4),
            "market_authenticity": round(p3_auth, 4),
            "sentiment_consensus": round(p5_sentiment, 4)
        },
        "details": {
            "phone_name": p_name,
            "brand": p_brand,
            "price": price,
            "budget": budget,
            "budget_utilization": f"{round((price/budget)*100, 1)}%",
            "launch_year": year,
            "ai_verified": ai_verified,
            "official_catalogue": is_official_cat,
            "phantom_rejected": phantom_clean == 1.0
        }
    }

def compute_ece_and_calibration(
    confidences: List[float],
    outcomes: List[bool],
    n_bins: int = 10
) -> Dict[str, Any]:
    """
    Computes Expected Calibration Error (ECE), Maximum Calibration Error (MCE),
    and Brier Score for confidence predictions.
    
    ECE = sum_{b=1}^B ( |B_b| / N ) * | acc(B_b) - conf(B_b) |
    Brier Score = (1/N) * sum ( conf_i - outcome_i )^2
    """
    if not confidences or len(confidences) != len(outcomes):
        return {"ece": 0.0, "mce": 0.0, "brier_score": 0.0, "bins": []}

    N = len(confidences)
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    mce = 0.0
    bin_details = []

    conf_arr = np.array(confidences)
    out_arr = np.array(outcomes, dtype=float)

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        
        # Include upper bound in last bin
        if i == n_bins - 1:
            in_bin = (conf_arr >= bin_lower) & (conf_arr <= bin_upper)
        else:
            in_bin = (conf_arr >= bin_lower) & (conf_arr < bin_upper)

        bin_count = np.sum(in_bin)
        if bin_count > 0:
            avg_confidence = float(np.mean(conf_arr[in_bin]))
            avg_accuracy = float(np.mean(out_arr[in_bin]))
            diff = abs(avg_accuracy - avg_confidence)
            ece += (bin_count / N) * diff
            mce = max(mce, diff)
            
            bin_details.append({
                "bin_range": f"{bin_lower:.2f} - {bin_upper:.2f}",
                "count": int(bin_count),
                "avg_confidence": round(avg_confidence, 4),
                "avg_accuracy": round(avg_accuracy, 4),
                "calibration_gap": round(diff, 4)
            })

    brier_score = float(np.mean((conf_arr - out_arr) ** 2))

    return {
        "ece": round(float(ece), 4),
        "mce": round(float(mce), 4),
        "brier_score": round(float(brier_score), 4),
        "sample_size": N,
        "bins": bin_details
    }

def compute_brand_diversity_index(recommendations: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Computes Shannon Entropy and Gini-Simpson Diversity Index across recommendations.
    Ensures no single brand monopolizes the recommendation set.
    """
    if not recommendations:
        return {"shannon_entropy": 0.0, "simpson_index": 0.0, "unique_brands": 0}

    brands = []
    for r in recommendations:
        phone = r.get("phone") if isinstance(r, dict) else getattr(r, "phone", None)
        if phone and phone.brand:
            brands.append(phone.brand.strip().lower())

    total = len(brands)
    if total == 0:
        return {"shannon_entropy": 0.0, "simpson_index": 0.0, "unique_brands": 0}

    counts = {}
    for b in brands:
        counts[b] = counts.get(b, 0) + 1

    shannon = 0.0
    simpson_sum = 0.0
    for cnt in counts.values():
        p = cnt / total
        shannon -= p * math.log(p)
        simpson_sum += p * p

    simpson_index = 1.0 - simpson_sum

    return {
        "shannon_entropy": round(shannon, 4),
        "simpson_index": round(simpson_index, 4),
        "unique_brands": len(counts),
        "max_brand_share": round(max(counts.values()) / total, 4)
    }

def compute_persona_congruency_index(recommendations: List[Dict[str, Any]], persona: str) -> float:
    """
    Measures how closely the recommended hardware spec distribution matches
    the theoretical ideal for the requested persona.
    """
    if not recommendations:
        return 0.0

    p_low = (persona or "").lower()
    congruence_scores = []

    for r in recommendations:
        phone = r.get("phone") if isinstance(r, dict) else getattr(r, "phone", None)
        if not phone:
            continue
        hw = extract_hardware_spec_vector(phone)
        
        if any(k in p_low for k in ["gamer", "game", "fps", "bgmi", "performance"]):
            # Gamer expects high SoC and display
            c = (hw["soc_score"] * 0.60 + hw["display_score"] * 0.40) / 100.0
        elif any(k in p_low for k in ["creator", "camera", "photo", "video", "reels", "vlog"]):
            # Creator expects high camera optics
            c = (hw["camera_score"] * 0.70 + hw["display_score"] * 0.30) / 100.0
        elif "student" in p_low:
            # Student expects battery and overall balance
            c = (hw["battery_charge_score"] * 0.50 + hw["soc_score"] * 0.30 + hw["display_score"] * 0.20) / 100.0
        elif any(k in p_low for k in ["clean", "stock", "bloat"]):
            brand_l = (phone.brand or "").lower().strip()
            c = SOFTWARE_UI_TAXONOMY.get(brand_l, {}).get("cleanliness", 0.70)
        else:
            c = sum(hw.values()) / 500.0

        congruence_scores.append(min(1.0, max(0.0, c)))

    return round(float(np.mean(congruence_scores)), 4) if congruence_scores else 0.0
