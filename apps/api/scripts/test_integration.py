"""Full integration test for the recommendation pipeline"""
import asyncio
import sys, os
sys.path.insert(0, '.')
# Secrets are loaded from environment or .env file

from app.db.database import get_db_pool, close_db_pool
from app.db.queries import get_all_phones
from app.services.recommender import recommend_easy
from app.models.query import EasyRecommendRequest
from app.services.verifier import verify_recommendations


async def test():
    conn = await get_db_pool()

    print("=== STUDENT Rs30,000 ===")
    phones = await get_all_phones(max_budget=30000, limit=1000)
    req = EasyRecommendRequest(persona="Student", budget=30000)
    scored = recommend_easy(phones, req)
    top15 = scored[:15]
    print(f"DB phones in budget: {len(phones)} | Top15: {len(top15)}")
    print("Top 5 BEFORE verification:")
    for i, s in enumerate(top15[:5]):
        p = s["phone"]
        print(f"  {i+1}. {p.name} ({p.brand}) Score={s['score']} Year={p.launch_year}")

    verified = verify_recommendations(top15)
    print(f"AFTER verification: {len(verified)}")
    for i, v in enumerate(verified[:5]):
        p = v["phone"]
        badge = "[AI VERIFIED]" if v.get("ai_verified") else "[UNVERIFIED]"
        print(f"  {i+1}. {badge} {p.name} Score={v['score']}")

    print()
    print("=== GAMER Rs1,50,000 ===")
    phones2 = await get_all_phones(max_budget=150000, limit=1000)
    req2 = EasyRecommendRequest(persona="Gamer", budget=150000)
    scored2 = recommend_easy(phones2, req2)
    top15_2 = scored2[:15]
    print(f"DB phones in budget: {len(phones2)} | Top15: {len(top15_2)}")
    print("Top 5 BEFORE verification:")
    for i, s in enumerate(top15_2[:5]):
        p = s["phone"]
        print(f"  {i+1}. {p.name} ({p.brand}) Score={s['score']} Year={p.launch_year}")

    verified2 = verify_recommendations(top15_2)
    print(f"AFTER verification: {len(verified2)}")
    for i, v in enumerate(verified2[:5]):
        p = v["phone"]
        badge = "[AI VERIFIED]" if v.get("ai_verified") else "[UNVERIFIED]"
        print(f"  {i+1}. {badge} {p.name} Score={v['score']}")

    await close_db_pool()


asyncio.run(test())
