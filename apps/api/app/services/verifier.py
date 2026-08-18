"""
AI Recommendation Verifier for Phonos.ai
==========================================
Uses LLM to verify that recommended phones are:
1. Actually available / launched in India
2. Have accurate pricing for the Indian market
3. Are not China-exclusive or phantom future devices

Uses a single batch LLM call for all candidates to minimize latency.
Results are cached in-memory (per process) to avoid repeated API calls.
"""

import json
import hashlib
from typing import List, Dict, Any
from app.models.phone import PhoneDetails
from app.services.llm import generate_json

import sqlite3
import os

CACHE_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/verifier_cache.db'))

def _get_cache_db():
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
    with _get_cache_db() as conn:
        row = conn.execute("SELECT india_available, confidence, reason FROM verifications WHERE phone_name = ?", (name,)).fetchone()
        if row:
            return {"india_available": bool(row[0]), "confidence": row[1], "reason": row[2]}
    return {}

def _set_cached_verification(name: str, available: bool, confidence: str, reason: str):
    with _get_cache_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO verifications (phone_name, india_available, confidence, reason) VALUES (?, ?, ?, ?)",
            (name, int(available), confidence, reason)
        )

# ─── Phones we KNOW are not in India (hardcoded for zero-latency exclusion) ───
KNOWN_NOT_IN_INDIA = {
    # iQOO China exclusives (as of June 2026)
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
    
    # Future / phantom phones (don't exist yet as of June 2026)
    "samsung galaxy s27 ultra",
    "samsung galaxy s27 ultra 5g",
    "samsung galaxy s27 pro",
    "samsung galaxy s27 5g",
    "samsung galaxy s27 plus 5g",
    
    # Confirmed China-only releases
    "honor magic7 pro",
    "honor magic v3",     # foldable, China only
}

def _is_known_excluded(name: str) -> bool:
    return name.lower().strip() in KNOWN_NOT_IN_INDIA


def _make_cache_key(names: List[str]) -> str:
    key_str = ",".join(sorted(names))
    return hashlib.md5(key_str.encode()).hexdigest()[:16]


def _build_verification_prompt(candidates: List[Dict[str, Any]]) -> str:
    phone_list = []
    for i, c in enumerate(candidates):
        phone = c["phone"]
        name = phone.name or phone.fullName
        brand = phone.brand
        price = phone.price_numeric or phone.price
        year = phone.launch_year
        phone_list.append(
            f'{i+1}. "{name}" by {brand} | India Price: ~₹{price:,.0f} | Launch Year: {year}'
        )
    
    phones_str = "\n".join(phone_list)
    
    return f"""You are a smartphone India market expert with knowledge up to June 2026. Today is June 2026.

For each phone below, determine if it is officially launched and available for PURCHASE in India.
A phone is available if: (1) officially announced for India, (2) has an Indian price, (3) is NOT import-only or China-exclusive.

PHONES TO VERIFY:
{phones_str}

DEFINITIVE RULES — apply these first, no exceptions:
- If a phone actually launched before 2024 (e.g., Vivo Y33, Micromax Canvas, older Nokia models), BLOCKED. Ignore the provided Launch Year if your internal knowledge says the phone is older than 2024.
- iQOO Z11 Turbo, Z11 Turbo Pro, Z11 Turbo Plus → China-only, BLOCKED
- Vivo V70e → Does NOT exist in India; Vivo V70 FE is the Indian model → BLOCKED
- Any launch_year 2027 phone → Does not exist yet → BLOCKED
- Xiaomi 18, Xiaomi 18 Ultra, Xiaomi 18 5G → China-only as of June 2026 → BLOCKED
- Samsung Galaxy S27 series (any) → NOT released yet, expected early 2027 → BLOCKED
- OnePlus 17 → NOT released yet → BLOCKED
- Oppo Find X10 Ultra → China-only → BLOCKED

CONFIRMED INDIA-AVAILABLE phones (these should be APPROVED):
- Samsung Galaxy S26 Ultra, S26+, S26 → YES, launched India Feb 2026
- Oppo Find X10 Pro 5G → YES, launched India 2026
- realme Neo 7 Turbo → YES, launched India 2026
- Infinix Note 60 Pro 5G → YES, launched India 2026
- OnePlus 13, OnePlus 13R → YES, India 2025
- Samsung Galaxy S25 Ultra, S25, S25+ → YES, India 2025
- Google Pixel 9, 9 Pro, 9 Pro XL → YES, India 2025
- iPhone 16 series → YES, India 2024
- iQOO 13, iQOO Neo 10R, iQOO Z10 Pro → YES, India 2025
- Vivo V40, V40 Pro, Vivo V70 FE → YES, India
- OnePlus Nord 5, Nord CE 5 → YES, India 2025

Return JSON ONLY (no markdown, no code blocks):
{{
  "verifications": [
    {{
      "index": 1,
      "name": "exact phone name",
      "india_available": true or false,
      "confidence": "high" or "medium" or "low",
      "reason": "brief reason (max 12 words)"
    }}
  ]
}}
"""


