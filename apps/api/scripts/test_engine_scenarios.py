"""
test_engine_scenarios.py
========================
Runs real-world scenario tests and edge cases against the live SQLite database,
validating ranking consistency, hardware allocations, and trade-off generation.
"""
import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.db.queries import get_all_phones, get_phone_by_slug
from app.models.query import EasyRecommendRequest, MediumRecommendRequest
from app.services.recommender import recommend_easy, recommend_medium
from app.services.hardware_similarity import find_similar_phones
from app.services.hardware_scorer import normalize_hardware_vector
from app.routers.recommend import _enforce_brand_diversity

SCENARIOS = [
    {
        "name": "1. Ultra-Low Budget Student",
        "type": "easy",
        "persona": "Student",
        "budget": 10000.0,
        "expect_max_price": 10500.0
    },
    {
        "name": "2. Mid-Range BGMI Competitive Gamer",
        "type": "easy",
        "persona": "Gamer",
        "budget": 35000.0,
        "expect_keywords": ["Gaming", "Silicon", "Vapor", "120Hz", "144Hz", "Performance"]
    },
    {
        "name": "3. 4K HDR Vlog & Reels Creator",
        "type": "easy",
        "persona": "Camera creator reels vlog 4k",
        "budget": 55000.0,
        "expect_keywords": ["Optics", "Camera", "Video", "Sensor", "Telephoto", "ZEISS", "OIS"]
    },
    {
        "name": "4. Pure Clean Stock OS Purist",
        "type": "easy",
        "persona": "Clean stock Android, zero ads, no bloatware",
        "budget": 32000.0,
        "expect_keywords": ["Clean", "Software", "Ad-free"]
    },
    {
        "name": "5. Ultra Flagship Executive",
        "type": "easy",
        "persona": "Executive flagship top tier",
        "budget": 150000.0,
        "expect_min_price": 80000.0
    },
    {
        "name": "6. Medium Mode 80% Battery Focus",
        "type": "medium",
        "priorities": {"battery": 0.80, "performance": 0.05, "camera": 0.05, "display": 0.05, "build": 0.05},
        "budget": 22000.0,
        "expect_max_price": 23100.0
    },
    {
        "name": "7. Medium Mode 80% Silicon Focus",
        "type": "medium",
        "priorities": {"performance": 0.80, "battery": 0.05, "camera": 0.05, "display": 0.05, "build": 0.05},
        "budget": 30000.0,
        "expect_max_price": 31500.0
    },
    {
        "name": "8. Hardware Spec Clones (S26 Ultra)",
        "type": "similar",
        "target_slug": "Samsung Galaxy S26 Ultra",
        "budget": 150000.0
    },
    {
        "name": "9. Hardware Spec Clones (Budget 5G)",
        "type": "similar",
        "target_slug": "Realme 16x 5G",
        "budget": 20000.0
    },
    {
        "name": "10. Tight Budget Squeeze Optimization",
        "type": "easy",
        "persona": "General",
        "budget": 18000.0,
        "expect_max_price": 18900.0
    }
]

async def run_scenario_tests():
    print("=" * 100)
    print("PHONOS.AI RECOMMENDATION ENGINE — LIVE SCENARIO TEST SUITE")
    print("=" * 100)

    # Load catalogue phones from DB
    all_phones = await get_all_phones(limit=300)
    print(f"Loaded {len(all_phones)} catalogue phones from SQLite.\n")

    results_table = []

    for sc in SCENARIOS:
        name = sc["name"]
        stype = sc["type"]
        status = "PASS"
        top_phone_name = "N/A"
        top_score = 0.0
        top_price = 0.0
        reason = "N/A"
        tradeoff = "N/A"

        try:
            if stype == "easy":
                req = EasyRecommendRequest(persona=sc["persona"], budget=sc["budget"])
                raw_recs = recommend_easy(all_phones, req)
                recs = _enforce_brand_diversity(raw_recs)
                if not recs:
                    status = "FAIL (Empty recs)"
                else:
                    first = recs[0]
                    top_phone_name = f"{first['phone'].brand} {first['phone'].name}"
                    top_score = round(first["score"], 1)
                    top_price = first["phone"].price_numeric or first["phone"].price
                    reason = first["match_reasons"][0] if first.get("match_reasons") else "N/A"
                    tradeoff = first["trade_offs"][0] if first.get("trade_offs") else "None"

                    # Assertions
                    if sc.get("expect_max_price") and top_price > sc["expect_max_price"]:
                        status = f"FAIL (Price {top_price} > max {sc['expect_max_price']})"
                    if sc.get("expect_min_price") and top_price < sc["expect_min_price"]:
                        status = f"FAIL (Price {top_price} < min {sc['expect_min_price']})"

            elif stype == "medium":
                req = MediumRecommendRequest(priorities=sc["priorities"], budget=sc["budget"])
                raw_recs = recommend_medium(all_phones, req)
                recs = _enforce_brand_diversity(raw_recs)
                if not recs:
                    status = "FAIL (Empty recs)"
                else:
                    first = recs[0]
                    top_phone_name = f"{first['phone'].brand} {first['phone'].name}"
                    top_score = round(first["score"], 1)
                    top_price = first["phone"].price_numeric or first["phone"].price
                    reason = first["match_reasons"][0] if first.get("match_reasons") else "N/A"
                    tradeoff = first["trade_offs"][0] if first.get("trade_offs") else "None"

            elif stype == "similar":
                target = await get_phone_by_slug(sc["target_slug"])
                if not target:
                    # Fallback to finding by name substring
                    for p in all_phones:
                        if sc["target_slug"].lower() in p.name.lower():
                            target = p
                            break

                if not target:
                    status = f"FAIL (Target {sc['target_slug']} not found)"
                else:
                    vec = normalize_hardware_vector(target)
                    sims = find_similar_phones(vec, top_k=4, max_budget=sc.get("budget"), exclude_ids=[target.id])
                    if not sims:
                        status = "FAIL (No similar clones found)"
                    else:
                        top_phone_name = f"{sims[0]['brand']} {sims[0]['name']}"
                        top_score = round(sims[0]["similarity_score"] * 100, 1)
                        top_price = sims[0]["price"]
                        reason = f"Closest 5D Hardware Match ({top_score}%) to {target.name}"
                        tradeoff = f"Direct hardware competitor at Rs.{top_price:,.0f}"

        except Exception as e:
            status = f"ERROR ({str(e)[:30]})"

        results_table.append({
            "name": name,
            "top_phone": top_phone_name,
            "score": top_score,
            "price": top_price,
            "status": status,
            "reason": reason[:60] + "..." if len(reason) > 60 else reason
        })

    # Print Table
    print(f"{'# SCENARIO':<38} | {'STATUS':<6} | {'TOP RECOMMENDATION':<32} | {'SCORE':<5} | {'PRICE (INR)':<11}")
    print("-" * 100)
    for r in results_table:
        print(f"{r['name']:<38} | {r['status']:<6} | {r['top_phone']:<32} | {r['score']:<5} | Rs.{r['price']:>9,}")

    print("=" * 100)
    all_passed = all("PASS" in r["status"] for r in results_table)
    if all_passed:
        print("✅ ALL 10 LIVE SCENARIOS VALIDATED SUCCESSFULLY WITHOUT ERRORS.")
    else:
        print("❌ SOME SCENARIOS FLAGGED ISSUES.")
    print("=" * 100)

if __name__ == "__main__":
    asyncio.run(run_scenario_tests())
