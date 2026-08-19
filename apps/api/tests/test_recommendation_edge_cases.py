"""
test_recommendation_edge_cases.py
==================================
Comprehensive 15-Scenario Edge-Case and Stress-Testing Suite for the Phonos.ai Recommendation Engine.
"""
import pytest
import numpy as np
from unittest.mock import patch
from app.models.phone import PhoneDetails
from app.models.query import EasyRecommendRequest, MediumRecommendRequest
from app.services.recommender import ml_score_phones, recommend_easy, recommend_medium
from app.routers.recommend import _enforce_brand_diversity
from app.services.knowledge_graph import filter_by_knowledge_graph
from app.services.hardware_similarity import find_similar_phones
from app.services.hardware_scorer import normalize_hardware_vector


# ── TEST CASE 1: Ultra-Low Budget Edge Case (₹6,000 - ₹8,000) ─────────────────
def test_case_1_ultra_low_budget_edge_case():
    budget = 8000.0
    phones = [
        PhoneDetails(id=1, name="Budget Champion A", brand="Realme", price=7499.0, price_numeric=7499.0, launch_year=2025),
        PhoneDetails(id=2, name="Budget Basic B", brand="Infinix", price=6299.0, price_numeric=6299.0, launch_year=2025),
        PhoneDetails(id=3, name="Midranger X", brand="Samsung", price=19999.0, price_numeric=19999.0, launch_year=2025),
    ]
    scored = ml_score_phones(phones, persona="Student", budget=budget)
    assert len(scored) == 2  # ₹19,999 phone must be filtered out
    for item in scored:
        assert item["phone"].price_numeric <= budget * 1.05
        assert 50.0 <= item["score"] <= 99.0


# ── TEST CASE 2: Ultra-High Budget Flagship Edge Case (₹1,50,000 - ₹2,00,000) ──
def test_case_2_ultra_high_budget_flagship():
    budget = 180000.0
    phones = [
        PhoneDetails(
            id=10,
            name="Samsung Galaxy S26 Ultra 5G",
            brand="Samsung",
            price=144999.0,
            price_numeric=144999.0,
            launch_year=2026,
            is_current_catalogue=1,
            raw_specs={"chipset": "Snapdragon 8 Elite", "camera": "200 MP periscope telephoto zeiss dolby vision", "display": "120Hz LTPO AMOLED 3000 nits"}
        ),
        PhoneDetails(
            id=11,
            name="Budget Phone Cheap",
            brand="Generic",
            price=12000.0,
            price_numeric=12000.0,
            launch_year=2025
        )
    ]
    scored = ml_score_phones(phones, persona="Photography", budget=budget)
    # The flagship allocating budget properly with current specs should heavily outperform sub-budget phone
    assert len(scored) == 1  # 12k phone is below dynamic 65% floor
    assert scored[0]["phone"].name == "Samsung Galaxy S26 Ultra 5G"
    assert scored[0]["score"] >= 80.0


# ── TEST CASE 3: Gamer Persona Silicon & Refresh Rate Matching ────────────────
def test_case_3_gamer_silicon_and_refresh_rate():
    budget = 45000.0
    gaming_phone = PhoneDetails(
        id=20,
        name="iQOO Neo 10 Pro Gaming",
        brand="iQOO",
        price=39999.0,
        price_numeric=39999.0,
        launch_year=2025,
        raw_specs={"chipset": "Snapdragon 8 Elite", "display": "144Hz AMOLED", "ram": "16GB RAM"}
    )
    battery_phone = PhoneDetails(
        id=21,
        name="Galaxy M55 Stamina",
        brand="Samsung",
        price=38999.0,
        price_numeric=38999.0,
        launch_year=2025,
        raw_specs={"chipset": "Snapdragon 7 Gen 1", "battery": "6000mAh", "display": "120Hz"}
    )
    scored = ml_score_phones([gaming_phone, battery_phone], persona="Gamer", budget=budget)
    assert scored[0]["phone"].name == "iQOO Neo 10 Pro Gaming"
    assert any("Gaming" in r or "Silicon" in r for r in scored[0]["match_reasons"])


