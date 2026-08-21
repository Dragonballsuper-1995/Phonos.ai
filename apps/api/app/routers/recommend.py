"""
Recommendation Router — Phonos.ai
===================================
Wires scoring → AI verification → top-5 response.
Flow: DB query → score_phones (top 15) → verify_recommendations → return top 5
"""

import asyncio
from typing import List, Dict, Optional, Any
from fastapi import APIRouter
from app.models.query import EasyRecommendRequest, MediumRecommendRequest
from app.models.response import RecommendationResponse, RecommendedPhone
from app.services.recommender import recommend_easy, recommend_medium
from app.services.verifier import verify_recommendations
from app.db.queries import get_all_phones

from app.services.llm import generate_explanations
from app.services.live_pricing import get_live_pricing_details

router = APIRouter()

import re
def _enforce_brand_diversity(verified: list) -> list:
    """Ensure at most 2 phones from the same brand in the top 5, and deduplicate RAM/ROM variants."""
    diverse = []
    brand_counts = {}
    seen_bases = set()
    
    for item in verified:
        p_name = item["phone"].name.strip().lower()
        base_name = re.sub(r'\s*\(\s*\d+\s*gb.*?\)', '', p_name).strip()
        brand = item["phone"].brand.strip()
        
        if base_name in seen_bases:
            continue
            
        if brand_counts.get(brand, 0) < 2:
            diverse.append(item)
            brand_counts[brand] = brand_counts.get(brand, 0) + 1
            seen_bases.add(base_name)
            
        if len(diverse) == 5:
            break
            
    return diverse

async def _build_response_with_explanations(verified: list, persona: str, budget: float) -> RecommendationResponse:
    # 1. Select top 5 with Brand Diversity (Max 2 per brand) & Live Pricing check
    top5 = []
    brand_counts = {}
    seen_bases = set()
    
    for item in verified:
        p_name = item["phone"].name.strip().lower()
        base_name = re.sub(r'\s*\(\s*\d+\s*gb.*?\)', '', p_name).strip()
        brand = item["phone"].brand.strip()
        
        if base_name in seen_bases:
            continue
            
        # Resolve Live Pricing Details before adding
        phone_name = item["phone"].name
        pricing = get_live_pricing_details(item["phone"].slug or phone_name, phone_name, default_price=item["phone"].price or 0.0)
        new_price = pricing.get("price")
        if new_price and new_price > 0:
            if new_price > budget * 1.05:
                continue
            item["phone"].price = new_price
            item["phone"].price_numeric = new_price
            
        if brand_counts.get(brand, 0) < 2:
            top5.append(item)
            brand_counts[brand] = brand_counts.get(brand, 0) + 1
            seen_bases.add(base_name)
            
        if len(top5) == 5:
            break
            
    # 2. Generate LLM Explanations for the top 5
    loop = asyncio.get_event_loop()
    explanations = await loop.run_in_executor(
        None, generate_explanations, top5, persona, budget
    )
    
    recommendations = []
    for item in top5:
        phone_name = item["phone"].name
        brand = item["phone"].brand
        
        # Try to find the matching explanation
        ai_exp = None
        for k, v in explanations.items():
            if phone_name.lower() in k.lower() or k.lower() in phone_name.lower() or brand.lower() in k.lower():
                ai_exp = v
                break
                
        rec = RecommendedPhone(
            phone=item["phone"],
            score=item["score"],
            match_reasons=item.get("match_reasons", []),
            trade_offs=item.get("trade_offs", []),
            ai_verified=item.get("ai_verified", False),
            verify_reason=item.get("verify_reason"),
            ai_explanation=ai_exp
        )
        recommendations.append(rec)
        
    return RecommendationResponse(
        recommendations=recommendations,
        persona_detected=persona,
        budget_used=budget,
    )

@router.post("/easy", response_model=RecommendationResponse)
async def easy_recommendation(request: EasyRecommendRequest):
    all_phones = await get_all_phones(max_budget=request.budget, limit=1000)
    scored = recommend_easy(all_phones, request)
    top_candidates = scored[:15]

    loop = asyncio.get_event_loop()
    verified = await loop.run_in_executor(
        None, verify_recommendations, top_candidates
    )

    return await _build_response_with_explanations(verified, request.persona, request.budget)

@router.post("/medium", response_model=RecommendationResponse)
async def medium_recommendation(request: MediumRecommendRequest):
    all_phones = await get_all_phones(max_budget=request.budget, limit=1000)
    scored = recommend_medium(all_phones, request)
    top_candidates = scored[:15]

    loop = asyncio.get_event_loop()
    verified = await loop.run_in_executor(
        None, verify_recommendations, top_candidates
    )

    return await _build_response_with_explanations(verified, "General/Enthusiast", request.budget)

from app.models.query import DeepRecommendRequest
from app.services.recommender import recommend_deep
from fastapi.responses import StreamingResponse
from app.services.llm import stream_deep_reasoning, generate_clarification_questions
import json

