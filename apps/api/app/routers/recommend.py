from fastapi import APIRouter
from app.models.query import EasyRecommendRequest, MediumRecommendRequest
from app.models.response import RecommendationResponse, RecommendedPhone
from app.services.recommender import recommend_easy, recommend_medium
from app.db.queries import get_all_phones

router = APIRouter()

@router.post("/easy", response_model=RecommendationResponse)
async def easy_recommendation(request: EasyRecommendRequest):
    all_phones = await get_all_phones(max_budget=request.budget, limit=1000)
    scored = recommend_easy(all_phones, request)
    
    recommendations = []
    for item in scored[:5]: # Top 5
        recommendations.append(RecommendedPhone(
            phone=item["phone"],
            score=item["score"],
            match_reasons=item["match_reasons"],
            trade_offs=item["trade_offs"]
        ))
        
    return RecommendationResponse(
        recommendations=recommendations,
        persona_detected=request.persona,
        budget_used=request.budget
    )

@router.post("/medium", response_model=RecommendationResponse)
async def medium_recommendation(request: MediumRecommendRequest):
    all_phones = await get_all_phones(max_budget=request.budget, limit=1000)
    scored = recommend_medium(all_phones, request)
    
    recommendations = []
    for item in scored[:5]:
        recommendations.append(RecommendedPhone(
            phone=item["phone"],
            score=item["score"],
            match_reasons=item["match_reasons"],
            trade_offs=item["trade_offs"]
        ))
        
    return RecommendationResponse(
        recommendations=recommendations,
        budget_used=request.budget
    )
