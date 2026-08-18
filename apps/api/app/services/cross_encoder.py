"""
Multi-LLM Cross-Encoder Reranker for Phonos.ai Deep Mode
==========================================================
Uses Groq (sub-200ms) / Gemini 2.5 Flash / Nvidia NIM as a reasoning judge to rerank
candidate phones on nuanced, subjective, and complex natural language requirements.
"""

import json
from typing import List, Dict, Any
from app.models.phone import PhoneDetails
from app.services.llm import generate_json
from app.core.constants import SOFTWARE_UI_TAXONOMY

def rerank_candidates_with_llm(
    candidates: List[Dict[str, Any]],
    user_query: str,
    budget: float,
    max_candidates_to_rerank: int = 12
) -> List[Dict[str, Any]]:
    """
    Reranks candidate phones using LLM cross-encoder reasoning.
    Falls back gracefully to existing heuristic rank if LLM fails.
    """
    if not candidates:
        return []

    top_pool = candidates[:max_candidates_to_rerank]
    
    # Prepare concise phone specs summary for LLM prompt
    phone_summaries = []
    for idx, item in enumerate(top_pool, 1):
        p: PhoneDetails = item["phone"]
        brand_l = str(p.brand).lower().strip()
        ui_name = SOFTWARE_UI_TAXONOMY.get(brand_l, {}).get("name", "Custom UI")
        price_str = f"₹{int(p.price_numeric):,}" if p.price_numeric else str(p.price)
        
        phone_summaries.append({
            "candidate_id": idx,
            "name": p.name,
            "brand": p.brand,
            "price": price_str,
            "year": int(p.launch_year) if p.launch_year else 2024,
            "software_ui": ui_name,
            "raw_specs": str(p.raw_specs or "")[:350]
        })

    prompt = f"""
You are the Chief Smartphone Expert and Recommendation Judge for Phonos.ai.
The user is looking for a smartphone in India with the following exact requirements:

USER QUERY: "{user_query}"
MAX BUDGET: ₹{int(budget):,}

Here are {len(phone_summaries)} pre-filtered candidate smartphones available in India:
{json.dumps(phone_summaries, indent=2)}

TASK:
1. Deeply analyze how well each phone satisfies the user's explicit and implicit needs in the query (e.g. clean OS, compact size, gaming FPS, telephoto lens, battery endurance, fast charging, display quality).
2. Rank the top candidates from best to worst fit.
3. Provide an AI Match Score (0 to 100) for each phone.
4. Provide 1 compelling reason why this phone fits the user's specific query.
5. Provide 1 honest trade-off / drawback the user should know.

Return ONLY a valid JSON object matching this structure:
{{
  "rankings": [
    {{
      "candidate_id": 1,
      "score": 96.0,
      "match_reason": "Specific reason why it fits the query",
      "trade_off": "Key limitation or drawback"
    }}
  ]
}}
"""

    try:
        response = generate_json(prompt, max_tokens=1500)
        rankings = response.get("rankings", [])
        
        if not rankings:
            return candidates

        # Map reranked scores back to original objects
        reranked = []
        id_to_item = {idx: item for idx, item in enumerate(top_pool, 1)}
        seen_ids = set()

        for rank_info in rankings:
            c_id = rank_info.get("candidate_id")
            if c_id in id_to_item and c_id not in seen_ids:
                item = id_to_item[c_id]
                score = float(rank_info.get("score", item["score"]))
                match_reason = rank_info.get("match_reason")
                trade_off = rank_info.get("trade_off")
                
                # Combine match reasons
                combined_reasons = []
                if match_reason:
                    combined_reasons.append(match_reason)
                combined_reasons.extend(item.get("match_reasons", []))
                
                trade_offs = []
                if trade_off:
                    trade_offs.append(trade_off)
                trade_offs.extend(item.get("trade_offs", []))

                reranked.append({
                    "phone": item["phone"],
                    "score": score,
                    "match_reasons": combined_reasons,
                    "trade_offs": trade_offs,
                    "ai_verified": True
                })
                seen_ids.add(c_id)

        # Append any items not returned in the LLM response
        for idx, item in enumerate(top_pool, 1):
            if idx not in seen_ids:
                reranked.append(item)

        # Append remaining candidates beyond max_candidates_to_rerank
        reranked.extend(candidates[max_candidates_to_rerank:])
        
        reranked.sort(key=lambda x: x["score"], reverse=True)
        return reranked

    except Exception as e:
        print(f"[CrossEncoder] LLM Reranking fallback due to: {e}")
        # Fallback cleanly to heuristic MAUT scoring
        return candidates
