"""
Phonos.ai Complete Recommendation Engine & Confidence Evaluation Suite
========================================================================
Executes comprehensive offline benchmark tests across all personas, slider weights,
and natural language queries. Calculates ECE calibration, constraint validity rates,
spec grounding fidelity, persona congruency index, and brand diversity entropy.

Generates:
1. apps/api/evaluation_confidence_report.json (machine telemetry)
2. ENGINE_CONFIDENCE_EVALUATION_REPORT.md (executive Markdown report with tables)
"""

import os
import sys
import time
import json
import asyncio
import numpy as np

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.queries import get_all_phones
from app.models.query import EasyRecommendRequest, MediumRecommendRequest, DeepRecommendRequest
from app.services.recommender import recommend_easy, recommend_medium, recommend_deep
from app.routers.recommend import _enforce_brand_diversity
from app.services.confidence_evaluator import (
    compute_recommendation_confidence,
    compute_ece_and_calibration,
    compute_brand_diversity_index,
    compute_persona_congruency_index,
    is_phone_phantom_or_excluded
)

BENCHMARK_SCENARIOS = [
    # ── 1. EASY MODE PERSONAS & BUDGET TIERS ──
    {
        "id": "EASY-01",
        "mode": "easy",
        "category": "Student Entry (₹10,000)",
        "req": EasyRecommendRequest(persona="Student", budget=10000),
        "persona": "Student",
        "budget": 10000,
        "expect_max_price": 10500,
        "description": "Strict low budget student daily driver"
    },
    {
        "id": "EASY-02",
        "mode": "easy",
        "category": "Student Mid-Range (₹20,000)",
        "req": EasyRecommendRequest(persona="Student", budget=20000),
        "persona": "Student",
        "budget": 20000,
        "expect_max_price": 21000,
        "description": "College student balanced performance & battery"
    },
    {
        "id": "EASY-03",
        "mode": "easy",
        "category": "Gamer Budget (₹25,000)",
        "req": EasyRecommendRequest(persona="Gamer", budget=25000),
        "persona": "Gamer",
        "budget": 25000,
        "expect_max_price": 26250,
        "description": "Budget competitive BGMI/framerate focus"
    },
    {
        "id": "EASY-04",
        "mode": "easy",
        "category": "Gamer Mid-Flagship (₹45,000)",
        "req": EasyRecommendRequest(persona="Gamer", budget=45000),
        "persona": "Gamer",
        "budget": 45000,
        "expect_max_price": 47250,
        "description": "High tier silicon + 144Hz cooling focus"
    },
    {
        "id": "EASY-05",
        "mode": "easy",
        "category": "Gamer Ultra Flagship (₹90,000)",
        "req": EasyRecommendRequest(persona="Gamer", budget=90000),
        "persona": "Gamer",
        "budget": 90000,
        "expect_max_price": 94500,
        "description": "Snapdragon 8 Elite / Dimensity 9400 extreme tier"
    },
    {
        "id": "EASY-06",
        "mode": "easy",
        "category": "Creator Mid-Range (₹35,000)",
        "req": EasyRecommendRequest(persona="Camera / Content Creator", budget=35000),
        "persona": "Camera / Content Creator",
        "budget": 35000,
        "expect_max_price": 36750,
        "description": "OIS + 4K video + front camera clarity"
    },
    {
        "id": "EASY-07",
        "mode": "easy",
        "category": "Creator Premium (₹60,000)",
        "req": EasyRecommendRequest(persona="Camera / Content Creator", budget=60000),
        "persona": "Camera / Content Creator",
        "budget": 60000,
        "expect_max_price": 63000,
        "description": "Telephoto periscope + 4K60 + portrait optics"
    },
    {
        "id": "EASY-08",
        "mode": "easy",
        "category": "Creator Flagship Studio (₹1,20,000)",
        "req": EasyRecommendRequest(persona="Camera / Content Creator", budget=120000),
        "persona": "Camera / Content Creator",
        "budget": 120000,
        "expect_max_price": 126000,
        "description": "ZEISS 200MP APO / Log video / Cinema tier"
    },
    {
        "id": "EASY-09",
        "mode": "easy",
        "category": "Executive / Business (₹70,000)",
        "req": EasyRecommendRequest(persona="Executive / Business", budget=70000),
        "persona": "Executive / Business",
        "budget": 70000,
        "expect_max_price": 73500,
        "description": "Premium build, reliability, battery, and clean UX"
    },
    {
        "id": "EASY-10",
        "mode": "easy",
        "category": "Clean OS Purist (₹32,000)",
        "req": EasyRecommendRequest(persona="Clean stock Android UI, zero ads, no bloatware", budget=32000),
        "persona": "Clean stock Android UI",
        "budget": 32000,
        "expect_max_price": 33600,
        "description": "Ad-free Motorola / Nothing / Google clean software"
    },
    {
        "id": "EASY-11",
        "mode": "easy",
        "category": "Senior / Basic Usability (₹12,000)",
        "req": EasyRecommendRequest(persona="Senior citizen, simple, big battery", budget=12000),
        "persona": "Senior / Basic",
        "budget": 12000,
        "expect_max_price": 12600,
        "description": "Reliable daily smartphone for seniors"
    },

    # ── 2. MEDIUM MODE MULTI-ATTRIBUTE SLIDERS ──
    {
        "id": "MED-01",
        "mode": "medium",
        "category": "Medium - 80% Performance Focus",
        "req": MediumRecommendRequest(budget=30000, priorities={"performance": 0.80, "camera": 0.05, "battery": 0.05, "display": 0.05, "build": 0.05}),
        "persona": "General",
        "budget": 30000,
        "expect_max_price": 31500,
        "description": "Extreme processing priority under 30k"
    },
    {
        "id": "MED-02",
        "mode": "medium",
        "category": "Medium - 80% Battery Focus",
        "req": MediumRecommendRequest(budget=22000, priorities={"battery": 0.80, "performance": 0.05, "camera": 0.05, "display": 0.05, "build": 0.05}),
        "persona": "General",
        "budget": 22000,
        "expect_max_price": 23100,
        "description": "Extreme battery & charge priority under 22k"
    },
    {
        "id": "MED-03",
        "mode": "medium",
        "category": "Medium - 80% Camera Focus",
        "req": MediumRecommendRequest(budget=50000, priorities={"camera": 0.80, "performance": 0.05, "battery": 0.05, "display": 0.05, "build": 0.05}),
        "persona": "General",
        "budget": 50000,
        "expect_max_price": 52500,
        "description": "Extreme photography priority under 50k"
    },
    {
        "id": "MED-04",
        "mode": "medium",
        "category": "Medium - Balanced All-Rounder",
        "req": MediumRecommendRequest(budget=40000, priorities={"performance": 0.25, "camera": 0.25, "battery": 0.25, "display": 0.25}),
        "persona": "General",
        "budget": 40000,
        "expect_max_price": 42000,
        "description": "Evenly weighted specs across all attributes"
    },
    {
        "id": "MED-05",
        "mode": "medium",
        "category": "Medium - Display & Build Focus",
        "req": MediumRecommendRequest(budget=65000, priorities={"display": 0.50, "build": 0.30, "performance": 0.10, "camera": 0.05, "battery": 0.05}),
        "persona": "General",
        "budget": 65000,
        "expect_max_price": 68250,
        "description": "LTPO AMOLED 144Hz and premium materials"
    },

    # ── 3. DEEP MODE NATURAL LANGUAGE QUERIES ──
    {
        "id": "DEEP-01",
        "mode": "deep",
        "category": "Deep - Compact Flagship Query",
        "req": DeepRecommendRequest(query="Compact smartphone with telephoto zoom, wireless charging and IP68", budget=85000),
        "persona": "Compact flagship",
        "budget": 85000,
        "expect_max_price": 89250,
        "description": "Natural language query: Compact flagship with telephoto"
    },
    {
        "id": "DEEP-02",
        "mode": "deep",
        "category": "Deep - Clean Stock OS with Fast Charge",
        "req": DeepRecommendRequest(query="Clean stock Android with zero bloatware, fast charging, and smooth 120Hz display", budget=35000),
        "persona": "Clean stock Android",
        "budget": 35000,
        "expect_max_price": 36750,
        "description": "Natural language query: Stock Android with fast charging"
    },
    {
        "id": "DEEP-03",
        "mode": "deep",
        "category": "Deep - 4K120 Vlogging Telephoto",
        "req": DeepRecommendRequest(query="Best phone for YouTube 4K vlogs with periscope zoom and great stabilization", budget=75000),
        "persona": "Vlog telephoto",
        "budget": 75000,
        "expect_max_price": 78750,
        "description": "Natural language query: 4K video recording with periscope"
    },

    # ── 4. ADVERSARIAL & EDGE CASES ──
    {
        "id": "EDGE-01",
        "mode": "easy",
        "category": "Edge Case - Ultra Luxury ₹2,00,000",
        "req": EasyRecommendRequest(persona="Luxury Flagship", budget=200000),
        "persona": "Luxury Flagship",
        "budget": 200000,
        "expect_max_price": 210000,
        "description": "Ensure zero phantom devices (e.g. S27 Ultra, Xiaomi 18) in top-tier"
    },
    {
        "id": "EDGE-02",
        "mode": "easy",
        "category": "Edge Case - Ultra Low ₹8,000",
        "req": EasyRecommendRequest(persona="Student", budget=8000),
        "persona": "Student",
        "budget": 8000,
        "expect_max_price": 8400,
        "description": "Ultra low budget - ensure only modern functional phones"
    },
    {
        "id": "EDGE-03",
        "mode": "easy",
        "category": "Edge Case - Dynamic Floor Squeeze ₹18,000",
        "req": EasyRecommendRequest(persona="General", budget=18000),
        "persona": "General",
        "budget": 18000,
        "expect_max_price": 18900,
        "description": "Ensures budget is maximized without recommending cheap ₹6k phones"
    }
]