# ── TEST CASE 4: Creator / Pro Optics & Video Recording ────────────────────────
def test_case_4_creator_pro_optics_and_video():
    budget = 65000.0
    cam_phone = PhoneDetails(
        id=30,
        name="Vivo X200 Pro Optics",
        brand="Vivo",
        price=62999.0,
        price_numeric=62999.0,
        launch_year=2025,
        raw_specs={"camera": "200 mp zeiss apo telephoto 4k@120fps dolby vision", "chipset": "Dimensity 9400"}
    )
    raw_perf_phone = PhoneDetails(
        id=31,
        name="Raw Performance Phone",
        brand="Realme",
        price=59999.0,
        price_numeric=59999.0,
        launch_year=2025,
        raw_specs={"chipset": "Snapdragon 8 Gen 3", "camera": "50MP basic", "display": "120Hz"}
    )
    scored = ml_score_phones([cam_phone, raw_perf_phone], persona="Creator / Photography", budget=budget)
    assert scored[0]["phone"].name == "Vivo X200 Pro Optics"
    assert any("ZEISS" in r or "Optics" in r or "Video" in r for r in scored[0]["match_reasons"])


# ── TEST CASE 5: Clean Stock OS vs Bloatware UI Taxonomy ──────────────────────
def test_case_5_clean_ui_intent_vs_ad_skins():
    budget = 35000.0
    clean_phone = PhoneDetails(
        id=40,
        name="Motorola Edge 50 Fusion",
        brand="Motorola",
        price=29999.0,
        price_numeric=29999.0,
        launch_year=2025,
        raw_specs={"chipset": "Snapdragon 7s Gen 2", "os": "Hello UI"}
    )
    bloat_phone = PhoneDetails(
        id=41,
        name="Xiaomi Note 14 Pro",
        brand="Xiaomi",
        price=29999.0,
        price_numeric=29999.0,
        launch_year=2025,
        raw_specs={"chipset": "Snapdragon 7s Gen 2", "os": "HyperOS"}
    )
    scored = ml_score_phones([clean_phone, bloat_phone], persona="Need clean stock Android with no ads", budget=budget)
    assert scored[0]["phone"].name == "Motorola Edge 50 Fusion"
    assert any("Clean" in r for r in scored[0]["match_reasons"])
    assert any("Ad-Supported" in t or "Promotional" in t for t in scored[1]["trade_offs"])


# ── TEST CASE 6: Knowledge Graph Defect & Thermal Shielding ───────────────────
def test_case_6_knowledge_graph_defect_shielding():
    phones = [
        PhoneDetails(id=50, name="Safe Modern Phone", brand="OnePlus", price=32000.0, launch_year=2025),
        PhoneDetails(id=51, name="Poco X3 Pro", brand="Poco", price=18000.0, launch_year=2021),  # Known motherboard dead issue
    ]
    safe = filter_by_knowledge_graph(phones)
    assert len(safe) == 1
    assert safe[0].name == "Safe Modern Phone"


# ── TEST CASE 7: Brand Diversity Enforcement (Max 2 per Brand) ────────────────
def test_case_7_brand_diversity_enforcement():
    # 8 Samsung devices and 3 alternatives
    recs = [
        {"phone": PhoneDetails(id=i, name=f"Samsung Galaxy {i}", brand="Samsung", price=30000.0), "score": 95.0 - i}
        for i in range(1, 9)
    ]
    recs.append({"phone": PhoneDetails(id=20, name="OnePlus 12R", brand="OnePlus", price=30000.0), "score": 85.0})
    recs.append({"phone": PhoneDetails(id=21, name="Motorola Edge 50", brand="Motorola", price=30000.0), "score": 84.0})
    recs.append({"phone": PhoneDetails(id=22, name="Vivo V40 Pro", brand="Vivo", price=30000.0), "score": 83.0})

    diverse = _enforce_brand_diversity(recs)
    assert len(diverse) == 5
    samsung_count = sum(1 for item in diverse if item["phone"].brand.lower() == "samsung")
    assert samsung_count <= 2  # Max 2 from any single brand


