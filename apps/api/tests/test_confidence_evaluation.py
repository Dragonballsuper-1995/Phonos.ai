import pytest
import numpy as np
from app.models.phone import PhoneDetails
from app.services.confidence_evaluator import (
    compute_recommendation_confidence,
    compute_ece_and_calibration,
    compute_brand_diversity_index,
    compute_persona_congruency_index,
    compute_spec_grounding_fidelity,
    is_phone_phantom_or_excluded
)

def test_phantom_device_detection():
    assert is_phone_phantom_or_excluded("Xiaomi 18 Ultra 5G") is True
    assert is_phone_phantom_or_excluded("Samsung Galaxy S27 Ultra") is True
    assert is_phone_phantom_or_excluded("Vivo X300 Ultra") is True
    assert is_phone_phantom_or_excluded("iQOO Z11 Turbo Pro") is True
    assert is_phone_phantom_or_excluded("Samsung Galaxy S25 5G") is False
    assert is_phone_phantom_or_excluded("iQOO 13") is False

def test_spec_grounding_fidelity():
    phone = PhoneDetails(
        id=1,
        name="iQOO 13 5G",
        brand="iQOO",
        price=54999.0,
        price_numeric=54999.0,
        launch_year=2025,
        raw_specs={"chipset": "Snapdragon 8 Elite", "display": "144Hz AMOLED", "battery": "6000 mAh"}
    )
    
    valid_reasons = [
        "Dedicated Gaming Silicon: Snapdragon 8 Elite high performance",
        "Ultra-High Refresh Panel: 144Hz display",
        "Massive Battery Reserve: 6000 mAh stamina"
    ]
    fidelity = compute_spec_grounding_fidelity(phone, valid_reasons)
    assert fidelity == 1.0

def test_confidence_budget_compliance():
    # Compliant phone
    phone_ok = PhoneDetails(
        id=10,
        name="Realme GT 6",
        brand="realme",
        price=32000.0,
        price_numeric=32000.0,
        launch_year=2025,
        is_current_catalogue=1,
        raw_specs={"chipset": "Snapdragon 8s Gen 3", "battery": "5500mAh", "display": "120Hz LTPO"}
    )
    item_ok = {
        "phone": phone_ok,
        "score": 90.0,
        "match_reasons": ["Allocates 91% of Rs. 35,000 budget with tier-1 specifications"],
        "trade_offs": [],
        "ai_verified": True
    }
    conf_ok = compute_recommendation_confidence(item_ok, persona="Student", budget=35000.0)
    assert conf_ok["confidence_score"] >= 0.85
    assert conf_ok["pillars"]["constraint_validity"] >= 0.90
    assert "High" in conf_ok["grade"]

    # Overbudget phone (>105%)
    phone_over = PhoneDetails(
        id=11,
        name="Overbudget Phone",
        brand="BrandX",
        price=45000.0,
        price_numeric=45000.0,
        launch_year=2025
    )
    item_over = {
        "phone": phone_over,
        "score": 50.0,
        "match_reasons": [],
        "trade_offs": [],
        "ai_verified": False
    }
    conf_over = compute_recommendation_confidence(item_over, persona="Student", budget=35000.0)
    # Pillar 1 must be 0.0 for hard budget failure
    assert conf_over["pillars"]["constraint_validity"] == 0.0
    assert conf_over["confidence_score"] < 0.70

def test_confidence_persona_hardware_fit():
    # Gaming phone with Snapdragon 8 Elite
    gamer_phone = PhoneDetails(
        id=20,
        name="iQOO 13 Beast",
        brand="iQOO",
        price=54000.0,
        price_numeric=54000.0,
        launch_year=2025,
        is_current_catalogue=1,
        raw_specs={"chipset": "Snapdragon 8 Elite", "display": "144Hz 2K AMOLED"}
    )
    item_gamer = {
        "phone": gamer_phone,
        "score": 95.0,
        "match_reasons": ["Dedicated Gaming Silicon: Snapdragon 8 Elite"],
        "trade_offs": [],
        "ai_verified": True
    }
    conf_gamer = compute_recommendation_confidence(item_gamer, persona="Gamer", budget=60000.0)
    assert conf_gamer["pillars"]["persona_hardware_fit"] >= 0.95

    # Creator phone with Zeiss 200MP
    creator_phone = PhoneDetails(
        id=21,
        name="Vivo X200 Pro Optics",
        brand="Vivo",
        price=85000.0,
        price_numeric=85000.0,
        launch_year=2025,
        is_current_catalogue=1,
        raw_specs={"camera": "50MP OIS ZEISS 200MP APO telephoto 4K120", "display": "120Hz LTPO"}
    )
    item_creator = {
        "phone": creator_phone,
        "score": 96.0,
        "match_reasons": ["ZEISS APO 200MP Telephoto: Flagship portrait clarity"],
        "trade_offs": [],
        "ai_verified": True
    }
    conf_creator = compute_recommendation_confidence(item_creator, persona="Photography & Video Creator", budget=90000.0)
    assert conf_creator["pillars"]["persona_hardware_fit"] >= 0.90

def test_ece_and_calibration_calculation():
    # 1. Perfectly calibrated predictions: confidences = [0.9, 0.9, 0.9, 0.9, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
    # where 90% bin has 90% accuracy and 10% bin has 10% accuracy
    confidences = [0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.9]
    # 9 out of 10 for 0.9, 0 out of 10 for 0.1
    outcomes =    [True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False, False, False, False]
    
    cal_res = compute_ece_and_calibration(confidences, outcomes, n_bins=5)
    assert "ece" in cal_res
    assert "mce" in cal_res
    assert "brier_score" in cal_res
    assert cal_res["ece"] <= 0.15
    assert cal_res["brier_score"] >= 0.0

def test_brand_diversity_entropy():
    # Top 5 with diverse brands (3 brands)
    diverse_recs = [
        {"phone": PhoneDetails(id=1, name="Poco F6", brand="Poco")},
        {"phone": PhoneDetails(id=2, name="iQOO Neo 10", brand="iQOO")},
        {"phone": PhoneDetails(id=3, name="Realme GT 6", brand="realme")},
        {"phone": PhoneDetails(id=4, name="Realme P2 Pro", brand="realme")},
        {"phone": PhoneDetails(id=5, name="iQOO Z9s", brand="iQOO")}
    ]
    div_metrics = compute_brand_diversity_index(diverse_recs)
    assert div_metrics["unique_brands"] == 3
    assert div_metrics["max_brand_share"] == 0.40  # 2 out of 5 = 40%
    assert div_metrics["shannon_entropy"] > 1.0

def test_persona_congruency_index():
    gamer_phones = [
        {"phone": PhoneDetails(id=1, name="iQOO 13", brand="iQOO", raw_specs={"chipset": "Snapdragon 8 Elite", "display": "144Hz AMOLED"})},
        {"phone": PhoneDetails(id=2, name="Realme GT 7 Pro", brand="realme", raw_specs={"chipset": "Snapdragon 8 Elite", "display": "120Hz OLED"})}
    ]
    pci_gamer = compute_persona_congruency_index(gamer_phones, "Gamer")
    assert pci_gamer >= 0.85
