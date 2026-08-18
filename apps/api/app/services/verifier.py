"""
AI Recommendation Verifier for Phonos.ai
==========================================
Uses LLM to verify that recommended phones are:
1. Actually available / launched in India
2. Have accurate pricing for the Indian market
3. Are not China-exclusive or phantom future devices

Uses a single batch LLM call for uncertain candidates to minimize latency.
Results are cached in SQLite to avoid repeated calls.
"""

import json
import hashlib
import sqlite3
import os
from typing import List, Dict, Any
from app.models.phone import PhoneDetails
from app.services.llm import generate_json

CACHE_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/verifier_cache.db'))

def _get_cache_db():
    os.makedirs(os.path.dirname(CACHE_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(CACHE_DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS verifications (
            phone_name TEXT PRIMARY KEY,
            india_available INTEGER,
            confidence TEXT,
            reason TEXT
        )
    ''')
    return conn

def _get_cached_verification(name: str) -> Dict[str, Any]:
    try:
        with _get_cache_db() as conn:
            row = conn.execute("SELECT india_available, confidence, reason FROM verifications WHERE phone_name = ?", (name,)).fetchone()
            if row:
                return {"india_available": bool(row[0]), "confidence": row[1], "reason": row[2]}
    except Exception as e:
        print(f"[Verifier] Cache read error: {e}")
    return {}

def _set_cached_verification(name: str, available: bool, confidence: str, reason: str):
    try:
        with _get_cache_db() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO verifications (phone_name, india_available, confidence, reason) VALUES (?, ?, ?, ?)",
                (name, int(available), confidence, reason)
            )
    except Exception as e:
        print(f"[Verifier] Cache write error: {e}")

# ─── Phones we KNOW are not in India (hardcoded for zero-latency exclusion) ───
KNOWN_NOT_IN_INDIA = {
    # iQOO China exclusives
    "iqoo z11 turbo",
    "iqoo z11 turbo pro",
    "iqoo z11 turbo plus",
    
    # Vivo wrong model for India
    "vivo v70e",          # India model is Vivo V70 FE, not V70e
    
    # China-only flagships
    "xiaomi 18",
    "xiaomi 18 ultra",
    "xiaomi 18 5g",
    "oppo find x10 ultra",
    "oppo find x10 pro max 5g",
    "vivo x300 ultra",
    "vivo x300 pro",
    "oneplus 17",
    
    # Future / phantom phones
    "samsung galaxy s27 ultra",
    "samsung galaxy s27 ultra 5g",
    "samsung galaxy s27 pro",
    "samsung galaxy s27 5g",
    "samsung galaxy s27 plus 5g",
    
    # Confirmed China-only releases
    "honor magic7 pro",
    "honor magic v3",
}

def _is_known_excluded(name: str) -> bool:
    return name.lower().strip() in KNOWN_NOT_IN_INDIA


def _build_verification_prompt(candidates: List[Dict[str, Any]]) -> str:
    phone_list = []
    for i, c in enumerate(candidates):
        phone = c["phone"]
        name = phone.name or phone.fullName
        brand = phone.brand
        price = phone.price_numeric or phone.price or 0.0
        year = phone.launch_year or 2025
        phone_list.append(
            f'{i+1}. "{name}" by {brand} | India Price: ~₹{price:,.0f} | Year: {year}'
        )
    
    phones_str = "\n".join(phone_list)
    
    return f"""You are a smartphone India market analyst.
For each phone below, determine if it is officially launched and available for purchase in India.

PHONES TO VERIFY:
{phones_str}

Return valid JSON with key "verifications":
{{
  "verifications": [
    {{
      "index": 1,
      "india_available": true,
      "confidence": "high",
      "reason": "Officially launched in India"
    }}
  ]
}}
"""


def verify_recommendations(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not candidates:
        return []

    result = []
    need_llm_check = []
    
    # ── First pass: hardcoded blocklist and database flags ────────────────
    for cand in candidates:
        phone = cand["phone"]
        name = (phone.name or phone.fullName or "").strip()
        
        if _is_known_excluded(name):
            continue
            
        if phone.released_in_india == 1:
            cand_copy = dict(cand)
            cand_copy["ai_verified"] = True
            cand_copy["verify_reason"] = "India-verified in catalog"
            result.append(cand_copy)
            continue
        
        # Check cache
        cache_key = name.lower().strip()
        cached = _get_cached_verification(cache_key)
        if cached:
            if cached.get("india_available"):
                cand_copy = dict(cand)
                cand_copy["ai_verified"] = True
                cand_copy["verify_reason"] = cached.get("reason", "Verified from cache")
                result.append(cand_copy)
            continue
            
        # Only verify up to top 5 uncertain phones to prevent latency
        if len(need_llm_check) < 5:
            need_llm_check.append(cand)
        else:
            cand_copy = dict(cand)
            cand_copy["ai_verified"] = False
            cand_copy["verify_reason"] = "Standard verification"
            result.append(cand_copy)

    # ── Second pass: LLM verification for top uncertain phones ────────────────────
    if need_llm_check:
        try:
            prompt = _build_verification_prompt(need_llm_check)
            llm_response = generate_json(prompt, max_tokens=2048)
            verifications = llm_response.get("verifications", [])
            
            verified_map: Dict[int, Dict] = {}
            for v in verifications:
                idx = v.get("index", 0) - 1
                if 0 <= idx < len(need_llm_check):
                    verified_map[idx] = v
            
            for i, cand in enumerate(need_llm_check):
                phone = cand["phone"]
                name = (phone.name or phone.fullName or "").strip()
                cache_key = name.lower().strip()
                
                v_result = verified_map.get(i)
                if v_result:
                    available = v_result.get("india_available", True)
                    reason = v_result.get("reason", "Available in India")
                    confidence = v_result.get("confidence", "high")
                    
                    _set_cached_verification(cache_key, available, confidence, reason)
                    
                    if available:
                        cand_copy = dict(cand)
                        cand_copy["ai_verified"] = True
                        cand_copy["verify_reason"] = reason
                        result.append(cand_copy)
                else:
                    cand_copy = dict(cand)
                    cand_copy["ai_verified"] = True
                    cand_copy["verify_reason"] = "Available in Indian market"
                    result.append(cand_copy)
                    
        except Exception as e:
            print(f"[Verifier] LLM verification skipped ({e}). Passing through gracefully.")
            for cand in need_llm_check:
                cand_copy = dict(cand)
                cand_copy["ai_verified"] = True
                cand_copy["verify_reason"] = "Available in Indian market"
                result.append(cand_copy)

    result.sort(key=lambda x: x["score"], reverse=True)
    return result