# ── TEST CASE 8: 100% Battery Priority Slider (Medium Mode) ───────────────────
def test_case_8_battery_slider_priority_extreme():
    budget = 25000.0
    big_battery_phone = PhoneDetails(
        id=60,
        name="Monster Battery 7000mAh",
        brand="Samsung",
        price=21999.0,
        price_numeric=21999.0,
        launch_year=2025,
        raw_specs={"battery": "7000mAh 45W", "chipset": "Snapdragon 6 Gen 1"}
    )
    speed_phone = PhoneDetails(
        id=61,
        name="Speedy Compact 4500mAh",
        brand="Realme",
        price=22999.0,
        price_numeric=22999.0,
        launch_year=2025,
        raw_specs={"battery": "4500mAh 33W", "chipset": "Snapdragon 7+ Gen 3"}
    )
    scored = ml_score_phones(
        [big_battery_phone, speed_phone],
        persona="General",
        budget=budget,
        weight_overrides={"battery": 1.0, "performance": 0.0, "camera": 0.0, "display": 0.0, "build": 0.0}
    )
    assert scored[0]["phone"].name == "Monster Battery 7000mAh"
    assert scored[0]["score"] > scored[1]["score"]


# ── TEST CASE 9: 100% Performance Priority Slider (Medium Mode) ───────────────
def test_case_9_performance_slider_priority_extreme():
    budget = 30000.0
    speed_phone = PhoneDetails(
        id=70,
        name="Turbo Silicon Dimensity 8300",
        brand="Poco",
        price=27999.0,
        price_numeric=27999.0,
        launch_year=2025,
        raw_specs={"chipset": "Dimensity 8300 Ultra", "battery": "5000mAh"}
    )
    camera_phone = PhoneDetails(
        id=71,
        name="Mid Optics Low Silicon",
        brand="Vivo",
        price=28999.0,
        price_numeric=28999.0,
        launch_year=2025,
        raw_specs={"chipset": "Snapdragon 4 Gen 2", "camera": "50MP OIS"}
    )
    scored = ml_score_phones(
        [speed_phone, camera_phone],
        persona="General",
        budget=budget,
        weight_overrides={"performance": 1.0, "battery": 0.0, "camera": 0.0, "display": 0.0, "build": 0.0}
    )
    assert scored[0]["phone"].name == "Turbo Silicon Dimensity 8300"
    assert scored[0]["score"] > scored[1]["score"]


# ── TEST CASE 10: Hardware Cosine Similarity Invariance ───────────────────────
def test_case_10_hardware_similarity_invariance():
    target = PhoneDetails(
        id=80,
        name="Samsung Galaxy S26 Ultra",
        brand="Samsung",
        price=134999.0,
        price_numeric=134999.0,
        launch_year=2026,
        raw_specs={"chipset": "Snapdragon 8 Elite", "camera": "200MP", "display": "120Hz LTPO", "battery": "5000mAh"}
    )
    query_vec = normalize_hardware_vector(target)
    assert abs(np.linalg.norm(query_vec) - 1.0) < 0.001

    similar = find_similar_phones(query_vec, top_k=5, max_budget=150000.0, exclude_ids=[target.id])
    assert len(similar) > 0
    for s in similar:
        assert s["id"] != target.id
        assert 0.0 <= s["similarity_score"] <= 1.0
        assert "brand" in s
        assert "name" in s
        assert "price" in s


# ── TEST CASE 11: Pattern 2 Gated ABSA Sentiment Modulation ────────────────────
def test_case_11_gated_absa_sentiment_modulation():
    phone_pos = PhoneDetails(
        id=90,
        name="Optics Review Praised",
        brand="Vivo",
        price=45000.0,
        price_numeric=45000.0,
        launch_year=2025,
        raw_specs={"camera": "50MP telephoto", "chipset": "Dimensity 8300"}
    )
    phone_neg = PhoneDetails(
        id=91,
        name="Optics Review Criticized",
        brand="Vivo",
        price=45000.0,
        price_numeric=45000.0,
        launch_year=2025,
        raw_specs={"camera": "50MP telephoto", "chipset": "Dimensity 8300"}
    )

    def mock_fetch(name):
        if "Praised" in name:
            return {"camera": 0.50, "performance": 0.0, "battery": 0.0, "display": 0.0, "build": 0.0}
        elif "Criticized" in name:
            return {"camera": -0.50, "performance": 0.0, "battery": 0.0, "display": 0.0, "build": 0.0}
        return {"camera": 0.0, "performance": 0.0, "battery": 0.0, "display": 0.0, "build": 0.0}

    with patch("app.services.recommender.fetch_live_sentiment", side_effect=mock_fetch):
        scored = ml_score_phones([phone_pos, phone_neg], persona="Photography", budget=50000.0)
        assert len(scored) == 2
        assert scored[0]["phone"].name == "Optics Review Praised"
        assert scored[0]["score"] > scored[1]["score"]
        assert any("Reviewer Acclaim" in r for r in scored[0]["match_reasons"])
        assert any("Reviewer Caution" in t for t in scored[1]["trade_offs"])


