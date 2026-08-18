import sys
import os
import asyncio
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import get_db_pool, close_db_pool
from app.db.queries import get_all_phones
from app.services.recommender import recommend_easy, recommend_medium, recommend_deep
from app.models.query import EasyRecommendRequest, MediumRecommendRequest, DeepRecommendRequest

async def run_live_recommendation_tests():
    print("================================================================================")
    print("                 PHONOS.AI RECOMMENDATION ENGINE LIVE TEST                      ")
    print("================================================================================")

    # 1. Load active phones from curated database
    all_phones = await get_all_phones(limit=2000)
    print(f"Loaded {len(all_phones)} active Indian smartphones from DB into candidate pool.\n")

    test_scenarios = [
        {
            "title": "Scenario 1: Budget Student Smartphone",
            "type": "easy",
            "req": EasyRecommendRequest(persona="Student", budget=20000),
            "description": "Persona: Student | Budget: ₹20,000 | Priority: Battery efficiency, value for money"
        },
        {
            "title": "Scenario 2: Mid-Range Performance & Gaming",
            "type": "easy",
            "req": EasyRecommendRequest(persona="Gamer", budget=35000),
            "description": "Persona: Gamer | Budget: ₹35,000 | Priority: High refresh rate, chipset performance, cooling"
        },
        {
            "title": "Scenario 3: Camera & Creator Enthusiast",
            "type": "easy",
            "req": EasyRecommendRequest(persona="Camera Enthusiast", budget=55000),
            "description": "Persona: Camera | Budget: ₹55,000 | Priority: Primary OIS camera, telephoto, image processing"
        },
        {
            "title": "Scenario 4: Ultra-Premium Flagship",
            "type": "easy",
            "req": EasyRecommendRequest(persona="Executive / Flagship", budget=120000),
            "description": "Persona: Executive | Budget: ₹1,20,000 | Priority: Flagship build, maximum performance & display"
        },
        {
            "title": "Scenario 5: Deep Mode Natural Language Query",
            "type": "deep",
            "req": DeepRecommendRequest(query="Clean stock Android UI with great battery life and 120Hz display", budget=40000),
            "description": "NL Prompt: 'Clean stock Android UI with great battery life and 120Hz display' | Budget: ₹40,000"
        }
    ]

    for sc in test_scenarios:
        print("--------------------------------------------------------------------------------")
        print(f"🎯 {sc['title']}")
        print(f"   {sc['description']}")
        print("--------------------------------------------------------------------------------")
        
        # Load budget-filtered candidates from database matching API router behavior
        all_phones = await get_all_phones(max_budget=sc['req'].budget, limit=1000)
        
        if sc['type'] == 'easy':
            results = recommend_easy(all_phones, sc['req'])
        elif sc['type'] == 'medium':
            results = recommend_medium(all_phones, sc['req'])
        else:
            results = recommend_deep(all_phones, sc['req'])

        from app.routers.recommend import _enforce_brand_diversity
        top_picks = _enforce_brand_diversity(results)[:3]
        if not top_picks:
            print("   ⚠️ No recommendations returned!")
        else:
            for idx, item in enumerate(top_picks, start=1):
                p = item['phone']
                score = round(item['score'], 1)
                price_fmt = f"₹{int(p.price_numeric):,}" if p.price_numeric else str(p.price)
                reasons = " | ".join(item.get('match_reasons', []))
                print(f"   🏆 Top #{idx}: {p.name} ({p.brand})")
                print(f"      • Price: {price_fmt} | Year: {int(p.launch_year) if p.launch_year else 'N/A'} | AI Match Score: {score}%")
                print(f"      • Key Reasons: {reasons}")
        print()

    await close_db_pool()

if __name__ == "__main__":
    asyncio.run(run_live_recommendation_tests())
