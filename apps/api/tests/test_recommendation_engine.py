import pytest
import asyncio
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
