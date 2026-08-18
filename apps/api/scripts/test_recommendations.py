import sys
import os
import asyncio

# Ensure API root is in path
API_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if API_ROOT not in sys.path:
    sys.path.insert(0, API_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.db.queries import get_all_phones
from app.models.query import EasyRecommendRequest, MediumRecommendRequest, DeepRecommendRequest
from app.services.recommender import recommend_easy, recommend_medium, recommend_deep
from app.services.verifier import verify_recommendations
from app.routers.recommend import _enforce_brand_diversity

TEST_CASES = [
    {
        "name": "1. Student / Battery Focus (₹15,000 Budget)",
        "type": "easy",
        "req": EasyRecommendRequest(persona="Student", budget=15000.0)
    },
    {
        "name": "2. Competitive Gamer (₹28,000 Budget)",
        "type": "easy",
        "req": EasyRecommendRequest(persona="Gamer", budget=28000.0)
    },
    {
        "name": "3. Clean Software / No Bloatware Enthusiast (₹40,000 Budget)",
        "type": "medium",
        "req": MediumRecommendRequest(
            persona="Clean Software",
            budget=40000.0,
            priorities={"performance": 0.2, "camera": 0.2, "display": 0.2, "battery": 0.2, "software": 0.2}
        )
    },
    {
        "name": "4. Photography & Content Creator (₹65,000 Budget)",
        "type": "easy",
        "req": EasyRecommendRequest(persona="Photography", budget=65000.0)
    },
    {
        "name": "5. Ultra-Premium Flagship / Executive (₹1,50,000 Budget)",
        "type": "easy",
        "req": EasyRecommendRequest(persona="Professional", budget=150000.0)
    },
    {
        "name": "6. Deep Freeform Query: 'Compact high-end phone with premium telephoto macro' (₹90,000 Budget)",
        "type": "deep",
        "req": DeepRecommendRequest(
            query="Compact high-end phone with premium telephoto macro and fast wireless charging",
            budget=90000.0
        )
    },
]

async def run_evaluation():
    print("=" * 90)
    print("📱 PHONOS.AI RECOMMENDATION ENGINE — LIVE EVALUATION & AUDIT REPORT")
    print("=" * 90)

    for tc in TEST_CASES:
        print(f"\n🔹 SCENARIO: {tc['name']}")
        print("-" * 90)

        budget = tc["req"].budget
        all_phones = await get_all_phones(max_budget=budget, limit=1000)

        if tc["type"] == "easy":
            scored = recommend_easy(all_phones, tc["req"])
        elif tc["type"] == "medium":
            scored = recommend_medium(all_phones, tc["req"])
        else:
            scored = recommend_deep(all_phones, tc["req"])

        top15 = scored[:15]
        verified = verify_recommendations(top15)
        final_top5 = _enforce_brand_diversity(verified)

        if not final_top5:
            print("   ⚠️ No valid recommendations found within constraints.")
            continue

        for rank, item in enumerate(final_top5, 1):
            p = item["phone"]
            price_str = f"₹{int(p.price):,}" if p.price else "NA"
            catalogue_status = "✅ OFFICIAL ACTIVE" if getattr(p, "is_current_catalogue", 0) == 1 else "ℹ️ Historical DB"
            launch_status = getattr(p, "launch_status", "available")
            
            print(f"   #{rank} {p.fullName:<35} | {price_str:<10} | Score: {item['score']:5.1f} | {catalogue_status} ({launch_status})")
            if item.get("match_reasons"):
                for r in item["match_reasons"][:2]:
                    print(f"       * Reason: {r}")
            if item.get("trade_offs"):
                for t in item["trade_offs"][:1]:
                    print(f"       ! Trade-off: {t}")

    print("\n" + "=" * 90)
    print("🎯 Live Recommendation Evaluation Complete!")
    print("=" * 90)

if __name__ == "__main__":
    asyncio.run(run_evaluation())
