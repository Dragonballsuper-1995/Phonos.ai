"""
evaluate_recommendations.py — Diagnostic & Quality Evaluation Suite for Phonos.ai
==================================================================================
Runs the recommendation engine across various personas, budgets, and priority matrices.
Outputs top recommendations, match reasons, scientific benchmark citations, and trade-offs.
"""

import os
import sys
import asyncio
from typing import List, Dict, Any

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.queries import get_all_phones
from app.models.query import EasyRecommendRequest, MediumRecommendRequest, DeepRecommendRequest
from app.services.recommender import recommend_easy, recommend_medium, recommend_deep


SCENARIOS = [
    # --- Gaming Personas ---
    {
        "name": "1. Budget Gamer (₹18,000)",
        "mode": "easy",
        "persona": "Gamer",
        "budget": 18000.0,
    },
    {
        "name": "2. Mid-Range Esports Gamer (₹35,000)",
        "mode": "easy",
        "persona": "Gamer",
        "budget": 35000.0,
    },
    {
        "name": "3. Flagship Extreme Gamer (₹75,000)",
        "mode": "easy",
        "persona": "Gamer",
        "budget": 75000.0,
    },

    # --- Photography / Camera Enthusiasts ---
    {
        "name": "4. Budget Camera / Social Creator (₹25,000)",
        "mode": "easy",
        "persona": "Photography",
        "budget": 25000.0,
    },
    {
        "name": "5. Mid-Range Camera Specialist (₹45,000)",
        "mode": "easy",
        "persona": "Photography",
        "budget": 45000.0,
    },
    {
        "name": "6. Ultra Flagship Camera / DxOMark Leader (₹140,000)",
        "mode": "easy",
        "persona": "Photography",
        "budget": 140000.0,
    },

    # --- Student & Battery ---
    {
        "name": "7. Student / Long Battery & Value (₹15,000)",
        "mode": "easy",
        "persona": "Student",
        "budget": 15000.0,
    },

    # --- Working Professional ---
    {
        "name": "8. Executive / Business Flagship (₹85,000)",
        "mode": "easy",
        "persona": "Professional",
        "budget": 85000.0,
    },

    # --- Medium Mode: Custom 5D Priority Matrices ---
    {
        "name": "9. Custom Priorities: Heavy Camera & Performance (₹50,000)",
        "mode": "medium",
        "budget": 50000.0,
        "priorities": {
            "camera": 0.40,
            "performance": 0.35,
            "battery": 0.15,
            "display": 0.10,
        }
    },
    {
        "name": "10. Custom Priorities: Maximum Battery & Display (₹30,000)",
        "mode": "medium",
        "budget": 30000.0,
        "priorities": {
            "camera": 0.10,
            "performance": 0.20,
            "battery": 0.45,
            "display": 0.25,
        }
    },

    # --- Deep Mode: Natural Semantic Queries ---
    {
        "name": "11. Deep Mode: 'Best compact flagship with telephoto zoom' (₹70,000)",
        "mode": "deep",
        "query": "Best compact flagship with telephoto zoom",
        "budget": 70000.0,
    },
    {
        "name": "12. Deep Mode: 'Phone for 4K 60fps video and clean stock UI' (₹40,000)",
        "mode": "deep",
        "query": "Phone for 4K 60fps video and clean stock UI",
        "budget": 40000.0,
    },
]


async def run_evaluation():
    print("=" * 80)
    print("🔬 PHONOS.AI ENGINE RECOMMENDATION EVALUATION MATRIX")
    print("=" * 80)

    # Fetch full Indian catalog from database
    all_phones = await get_all_phones(limit=2000)
    print(f"📦 Active Indian Phones Loaded: {len(all_phones)} models")
    print("-" * 80)

    for sc in SCENARIOS:
        print(f"\n================================================================================")
        print(f"🎯 Scenario: {sc['name']}")
        print(f"================================================================================")

        if sc["mode"] == "easy":
            req = EasyRecommendRequest(persona=sc["persona"], budget=sc["budget"])
            results = recommend_easy(all_phones, req)[:3]
        elif sc["mode"] == "medium":
            req = MediumRecommendRequest(budget=sc["budget"], priorities=sc["priorities"])
            results = recommend_medium(all_phones, req)[:3]
        elif sc["mode"] == "deep":
            req = DeepRecommendRequest(query=sc["query"], budget=sc["budget"])
            results = recommend_deep(all_phones, req)[:3]
        else:
            continue

        for rank, res in enumerate(results, start=1):
            phone = res["phone"]
            score = res["score"]
            reasons = res.get("match_reasons", [])
            trade_offs = res.get("trade_offs", [])

            price_str = f"₹{int(phone.price_numeric):,}" if phone.price_numeric else phone.price

            # Extract benchmark badges if present
            benchmarks = []
            if phone.dxomark_camera_score:
                benchmarks.append(f"DxOMark: {int(phone.dxomark_camera_score)}")
            if phone.geekbench_multi:
                benchmarks.append(f"GB6 Multi: {int(phone.geekbench_multi):,}")
            if phone.antutu_v10_score:
                benchmarks.append(f"AnTuTu: {phone.antutu_v10_score/1000000:.1f}M")
            if phone.gsmarena_battery_hours:
                benchmarks.append(f"Battery: {phone.gsmarena_battery_hours}h")
            if phone.vcx_camera_score:
                benchmarks.append(f"VCX: {int(phone.vcx_camera_score)}★")

            bench_str = " | ".join(benchmarks) if benchmarks else "Spec-Engine Hybrid Fallback"

            print(f"  #{rank} [{score:.1f}% Match] {phone.name} ({phone.brand}) — {price_str}")
            print(f"     📊 Lab Benchmarks: {bench_str}")
            if reasons:
                print(f"     ✅ Key Strengths: {reasons[0]}")
            if trade_offs:
                print(f"     ⚠️ Trade-off: {trade_offs[0]}")
            print()


if __name__ == "__main__":
    asyncio.run(run_evaluation())
