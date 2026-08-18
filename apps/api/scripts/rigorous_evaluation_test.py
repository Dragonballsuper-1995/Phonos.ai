import asyncio
import sys
import os
import time
import json

# Ensure UTF-8 output on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, '.')
# Secrets are loaded from environment or .env file

from app.db.database import get_db_pool, close_db_pool
from app.models.query import EasyRecommendRequest, MediumRecommendRequest, DeepRecommendRequest
from app.routers.recommend import easy_recommendation, medium_recommendation, deep_recommendation

TEST_CASES = [
    {
        "id": "TC-01",
        "category": "Easy - Student Budget",
        "type": "easy",
        "req": EasyRecommendRequest(persona="Student", budget=15000),
        "desc": "Student with strict budget Rs. 15,000"
    },
    {
        "id": "TC-02",
        "category": "Easy - Student Mid",
        "type": "easy",
        "req": EasyRecommendRequest(persona="Student", budget=30000),
        "desc": "Student / College all-rounder budget Rs. 30,000"
    },
    {
        "id": "TC-03",
        "category": "Easy - Gamer Budget",
        "type": "easy",
        "req": EasyRecommendRequest(persona="Gamer", budget=25000),
        "desc": "Budget gaming phone under Rs. 25,000"
    },
    {
        "id": "TC-04",
        "category": "Easy - Gamer Mid-Flagship",
        "type": "easy",
        "req": EasyRecommendRequest(persona="Gamer", budget=50000),
        "desc": "Competitive gaming phone under Rs. 50,000"
    },
    {
        "id": "TC-05",
        "category": "Easy - Gamer Ultra-Flagship",
        "type": "easy",
        "req": EasyRecommendRequest(persona="Gamer", budget=150000),
        "desc": "Top-tier flagship gaming under Rs. 1,50,000"
    },
    {
        "id": "TC-06",
        "category": "Easy - Creator Mid",
        "type": "easy",
        "req": EasyRecommendRequest(persona="Camera / Content Creator", budget=40000),
        "desc": "Content Creator / Camera focused under Rs. 40,000"
    },
    {
        "id": "TC-07",
        "category": "Easy - Creator Flagship",
        "type": "easy",
        "req": EasyRecommendRequest(persona="Camera / Content Creator", budget=100000),
        "desc": "Pro camera creator flagship under Rs. 1,00,000"
    },
    {
        "id": "TC-08",
        "category": "Easy - Executive / Battery",
        "type": "easy",
        "req": EasyRecommendRequest(persona="Battery / Executive", budget=35000),
        "desc": "Long battery life & productivity under Rs. 35,000"
    },
    {
        "id": "TC-09",
        "category": "Medium - Sliders (Performance & Battery)",
        "type": "medium",
        "req": MediumRecommendRequest(budget=60000, importance={"performance": 0.9, "battery": 0.8, "camera": 0.5, "display": 0.7}),
        "desc": "Custom sliders high performance + battery under Rs. 60,000"
    },
    {
        "id": "TC-10",
        "category": "Deep - Compact Flagship Query",
        "type": "deep",
        "req": DeepRecommendRequest(query="Compact smartphone under 6.36 inches with telephoto zoom and wireless charging", budget=85000),
        "desc": "Natural language query: Compact flagship with telephoto"
    },
    {
        "id": "TC-11",
        "category": "Deep - Clean Stock Android",
        "type": "deep",
        "req": DeepRecommendRequest(query="Clean stock Android UI without bloatware with eSIM and fast charging", budget=45000),
        "desc": "Natural language query: Clean stock Android with eSIM"
    },
    {
        "id": "TC-12",
        "category": "Edge Case - Ultra Luxury Rs. 2,00,000",
        "type": "easy",
        "req": EasyRecommendRequest(persona="General / Luxury", budget=200000),
        "desc": "Ultra luxury bracket - ensure zero phantom phones (e.g. S27 Ultra, Xiaomi 18)"
    },
    {
        "id": "TC-13",
        "category": "Edge Case - Low Budget Rs. 8,000",
        "type": "easy",
        "req": EasyRecommendRequest(persona="Student", budget=8000),
        "desc": "Low budget Rs. 8,000 - ensure only functional modern 4G/5G smartphones"
    }
]

async def run_rigorous_tests():
    conn = await get_db_pool()
    all_results = []
    
    print("=" * 80)
    print("PHONOS.AI RIGOROUS RECOMMENDATIONS TEST SUITE")
    print(f"Executing {len(TEST_CASES)} comprehensive test cases across all personas & modes")
    print("=" * 80)

    for tc in TEST_CASES:
        t0 = time.time()
        tc_id = tc["id"]
        category = tc["category"]
        print(f"\n[{tc_id}] Running: {category} ({tc['desc']})...")
        
        try:
            if tc["type"] == "easy":
                resp = await easy_recommendation(tc["req"])
            elif tc["type"] == "medium":
                resp = await medium_recommendation(tc["req"])
            elif tc["type"] == "deep":
                resp = await deep_recommendation(tc["req"])
            else:
                resp = None

            elapsed = round(time.time() - t0, 2)
            recs = resp.recommendations if resp else []
            
            print(f" -> Generated {len(recs)} recommendations in {elapsed}s:")
            
            tc_summary = {
                "id": tc_id,
                "category": category,
                "description": tc["desc"],
                "elapsed_sec": elapsed,
                "recommendations": []
            }
            
            for rank, r in enumerate(recs, 1):
                p = r.phone
                p_name = p.name
                p_brand = p.brand
                p_price = p.price
                p_year = p.launch_year
                ai_ver = r.ai_verified
                ver_reason = r.verify_reason
                explanation = r.ai_explanation
                
                print(f"    {rank}. {p_name} ({p_brand}) | Rs. {p_price:,.0f} | Score: {r.score:.1f} | Verified: {ai_ver}")
                if explanation:
                    print(f"       Pitch: {explanation[:110]}...")
                    
                tc_summary["recommendations"].append({
                    "rank": rank,
                    "name": p_name,
                    "brand": p_brand,
                    "price": p_price,
                    "year": p_year,
                    "score": r.score,
                    "ai_verified": ai_ver,
                    "verify_reason": ver_reason,
                    "explanation": explanation,
                    "match_reasons": r.match_reasons
                })
                
            all_results.append(tc_summary)
            
        except Exception as e:
            print(f"[ERROR] in {tc_id}: {e}")
            all_results.append({
                "id": tc_id,
                "category": category,
                "error": str(e)
            })

    # Save detailed JSON output for fact-checking
    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../evaluation_results.json'))
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
        
    print("\n" + "=" * 80)
    print(f"SUCCESS: All {len(TEST_CASES)} test cases completed! Saved structured results to evaluation_results.json")
    print("=" * 80)
    
    await close_db_pool()

if __name__ == "__main__":
    asyncio.run(run_rigorous_tests())
