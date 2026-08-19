import pytest
import asyncio
import numpy as np
from app.models.phone import PhoneDetails
from app.models.query import EasyRecommendRequest, MediumRecommendRequest, DeepRecommendRequest
from app.services.hardware_scorer import evaluate_soc_score, evaluate_camera_score, evaluate_display_score, evaluate_battery_charge_score, evaluate_build_score, extract_hardware_spec_vector
from app.services.recommender import recommend_easy, recommend_medium, recommend_deep, ml_score_phones
from app.routers.recommend import _enforce_brand_diversity
from app.core.constants import SOFTWARE_UI_TAXONOMY, LINEUP_DNA_HIERARCHY, PERSONA_WEIGHTS

def test_hardware_scorer_soc_matrix():
    # Flagship processors
    assert evaluate_soc_score("Powered by Snapdragon 8 Elite chipset") == 100.0
    assert evaluate_soc_score("MediaTek Dimensity 9400 processor") == 98.0
    assert evaluate_soc_score("Apple A18 Pro Bionic") == 98.0
    assert evaluate_soc_score("Qualcomm Snapdragon 8 Gen 3") == 92.0
    assert evaluate_soc_score("Snapdragon 8s Gen 3 Mobile Platform") == 85.0
    assert evaluate_soc_score("Dimensity 8300 Ultra processor") == 83.0
    assert evaluate_soc_score("Snapdragon 7+ Gen 3") == 81.0
    
    # Mid-range and budget processors
    assert evaluate_soc_score("Snapdragon 7 Gen 3") == 70.0
    assert evaluate_soc_score("Dimensity 7300 Energy") == 69.0
    assert evaluate_soc_score("Snapdragon 6 Gen 1") == 55.0
    assert evaluate_soc_score("Dimensity 6300") == 50.0
    assert evaluate_soc_score("Helio G99") == 38.0

def test_hardware_scorer_camera_matrix():
    score_ois_tele = evaluate_camera_score("50MP OIS main camera with 3x periscope optical zoom, Zeiss T* coating, 4K@60fps video", "Vivo X200 Pro")
    assert score_ois_tele >= 90.0
    
    score_basic = evaluate_camera_score("50MP dual rear camera, 1080p video", "Budget Phone")
    assert score_basic < 55.0

def test_hardware_scorer_display_and_battery():
    disp_score = evaluate_display_score("6.78-inch 1.5K LTPO AMOLED display with 144Hz refresh rate, 4500 nits peak brightness")
    assert disp_score >= 90.0
    
    batt_score = evaluate_battery_charge_score("6000mAh battery with 120W fast charging and wireless charging support")
    assert batt_score >= 95.0

def test_brand_diversity_enforcement():
    dummy_phones = [
        {"phone": PhoneDetails(id=1, name="Realme GT 6 (12GB RAM)", brand="realme", price=32999.0, price_numeric=32999.0), "score": 95.0},
        {"phone": PhoneDetails(id=2, name="Realme GT 6 (8GB RAM)", brand="realme", price=28999.0, price_numeric=28999.0), "score": 94.0},
        {"phone": PhoneDetails(id=3, name="Realme GT 6T", brand="realme", price=29440.0, price_numeric=29440.0), "score": 93.0},
        {"phone": PhoneDetails(id=4, name="Poco F6 5G", brand="Poco", price=27490.0, price_numeric=27490.0), "score": 92.0},
        {"phone": PhoneDetails(id=5, name="iQOO Neo 10", brand="iQOO", price=31998.0, price_numeric=31998.0), "score": 91.0},
        {"phone": PhoneDetails(id=6, name="Realme 13 Pro+", brand="realme", price=31999.0, price_numeric=31999.0), "score": 90.0},
    ]
    
    diverse = _enforce_brand_diversity(dummy_phones)
    
    # Check max 2 per brand
    realme_count = sum(1 for item in diverse if item["phone"].brand == "realme")
    assert realme_count <= 2
    
    # Check deduplication of base name variants
    names = [item["phone"].name for item in diverse]
    assert len(names) == len(set(names))

