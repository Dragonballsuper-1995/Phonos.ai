import sys
import os
import asyncio
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.queries import get_all_phones
from app.db.database import close_db_pool
from app.services.recommender import recommend_deep
from app.models.query import DeepRecommendRequest
from app.routers.recommend import _enforce_brand_diversity

async def test_deep_cross_encoder_prompts():
    print("================================================================================", flush=True)
    print("       TESTING MULTI-LLM CROSS-ENCODER RERANKER (DEEP MODE PROMPTS)             ", flush=True)
    print("================================================================================", flush=True)

    test_queries = [
        {
            "title": "Prompt 1: Clean Stock UI & Haptics",
            "query": "I want a clean stock Android UI with zero bloatware, great haptics, 120Hz display, and long battery life",
            "budget": 40000
        },
        {
            "title": "Prompt 2: Hardcore Gaming & Thermals",
            "query": "Need a heavy gaming phone with high sustained FPS, vapor chamber cooling, and ultra-fast charging",
            "budget": 35000
        },
        {
            "title": "Prompt 3: Periscope Telephoto & Portrait Camera",
            "query": "Looking for the best camera phone with dedicated optical telephoto zoom, OIS, and realistic skin tone color tuning",
            "budget": 60000
        },
        {
            "title": "Prompt 4: Premium Titanium Flagship",
            "query": "Ultimate flagship smartphone with premium titanium frame, tier-1 display, and top-tier performance",
            "budget": 125000
        }
    ]

    for t in test_queries:
        print("--------------------------------------------------------------------------------", flush=True)
        print(f"🎯 {t['title']}", flush=True)
        print(f"   Query:  \"{t['query']}\"", flush=True)
        print(f"   Budget: ₹{t['budget']:,}", flush=True)
        print("--------------------------------------------------------------------------------", flush=True)

        all_phones = await get_all_phones(max_budget=t['budget'], limit=1000)
        req = DeepRecommendRequest(query=t['query'], budget=t['budget'])
        
        # Runs through Semantic Search -> Hardware Scorer -> DNA -> LLM Cross-Encoder
        results = recommend_deep(all_phones, req)
        top3 = _enforce_brand_diversity(results)[:3]

        if not top3:
            print("   ⚠️ No recommendations returned!", flush=True)
        else:
            for idx, item in enumerate(top3, 1):
                p = item["phone"]
                score = round(item["score"], 1)
                price_fmt = f"₹{int(p.price_numeric):,}" if p.price_numeric else str(p.price)
                reasons = item.get("match_reasons", [])
                primary_reason = reasons[0] if reasons else "Top overall fit"
                trade_offs = item.get("trade_offs", [])
                primary_drawback = trade_offs[0] if trade_offs else "None reported"

                print(f"   🏆 #{idx}: {p.name} ({p.brand})", flush=True)
                print(f"      • Price: {price_fmt} | Year: {int(p.launch_year) if p.launch_year else 'N/A'} | AI Match Score: {score}%", flush=True)
                print(f"      • Why Picked: {primary_reason}", flush=True)
                print(f"      • Trade-Off:  {primary_drawback}", flush=True)
        print(flush=True)

    await close_db_pool()

if __name__ == "__main__":
    asyncio.run(test_deep_cross_encoder_prompts())