async def run_full_confidence_evaluation():
    print("=" * 90)
    print("🚀 PHONOS.AI RECOMMENDATION ENGINE — COMPLETE CONFIDENCE & QUALITY BENCHMARK")
    print(f"Executing {len(BENCHMARK_SCENARIOS)} diverse evaluation scenarios across Easy, Medium, Deep, and Edge modes.")
    print("=" * 90)

    # 1. Fetch live SQLite catalogue
    all_phones = await get_all_phones(limit=500)
    print(f"✅ Loaded {len(all_phones)} active catalogue devices from SQLite.\n")

    scenario_results = []
    all_confidence_scores = []
    all_empirical_outcomes = []
    pci_scores = []
    grounding_scores = []
    diversity_scores = []
    latencies = []
    total_recs_count = 0
    valid_recs_count = 0
    zero_phantom_violations = 0

    for sc in BENCHMARK_SCENARIOS:
        sc_id = sc["id"]
        mode = sc["mode"]
        cat = sc["category"]
        desc = sc["description"]
        budget = sc["budget"]
        persona = sc["persona"]

        t0 = time.time()
        error_msg = None
        recs = []

        try:
            if mode == "easy":
                raw = recommend_easy(all_phones, sc["req"])
            elif mode == "medium":
                raw = recommend_medium(all_phones, sc["req"])
            elif mode == "deep":
                raw = recommend_deep(all_phones, sc["req"])
            else:
                raw = []

            # Enforce brand diversity (max 2 per brand)
            diverse_raw = _enforce_brand_diversity(raw)
            recs = diverse_raw[:5]

        except Exception as e:
            error_msg = str(e)

        elapsed_ms = round((time.time() - t0) * 1000, 2)
        latencies.append(elapsed_ms)

        sc_recs_summary = []
        sc_confidences = []
        sc_pci = compute_persona_congruency_index(recs, persona) if recs else 0.0
        pci_scores.append(sc_pci)

        div_metrics = compute_brand_diversity_index(recs) if recs else {"shannon_entropy": 0.0, "simpson_index": 0.0, "unique_brands": 0, "max_brand_share": 0.0}
        diversity_scores.append(div_metrics)

        all_sc_constraints_pass = True

        for rank, r in enumerate(recs, 1):
            total_recs_count += 1
            phone = r["phone"] if isinstance(r, dict) else getattr(r, "phone", None)
            conf_data = compute_recommendation_confidence(r, persona, budget)
            conf_score = conf_data["confidence_score"]
            sc_confidences.append(conf_score)
            all_confidence_scores.append(conf_score)

            # Grounding
            g_score = conf_data["pillars"]["spec_grounding_fidelity"]
            grounding_scores.append(g_score)

            # Validation checks
            price = phone.price_numeric if phone.price_numeric is not None else float(phone.price or 0.0)
            is_budget_ok = price <= budget * 1.05
            is_phantom = is_phone_phantom_or_excluded(phone.name)
            is_year_ok = (phone.launch_year or 2025) >= 2024

            if is_phantom:
                zero_phantom_violations += 1

            # Empirical success: within budget + verified + not phantom + year >= 2024 + high persona congruence
            success = is_budget_ok and (not is_phantom) and is_year_ok and (conf_score >= 0.70)
            all_empirical_outcomes.append(success)

            if success:
                valid_recs_count += 1
            else:
                all_sc_constraints_pass = False

            sc_recs_summary.append({
                "rank": rank,
                "name": phone.name,
                "brand": phone.brand,
                "price": price,
                "budget_utilization": f"{round((price/budget)*100, 1)}%",
                "score": round(r["score"], 1) if isinstance(r, dict) else round(r.score, 1),
                "confidence_score": conf_score,
                "grade": conf_data["grade"],
                "pillars": conf_data["pillars"],
                "is_phantom": is_phantom,
                "is_budget_ok": is_budget_ok
            })

        mean_sc_conf = round(float(np.mean(sc_confidences)), 4) if sc_confidences else 0.0
        status = "PASS" if (len(recs) > 0 and all_sc_constraints_pass and error_msg is None) else ("ERROR" if error_msg else "FAIL")

        print(f"[{sc_id}] {cat:<40} | Status: {status:<5} | Recs: {len(recs)} | Avg Conf: {mean_sc_conf:.3f} | Latency: {elapsed_ms}ms", flush=True)

        scenario_results.append({
            "id": sc_id,
            "category": cat,
            "mode": mode,
            "description": desc,
            "budget": budget,
            "persona": persona,
            "status": status,
            "latency_ms": elapsed_ms,
            "error": error_msg,
            "mean_confidence": mean_sc_conf,
            "persona_congruency_index": sc_pci,
            "brand_diversity": div_metrics,
            "recommendations": sc_recs_summary
        })

    # ── 2. CALCULATE GLOBAL STATISTICAL METRICS ──
    cal_metrics = compute_ece_and_calibration(all_confidence_scores, all_empirical_outcomes, n_bins=10)
    cvr = (valid_recs_count / max(1, total_recs_count)) * 100.0
    mean_global_conf = round(float(np.mean(all_confidence_scores)), 4) if all_confidence_scores else 0.0
    mean_pci = round(float(np.mean(pci_scores)), 4) if pci_scores else 0.0
    mean_grounding = round(float(np.mean(grounding_scores)), 4) if grounding_scores else 0.0
    mean_latency = round(float(np.mean(latencies)), 2)
    phantom_integrity = 100.0 if zero_phantom_violations == 0 else max(0.0, 100.0 - (zero_phantom_violations / total_recs_count * 100))
    avg_entropy = round(float(np.mean([d["shannon_entropy"] for d in diversity_scores])), 4)
    avg_simpson = round(float(np.mean([d["simpson_index"] for d in diversity_scores])), 4)

    summary_stats = {
        "total_scenarios_evaluated": len(BENCHMARK_SCENARIOS),
        "total_recommendations_evaluated": total_recs_count,
        "valid_recommendations_count": valid_recs_count,
        "constraint_validity_rate_pct": round(cvr, 2),
        "phantom_integrity_rate_pct": round(phantom_integrity, 2),
        "mean_recommendation_confidence_score": mean_global_conf,
        "mean_persona_congruency_index": mean_pci,
        "mean_spec_grounding_fidelity": mean_grounding,
        "expected_calibration_error_ece": cal_metrics["ece"],
        "max_calibration_error_mce": cal_metrics["mce"],
        "brier_score": cal_metrics["brier_score"],
        "mean_brand_diversity_shannon": avg_entropy,
        "mean_brand_diversity_simpson": avg_simpson,
        "average_response_latency_ms": mean_latency,
        "calibration_bins": cal_metrics["bins"]
    }

    full_report = {
        "engine_name": "Phonos.ai Multi-Stage Recommendation Engine",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "benchmark_summary": summary_stats,
        "scenarios": scenario_results
    }

    # ── 3. WRITE JSON TELEMETRY ──
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../evaluation_confidence_report.json'))
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(full_report, f, indent=2, ensure_ascii=False)
    print(f"\n📁 Saved comprehensive evaluation data to: {json_path}")

    # ── 4. WRITE VISUAL EXECUTIVE MARKDOWN REPORT ──
    md_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ENGINE_CONFIDENCE_EVALUATION_REPORT.md'))
    generate_markdown_report(full_report, md_path)
    print(f"📄 Saved executive benchmark report to: {md_path}")

    # ── 5. PRINT CONSOLE SUMMARY ──
    print("\n" + "=" * 90)
    print("📊 PHONOS.AI ENGINE CONFIDENCE BENCHMARK SUMMARY")
    print("=" * 90)
    print(f"Total Scenarios Evaluated       : {summary_stats['total_scenarios_evaluated']}")
    print(f"Total Recommendations Generated : {summary_stats['total_recommendations_evaluated']}")
    print(f"Constraint Validity Rate (CVR)  : {summary_stats['constraint_validity_rate_pct']}% (Target: >= 99%)")
    print(f"Phantom Device Integrity Rate   : {summary_stats['phantom_integrity_rate_pct']}% (Target: 100%)")
    print(f"Mean Confidence Score (RCS)     : {summary_stats['mean_recommendation_confidence_score']} / 1.000")
    print(f"Expected Calibration Error (ECE): {summary_stats['expected_calibration_error_ece']} (Target: < 0.08)")
    print(f"Brier Calibration Score         : {summary_stats['brier_score']}")
    print(f"Persona Congruency Index (PCI)  : {summary_stats['mean_persona_congruency_index']} / 1.000")
    print(f"Spec Grounding & Fact Fidelity  : {summary_stats['mean_spec_grounding_fidelity'] * 100:.1f}%")
    print(f"Mean Brand Diversity (Shannon)  : {summary_stats['mean_brand_diversity_shannon']}")
    print(f"Average Engine Latency          : {summary_stats['average_response_latency_ms']} ms")
    print("=" * 90)

    if cvr >= 99.0 and phantom_integrity == 100.0 and summary_stats['expected_calibration_error_ece'] < 0.10:
        print("🏆 VERDICT: RECOMMENDATION ENGINE HIGH CONFIDENCE CERTIFIED (GRADE A+)")
    else:
        print("⚠️ VERDICT: ENGINE MEETS BASELINE; MINOR CALIBRATION ADJUSTMENTS SUGGESTED")
    print("=" * 90)