def test_clean_ui_software_scoring():
    moto_phone = PhoneDetails(id=10, name="Motorola Edge 60 Pro", brand="Motorola", price=30799.0, price_numeric=30799.0, launch_year=2025, raw_specs={"display": "144Hz OLED", "os": "Hello UI"})
    ad_phone = PhoneDetails(id=11, name="Custom Skin Phone", brand="Tecno", price=30799.0, price_numeric=30799.0, launch_year=2025, raw_specs={"display": "120Hz LCD", "os": "HiOS"})
    
    scored = ml_score_phones([moto_phone, ad_phone], persona="Clean stock Android UI with no ads", budget=40000)
    assert len(scored) == 2
    # Motorola with Hello UI should strongly beat ad-supported skin for clean UI seekers
    assert scored[0]["phone"].name == "Motorola Edge 60 Pro"
    assert scored[0]["score"] > scored[1]["score"]

def test_feature_extraction_canonical_schema():
    from app.services.recommender import extract_features, FEATURE_COLS, MAX_PRICE_NORM
    phone = PhoneDetails(
        id=20,
        name="iQOO 13 5G",
        brand="iQOO",
        price=54999.0,
        price_numeric=54999.0,
        launch_year=2025,
        raw_specs={"chipset": "Snapdragon 8 Elite", "ram": "16GB RAM", "battery": "6000 mAh", "display": "144Hz 2K AMOLED"}
    )
    feats = extract_features(phone, persona_idx=1, budget=60000.0)
    assert len(feats) == len(FEATURE_COLS) == 7
    # Check bounds
    assert feats[0] == 1.0  # Gamer persona
    assert 0.0 <= feats[1] <= 1.05  # budget_ratio
    assert 0.0 <= feats[2] <= 1.0   # price_ratio
    assert 0.0 <= feats[3] <= 1.0   # battery_norm
    assert 0.0 <= feats[4] <= 1.0   # ram_norm
    assert 0.0 <= feats[5] <= 1.0   # hz_norm
    assert feats[6] == 1.0          # perf_tier for Snapdragon 8 Elite

def test_medium_mode_slider_weight_overrides():
    cam_heavy_phone = PhoneDetails(
        id=31,
        name="Vivo X200 Pro Optics",
        brand="Vivo",
        price=48000.0,
        price_numeric=48000.0,
        launch_year=2025,
        raw_specs={"camera": "50MP OIS ZEISS 200MP APO telephoto 4K120", "chipset": "Dimensity 8300", "battery": "5000mAh", "display": "120Hz"}
    )
    perf_heavy_phone = PhoneDetails(
        id=32,
        name="iQOO Neo 10 Turbo Gaming",
        brand="iQOO",
        price=48000.0,
        price_numeric=48000.0,
        launch_year=2025,
        raw_specs={"chipset": "Snapdragon 8 Elite", "display": "144Hz OLED", "camera": "50MP basic", "battery": "6500mAh 120W"}
    )

    # 1. Camera-heavy request
    scored_cam = ml_score_phones(
        [cam_heavy_phone, perf_heavy_phone],
        persona="General",
        budget=50000.0,
        weight_overrides={"camera": 0.80, "performance": 0.10, "battery": 0.05, "display": 0.05}
    )
    assert scored_cam[0]["phone"].name == "Vivo X200 Pro Optics"

    # 2. Performance-heavy request
    scored_perf = ml_score_phones(
        [cam_heavy_phone, perf_heavy_phone],
        persona="General",
        budget=50000.0,
        weight_overrides={"performance": 0.80, "camera": 0.05, "battery": 0.05, "display": 0.10}
    )
    assert scored_perf[0]["phone"].name == "iQOO Neo 10 Turbo Gaming"

def test_score_bonus_capping():
    # Phone with massive keyword stacking (Year 2026 + Catalogue + ZEISS 200MP + Dolby Vision + Center Stage + Clean UI)
    stacked_phone = PhoneDetails(
        id=99,
        name="Ultra Stacked Flagship 2026",
        brand="Google",
        price=75000.0,
        price_numeric=75000.0,
        launch_year=2026,
        is_current_catalogue=1,
        raw_specs={
            "camera": "200 mp zeiss apo dolby vision center stage 4k@120fps",
            "chipset": "Tensor G4",
            "battery": "5000mAh",
            "display": "120Hz LTPO",
            "os": "Pixel UI (Stock)"
        }
    )

    scored = ml_score_phones(
        [stacked_phone],
        persona="Camera creator with clean stock OS",
        budget=80000.0
    )
    assert len(scored) == 1
    # Raw stacked bonuses would have exceeded 85 points.
    # Score must be bounded properly:
    assert 50.0 <= scored[0]["score"] <= 99.0