@router.post("/deep", response_model=RecommendationResponse)
async def deep_recommendation(request: DeepRecommendRequest):
    all_phones = await get_all_phones(max_budget=request.budget, limit=1000)
    scored = recommend_deep(all_phones, request)
    top_candidates = scored[:15]

    loop = asyncio.get_event_loop()
    verified = await loop.run_in_executor(
        None, verify_recommendations, top_candidates
    )

    # Use the freeform query as the persona context for the LLM Pitch
    return await _build_response_with_explanations(verified, f"Custom query: {request.query}", request.budget)


@router.post("/deep-stream")
async def deep_stream_recommendation(request: DeepRecommendRequest):
    """
    Real-time SSE Streaming Copilot for Deep Mode with multi-turn clarification questions.
    """
    async def event_generator():
        # 1. Emit Initial Analyzing Status
        yield f"event: status\ndata: {json.dumps({'step': 'analyzing', 'message': 'Analyzing hardware constraints and query intent...'})}\n\n"
        await asyncio.sleep(0.05)

        # 2. Database Retrieval & Hybrid Benchmark Scoring
        yield f"event: status\ndata: {json.dumps({'step': 'searching', 'message': 'Scanning catalog with DxOMark, Geekbench & battery lab benchmarks...'})}\n\n"
        all_phones = await get_all_phones(max_budget=request.budget, limit=1000)
        scored = recommend_deep(all_phones, request)
        top_candidates = scored[:15]

        loop = asyncio.get_event_loop()
        verified = await loop.run_in_executor(
            None, verify_recommendations, top_candidates
        )

        # Apply Brand Diversity & Live Pricing
        top5 = []
        brand_counts = {}
        seen_bases = set()
        for item in verified:
            p_name = item["phone"].name.strip().lower()
            base_name = re.sub(r'\s*\(\s*\d+\s*gb.*?\)', '', p_name).strip()
            brand = item["phone"].brand.strip()
            if base_name in seen_bases:
                continue
            phone_name = item["phone"].name
            pricing = get_live_pricing_details(item["phone"].slug or phone_name, phone_name, default_price=item["phone"].price or 0.0)
            new_price = pricing.get("price")
            if new_price and new_price > 0:
                if new_price > request.budget * 1.05:
                    continue
                item["phone"].price = new_price
                item["phone"].price_numeric = new_price
            if brand_counts.get(brand, 0) < 2:
                top5.append(item)
                brand_counts[brand] = brand_counts.get(brand, 0) + 1
                seen_bases.add(base_name)
            if len(top5) == 5:
                break

        # 3. Stream Reasoning Breakdown
        yield f"event: status\ndata: {json.dumps({'step': 'reasoning', 'message': 'Synthesizing expert architectural breakdown...'})}\n\n"
        async for token in stream_deep_reasoning(request.query, top5, request.budget):
            yield f"event: token\ndata: {json.dumps({'token': token})}\n\n"

        # 4. Generate & Emit Clarification Questions
        questions = generate_clarification_questions(request.query, request.budget)
        yield f"event: questions\ndata: {json.dumps({'questions': questions})}\n\n"

        # 5. Format and Emit Final Recommendations
        recommendations = []
        for item in top5:
            rec = {
                "phone": item["phone"].model_dump() if hasattr(item["phone"], "model_dump") else item["phone"].dict(),
                "score": item["score"],
                "match_reasons": item.get("match_reasons", []),
                "trade_offs": item.get("trade_offs", []),
                "ai_verified": item.get("ai_verified", False),
                "verify_reason": item.get("verify_reason"),
            }
            recommendations.append(rec)

        yield f"event: recommendations\ndata: {json.dumps({'recommendations': recommendations})}\n\n"
        yield f"event: done\ndata: {json.dumps({'status': 'complete'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


from pydantic import BaseModel
from scripts.retrain_rlhf_worker import log_feedback_event, retrain_ranker
import asyncio

class FeedbackRequest(BaseModel):
    phone_id: Optional[int] = None
    phone_name: str
    persona: str = "general"
    budget: float = 50000.0
    event_type: str
    weight: float = 1.0


@router.post("/feedback")
async def record_feedback(payload: FeedbackRequest):
    """
    Records a user interaction event to the RLHF feedback store.
    """
    log_feedback_event(
        phone_id=payload.phone_id or 0,
        phone_name=payload.phone_name,
        persona=payload.persona,
        budget=payload.budget,
        event_type=payload.event_type,
        weight=payload.weight,
    )
    return {"status": "recorded", "event": payload.event_type, "phone": payload.phone_name}


@router.post("/retrain")
async def trigger_retrain(dry_run: bool = False, samples: int = 15000):
    """
    Triggers continuous RLHF retraining of the XGBoost DLRM ranker.
    """
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, retrain_ranker, dry_run, samples)
    return results