# ── TEST CASE 12: Outdated Flagship Lifecycle Degradation ─────────────────────
def test_case_12_outdated_flagship_lifecycle_penalty():
    old_flagship = PhoneDetails(
        id=100,
        name="Old 2024 Expensive Flagship",
        brand="Samsung",
        price=75000.0,
        price_numeric=75000.0,
        launch_year=2024,
        raw_specs={"chipset": "Snapdragon 8 Gen 2", "camera": "50MP"}
    )
    new_subflagship = PhoneDetails(
        id=101,
        name="New 2025 Sub-Flagship",
        brand="OnePlus",
        price=65000.0,
        price_numeric=65000.0,
        launch_year=2025,
        raw_specs={"chipset": "Snapdragon 8s Gen 3", "camera": "50MP"}
    )
    scored = ml_score_phones([old_flagship, new_subflagship], persona="General", budget=80000.0)
    assert len(scored) == 2
    assert scored[0]["phone"].name == "New 2025 Sub-Flagship"
    assert any("2024" in t or "lifecycle" in t.lower() or "aging" in t.lower() for t in scored[1]["trade_offs"])


# ── TEST CASE 13: 25-Point Bonus Cap (Anti-Stacking Stress Test) ──────────────
def test_case_13_additive_bonus_capping_anti_stacking():
    mega_stacked = PhoneDetails(
        id=110,
        name="Hyper Stacked Feature Monster",
        brand="Google",
        price=70000.0,
        price_numeric=70000.0,
        launch_year=2026,
        is_current_catalogue=1,
        raw_specs={
            "camera": "200 mp zeiss apo dolby vision center stage 4k@120fps",
            "chipset": "Tensor G4",
            "battery": "6000mah 120w",
            "display": "165hz ltpo",
            "os": "Pixel UI (Clean)"
        }
    )
    scored = ml_score_phones([mega_stacked], persona="Creator with clean software and fast gaming", budget=75000.0)
    assert len(scored) == 1
    # Without cap, stacked bonuses would exceed 90 points pushing score > 150.
    # With calibration, score must be bounded cleanly in [50.0, 99.0].
    assert 50.0 <= scored[0]["score"] <= 99.0


# ── TEST CASE 14: Empty Budget Floor Graceful Recovery ────────────────────────
def test_case_14_empty_floor_graceful_recovery():
    # Only phones at 50% of budget exist (below tight 65% floor)
    budget = 40000.0
    sparse_phones = [
        PhoneDetails(id=120, name="Sparse Phone 1", brand="Realme", price=18000.0, price_numeric=18000.0, launch_year=2025),
        PhoneDetails(id=121, name="Sparse Phone 2", brand="Motorola", price=19000.0, price_numeric=19000.0, launch_year=2025),
    ]
    # Should fallback to wider floor [4500 to budget*1.05] instead of returning empty
    scored = ml_score_phones(sparse_phones, persona="General", budget=budget)
    assert len(scored) == 2


# ── TEST CASE 15: Malformed Specs & Corrupted Schema Resiliency ───────────────
def test_case_15_malformed_specs_and_missing_data_resilience():
    corrupted_phones = [
        PhoneDetails(id=130, name="Missing Specs Phone", brand="Unknown", price=25000.0, price_numeric=25000.0, raw_specs=None),
        PhoneDetails(id=131, name="Empty Dict Specs Phone", brand="", price="25000", price_numeric=None, raw_specs={}),
        PhoneDetails(id=132, name="Broken Types Phone", brand="Brand", price=None, price_numeric=None, raw_specs={"camera": 12345, "battery": None}),
    ]
    # Must process without throwing TypeError, ValueError, or unhandled exceptions
    scored = ml_score_phones(corrupted_phones, persona="General", budget=30000.0)
    assert isinstance(scored, list)
    for s in scored:
        assert "phone" in s
        assert "score" in s
        assert "match_reasons" in s
        assert "trade_offs" in s
        assert 50.0 <= s["score"] <= 99.0