def test_normalize_hardware_vector():
    from app.services.hardware_scorer import normalize_hardware_vector
    phone = PhoneDetails(
        id=101,
        name="Samsung Galaxy S26 Ultra",
        brand="Samsung",
        price=134999.0,
        price_numeric=134999.0,
        launch_year=2026,
        raw_specs={
            "chipset": "Snapdragon 8 Elite",
            "camera": "200 MP OIS periscope telephoto 4K@120fps",
            "display": "6.8 inch 120Hz LTPO AMOLED 3000 nits",
            "battery": "5000 mAh 45W",
            "build": "IP68 titanium frame victus glass"
        }
    )
    vec = normalize_hardware_vector(phone)
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (5,)
    assert vec.dtype == np.float32
    norm = np.linalg.norm(vec)
    assert abs(norm - 1.0) < 0.001

def test_hardware_similarity_search():
    from app.services.hardware_similarity import find_similar_phones, build_persona_query_vector
    from app.services.hardware_scorer import normalize_hardware_vector

    sample_phone = PhoneDetails(
        id=102,
        name="Flagship Camera Device",
        brand="Vivo",
        price=79999.0,
        price_numeric=79999.0,
        launch_year=2025,
        raw_specs={"chipset": "Dimensity 9400", "camera": "50MP ZEISS 200MP APO telephoto", "display": "144Hz OLED"}
    )
    query_vec = normalize_hardware_vector(sample_phone)
    similar = find_similar_phones(query_vec, top_k=5, max_budget=150000.0)
    assert len(similar) > 0
    assert "similarity_score" in similar[0]
    assert 0.0 <= similar[0]["similarity_score"] <= 1.0
    assert "name" in similar[0]
    assert "price" in similar[0]

def test_build_persona_query_vector():
    from app.services.hardware_similarity import build_persona_query_vector
    gamer_weights = {"performance": 0.35, "camera": 0.10, "display": 0.25, "battery": 0.20, "build": 0.10}
    vec = build_persona_query_vector(gamer_weights)
    assert vec.shape == (5,)
    assert abs(np.linalg.norm(vec) - 1.0) < 0.001

@pytest.mark.asyncio
async def test_similar_phones_api_endpoint():
    from httpx import AsyncClient, ASGITransport
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/phones/Samsung%20Galaxy%20S26%20Edge/similar?top_k=3")
    assert response.status_code == 200
    data = response.json()
    assert "source" in data
    assert "similar_phones" in data
    assert len(data["similar_phones"]) <= 3
    if len(data["similar_phones"]) > 0:
        first = data["similar_phones"][0]
        assert "name" in first
        assert "similarity_score" in first
        assert "price" in first

def test_absa_columns_and_sentiment_lookup():
    import sqlite3
    from app.services.youtube_sentiment import fetch_live_sentiment, DB_PATH

    conn = sqlite3.connect(DB_PATH)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(phones)").fetchall()]
    conn.close()

    for aspect in ["camera", "battery", "performance", "display", "build", "updated_at"]:
        assert f"absa_{aspect}" in cols, f"Missing column absa_{aspect} in phones table"

    # Test sentiment fetch function
    sent = fetch_live_sentiment("Samsung Galaxy A57")
    assert isinstance(sent, dict)
    assert "camera" in sent
    assert "battery" in sent
    assert "performance" in sent
    assert "display" in sent
    assert "build" in sent