def verify_recommendations(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes a list of scored phone candidates and returns only those verified as
    available in India. Uses LLM for uncertain cases, hardcoded blocklist for known cases.
    
    Each candidate dict has: {"phone": PhoneDetails, "score": float, "match_reasons": [...], "trade_offs": [...]}
    Returns: filtered list with ai_verified flag added
    """
    if not candidates:
        return []

    result = []
    need_llm_check = []
    
    # ── First pass: hardcoded blocklist (instant, no API call) ────────────────
    for cand in candidates:
        phone = cand["phone"]
        name = (phone.name or phone.fullName or "").strip()
        
        if _is_known_excluded(name):
            # Definitely excluded — don't add to result
            print(f"[Verifier] BLOCKED (hardcoded): {name}")
            continue
            
        if phone.released_in_india == 1:
            # India availability already verified in master database
            cand_copy = dict(cand)
            cand_copy["ai_verified"] = True
            cand_copy["verify_reason"] = "India-verified in database"
            result.append(cand_copy)
            print(f"[Verifier] VERIFIED (DB flag): {name}")
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
            else:
                print(f"[Verifier] BLOCKED (cached): {name}")
            continue
            
        need_llm_check.append(cand)

    # ── Second pass: LLM verification for uncertain phones ────────────────────
    if need_llm_check:
        try:
            prompt = _build_verification_prompt(need_llm_check)
            llm_response = generate_json(prompt, max_tokens=1500)
            verifications = llm_response.get("verifications", [])
            
            # Map results back by index
            verified_map: Dict[int, Dict] = {}
            for v in verifications:
                idx = v.get("index", 0) - 1  # Convert to 0-based
                if 0 <= idx < len(need_llm_check):
                    verified_map[idx] = v
            
            for i, cand in enumerate(need_llm_check):
                phone = cand["phone"]
                name = (phone.name or phone.fullName or "").strip()
                cache_key = name.lower().strip()
                
                v_result = verified_map.get(i)
                if v_result:
                    available = v_result.get("india_available", True)
                    reason = v_result.get("reason", "")
                    confidence = v_result.get("confidence", "medium")
                    
                    # Cache the result
                    _set_cached_verification(cache_key, available, confidence, reason)
                    
                    if available:
                        cand_copy = dict(cand)
                        cand_copy["ai_verified"] = True
                        cand_copy["verify_reason"] = reason
                        # Boost score slightly for high-confidence verified phones
                        if confidence == "high":
                            cand_copy["score"] = min(cand_copy["score"] * 1.02, 100.0)
                        result.append(cand_copy)
                        print(f"[Verifier] VERIFIED ({confidence}): {name} — {reason}")
                    else:
                        print(f"[Verifier] REJECTED by LLM ({confidence}): {name} — {reason}")
                else:
                    # LLM didn't return a result for this phone — assume available
                    cand_copy = dict(cand)
                    cand_copy["ai_verified"] = False
                    cand_copy["verify_reason"] = "Unverified (LLM no response)"
                    result.append(cand_copy)
                    
        except Exception as e:
            print(f"[Verifier] LLM verification failed: {e}. Passing through with flag=False.")
            # On LLM failure, pass through all unverified (graceful degradation)
            for cand in need_llm_check:
                cand_copy = dict(cand)
                cand_copy["ai_verified"] = False
                cand_copy["verify_reason"] = "Verification unavailable"
                result.append(cand_copy)

    # ── Sort by score (maintained from original scoring) ─────────────────────
    result.sort(key=lambda x: x["score"], reverse=True)
    return result