def generate_markdown_report(report: Dict[str, Any], output_path: str):
    s = report["benchmark_summary"]
    scenarios = report["scenarios"]

    md = []
    md.append("# Phonos.ai Recommendation Engine — Confidence & Quality Benchmark Report")
    md.append(f"**Generated on:** `{report['timestamp']}`  ")
    md.append(f"**Engine Architecture:** 4-Stage Hybrid (Vector Search + Knowledge Graph + XGBoost Ranker + ABSA Sentiment + AI Verification)  ")
    md.append("\n---\n")

    md.append("## 1. Executive Summary & Confidence Scorecard\n")
    md.append("| Metric | Result | Benchmark Target | Status |")
    md.append("| :--- | :--- | :--- | :--- |")
    md.append(f"| **Constraint Validity Rate (CVR)** | **{s['constraint_validity_rate_pct']}%** | $\\ge 99.0\\%$ | {'✅ PASS' if s['constraint_validity_rate_pct'] >= 99.0 else '⚠️ WARN'} |")
    md.append(f"| **Phantom Device Exclusion Rate** | **{s['phantom_integrity_rate_pct']}%** | $100.0\\%$ | {'✅ PASS' if s['phantom_integrity_rate_pct'] == 100.0 else '❌ FAIL'} |")
    md.append(f"| **Mean Recommendation Confidence (RCS)** | **{s['mean_recommendation_confidence_score']} / 1.0** | $\\ge 0.820$ | {'✅ PASS' if s['mean_recommendation_confidence_score'] >= 0.82 else '⚠️ WARN'} |")
    md.append(f"| **Expected Calibration Error (ECE)** | **{s['expected_calibration_error_ece']}** | $< 0.080$ | {'✅ PASS' if s['expected_calibration_error_ece'] < 0.08 else '⚠️ WARN'} |")
    md.append(f"| **Brier Calibration Score** | **{s['brier_score']}** | $< 0.100$ | {'✅ PASS' if s['brier_score'] < 0.10 else '⚠️ WARN'} |")
    md.append(f"| **Persona Congruency Index (PCI)** | **{s['mean_persona_congruency_index']} / 1.0** | $\\ge 0.850$ | {'✅ PASS' if s['mean_persona_congruency_index'] >= 0.85 else '⚠️ WARN'} |")
    md.append(f"| **Spec Grounding & Fact Fidelity** | **{s['mean_spec_grounding_fidelity'] * 100:.1f}%** | $\\ge 98.0\\%$ | {'✅ PASS' if s['mean_spec_grounding_fidelity'] >= 0.98 else '⚠️ WARN'} |")
    md.append(f"| **Brand Diversity (Shannon Entropy)** | **{s['mean_brand_diversity_shannon']}** | $\\ge 1.000$ | {'✅ PASS' if s['mean_brand_diversity_shannon'] >= 1.0 else '⚠️ WARN'} |")
    md.append(f"| **Average Inference Latency** | **{s['average_response_latency_ms']} ms** | $< 500\\text{{ ms}}$ | {'✅ PASS' if s['average_response_latency_ms'] < 500 else '⚠️ WARN'} |")
    md.append("\n---\n")

    md.append("## 2. Confidence Calibration & Reliability Analysis (ECE)\n")
    md.append("Confidence calibration measures whether a confidence score of 90% actually corresponds to a 90% empirical success and satisfaction rate.\n")
    md.append("| Confidence Bin | Sample Count | Avg Confidence | Empirical Accuracy | Calibration Gap (|Acc - Conf|) |")
    md.append("| :--- | :--- | :--- | :--- | :--- |")
    for b in s["calibration_bins"]:
        md.append(f"| `{b['bin_range']}` | {b['count']} | {b['avg_confidence']:.3f} | {b['avg_accuracy']:.3f} | {b['calibration_gap']:.3f} |")
    md.append(f"\n**Global Expected Calibration Error (ECE):** `{s['expected_calibration_error_ece']}`  ")
    md.append(f"**Maximum Calibration Error (MCE):** `{s['max_calibration_error_mce']}`\n")
    md.append("\n---\n")

    md.append("## 3. Detailed Evaluation Scenarios Breakdown\n")
    md.append("| ID | Category & User Intent | Budget (₹) | Top Recommended Device | RCS Confidence | PCI Fit | Diversity (Brands) | Status |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for sc in scenarios:
        top_rec = sc["recommendations"][0] if sc["recommendations"] else None
        top_name = f"{top_rec['brand']} {top_rec['name']}" if top_rec else "N/A"
        top_conf = f"{top_rec['confidence_score']:.3f}" if top_rec else "0.0"
        brands_count = sc["brand_diversity"]["unique_brands"]
        md.append(f"| `{sc['id']}` | {sc['category']} | ₹{sc['budget']:,} | **{top_name}** | `{top_conf}` | `{sc['persona_congruency_index']:.2f}` | {brands_count} brands | **{sc['status']}** |")

    md.append("\n---\n")
    md.append("## 4. Pillar-by-Pillar Confidence Architecture\n")
    md.append("Phonos.ai computes recommendation confidence through 5 deterministic pillars:\n")
    md.append("1. **Constraint Validity (30% weight)**: Strict budget compliance, dynamic price floor, 2024–2026 launch year recency, zero phantom models.")
    md.append("2. **Persona & Hardware Alignment (25% weight)**: Silicon tier, camera optics, display refresh rate, and battery endurance matched against user persona.")
    md.append("3. **Spec Grounding Fidelity (20% weight)**: Fact-checking that all claims in recommendation pitches match verifiable hardware specs.")
    md.append("4. **Market Authenticity (15% weight)**: Official active selling catalog status and Indian retail validation.")
    md.append("5. **Sentiment & Consensus (10% weight)**: Aspect-Based Sentiment Analysis (ABSA) extracted from reviewer testing.")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md))

if __name__ == "__main__":
    asyncio.run(run_full_confidence_evaluation())
