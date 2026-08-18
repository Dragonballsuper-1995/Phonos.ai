import asyncio
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.queries import get_all_phones
from app.models.query import EasyRecommendRequest
from app.services.recommender import recommend_easy
from app.routers.recommend import _enforce_brand_diversity, _build_response_with_explanations
from app.db.database import close_db_pool

async def debug_student_40k():
    req = EasyRecommendRequest(persona='student', budget=40000)
    all_phones = await get_all_phones(max_budget=req.budget, limit=1000)
    print(f"Total phones found <= 40000: {len(all_phones)}")
    scored = recommend_easy(all_phones, req)
    top15 = scored[:15]
    print("\n--- Raw Top 15 Scored (Before Live Pricing) ---")
    for i, s in enumerate(top15, 1):
        p = s['phone']
        print(f"{i}. {p.name} ({p.brand}) - DB Price: ₹{p.price_numeric} | Score: {round(s['score'], 1)}")
    
    resp = await _build_response_with_explanations(top15, req.persona, req.budget)
    print("\n--- Final Built Response (After Live Pricing & Diversity) ---")
    for i, r in enumerate(resp.recommendations, 1):
        p = r.phone
        print(f"{i}. {p.name} ({p.brand}) - Final Price: ₹{p.price_numeric} | Score: {round(r.score, 1)}")
    
    await close_db_pool()

if __name__ == "__main__":
    asyncio.run(debug_student_40k())