def test_rlhf_event_conversion_and_features():
    from scripts.retrain_from_rlhf import events_to_training_data
    from app.services.recommender import FEATURE_COLS

    mock_phone = PhoneDetails(
        id=201,
        name="OnePlus 13",
        brand="OnePlus",
        price=69999.0,
        price_numeric=69999.0,
        launch_year=2025,
        raw_specs={"chipset": "Snapdragon 8 Elite", "ram": "16GB RAM", "battery": "6000mAh", "display": "120Hz LTPO"}
    )
    phone_lookup = {"oneplus 13": mock_phone}

    mock_events = [
        {
            "event": "buy_clicked",
            "properties": {
                "phone_name": "OnePlus 13",
                "persona": "Gamer",
                "budget": 75000.0,
                "ai_rank": 1
            }
        },
        {
            "event": "phone_rejected",
            "properties": {
                "phone_name": "OnePlus 13",
                "persona": "Student",
                "budget": 20000.0,
                "ai_rank": 5
            }
        }
    ]

    X, y = events_to_training_data(mock_events, phone_lookup)
    assert len(X) == 2
    assert len(y) == 2
    assert y == [1, 0]  # buy_clicked = 1, phone_rejected = 0
    assert len(X[0]) == len(FEATURE_COLS) == 7
    assert len(X[1]) == len(FEATURE_COLS) == 7

def test_recommend_easy_persona_weighted_retrieval():
    phones = [
        PhoneDetails(
            id=301,
            name="Gaming Beast 144Hz",
            brand="iQOO",
            price=42000.0,
            price_numeric=42000.0,
            launch_year=2025,
            raw_specs={"chipset": "Snapdragon 8 Elite", "display": "144Hz OLED", "ram": "16GB RAM"}
        ),
        PhoneDetails(
            id=302,
            name="Camera Flagship Pro",
            brand="Vivo",
            price=44000.0,
            price_numeric=44000.0,
            launch_year=2025,
            raw_specs={"chipset": "Dimensity 8300", "camera": "50MP ZEISS 200MP APO telephoto 4K120", "display": "120Hz"}
        )
    ]
    req_gamer = EasyRecommendRequest(persona="Gamer", budget=45000.0)
    results_gamer = recommend_easy(phones, req_gamer)
    assert len(results_gamer) == 2
    # Gaming phone should be top ranked for Gamer persona
    assert results_gamer[0]["phone"].name == "Gaming Beast 144Hz"

    req_camera = EasyRecommendRequest(persona="Photography", budget=45000.0)
    results_camera = recommend_easy(phones, req_camera)
    assert len(results_camera) == 2
    # Camera phone should be top ranked for Photography persona
    assert results_camera[0]["phone"].name == "Camera Flagship Pro"

def test_gated_sentiment_modulation():
    from unittest.mock import patch

    phone_a = PhoneDetails(
        id=401,
        name="Optics Beast Positive Reviews",
        brand="Vivo",
        price=55000.0,
        price_numeric=55000.0,
        launch_year=2025,
        raw_specs={"camera": "50MP periscope telephoto", "chipset": "Dimensity 9300"}
    )
    phone_b = PhoneDetails(
        id=402,
        name="Optics Beast Negative Reviews",
        brand="Vivo",
        price=55000.0,
        price_numeric=55000.0,
        launch_year=2025,
        raw_specs={"camera": "50MP periscope telephoto", "chipset": "Dimensity 9300"}
    )

    # Mock fetch_live_sentiment to return positive sentiment for phone A and negative for phone B
    def mock_fetch(name):
        if "Positive" in name:
            return {"camera": 0.40, "performance": 0.0, "battery": 0.0, "display": 0.0, "build": 0.0}
        elif "Negative" in name:
            return {"camera": -0.40, "performance": 0.0, "battery": 0.0, "display": 0.0, "build": 0.0}
        return {"camera": 0.0, "performance": 0.0, "battery": 0.0, "display": 0.0, "build": 0.0}

    with patch("app.services.recommender.fetch_live_sentiment", side_effect=mock_fetch):
        scored = ml_score_phones([phone_a, phone_b], persona="Photography", budget=60000.0)
        assert len(scored) == 2
        # Positively reviewed camera phone should score strictly higher than identical phone with negative review sentiment
        assert scored[0]["phone"].name == "Optics Beast Positive Reviews"
        assert scored[0]["score"] > scored[1]["score"]
        # Check reasons / trade-offs
        assert any("Reviewer Acclaim" in r for r in scored[0]["match_reasons"])
        assert any("Reviewer Caution" in t for t in scored[1]["trade_offs"])








