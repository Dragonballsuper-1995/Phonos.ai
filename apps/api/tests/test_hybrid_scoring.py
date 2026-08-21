"""
test_hybrid_scoring.py — Phase 2 Test Suite for Hybrid Scientific Benchmark Scoring
===================================================================================
Validates:
1. Hybrid Camera evaluation (DxOMark + VCX + Optic spec formula fusion).
2. Hybrid SoC evaluation (Geekbench 6 + AnTuTu v10 + Silicon index fusion).
3. Hybrid Display & Battery evaluation (DxOMark Display + GSMArena AUS hours).
4. Graceful fallbacks for unbenchmarked budget devices.
5. End-to-end recommendation scoring bounds [50.0, 99.0] and lab benchmark citations.
"""

import pytest
import numpy as np
from app.models.phone import PhoneDetails
from app.services.hardware_scorer import (
    evaluate_camera_score,
    evaluate_soc_score,
    evaluate_hybrid_camera_score,
    evaluate_hybrid_soc_score,
    evaluate_hybrid_display_score,
    evaluate_hybrid_battery_score,
    extract_hardware_spec_vector,
    normalize_hardware_vector,
)
from app.services.recommender import ml_score_phones


def test_hybrid_camera_with_dxomark():
    """Verify that a phone with a DxOMark score blends lab metrics with spec score."""
    phone_dxo = PhoneDetails(
        id=501,
        name="Vivo X200 Pro 5G",
        brand="Vivo",
        price=94999.0,
        price_numeric=94999.0,
        dxomark_camera_score=160.0,
        raw_specs={"camera": "50MP OIS periscope telephoto zeiss apo 4k120"}
    )
    base_spec = evaluate_camera_score(str(phone_dxo.raw_specs), phone_dxo.name)
    hybrid_score = evaluate_hybrid_camera_score(phone_dxo)

    # DxOMark 160/160 * 100 = 100.0 norm
    expected = (100.0 * 0.55) + (base_spec * 0.45)
    assert abs(hybrid_score - expected) < 0.01
    assert 0.0 <= hybrid_score <= 100.0


def test_hybrid_camera_with_vcx_fallback():
    """Verify that a phone with VCX score (and no DxOMark) blends VCX lab metrics."""
    phone_vcx = PhoneDetails(
        id=502,
        name="Mid-Range Camera Challenger",
        brand="Motorola",
        price=32999.0,
        price_numeric=32999.0,
        vcx_camera_score=64.0,  # 64 / 80 = 80.0%
        raw_specs={"camera": "50MP OIS 3x telephoto"}
    )
    base_spec = evaluate_camera_score(str(phone_vcx.raw_specs), phone_vcx.name)
    hybrid_score = evaluate_hybrid_camera_score(phone_vcx)

    expected = (80.0 * 0.50) + (base_spec * 0.50)
    assert abs(hybrid_score - expected) < 0.01


def test_hybrid_camera_without_benchmarks_fallback():
    """Verify that an unbenchmarked budget phone falls back 100% to rule-based spec score."""
    phone_budget = PhoneDetails(
        id=503,
        name="Budget 5G Phone",
        brand="Motorola",
        price=10999.0,
        price_numeric=10999.0,
        raw_specs={"camera": "50MP basic dual camera"}
    )
    base_spec = evaluate_camera_score(str(phone_budget.raw_specs), phone_budget.name)
    hybrid_score = evaluate_hybrid_camera_score(phone_budget)

    assert hybrid_score == base_spec


def test_hybrid_soc_with_geekbench():
    """Verify Geekbench 6 multi-core compute fusion."""
    phone_flagship = PhoneDetails(
        id=504,
        name="OnePlus 13 5G",
        brand="OnePlus",
        price=69999.0,
        price_numeric=69999.0,
        geekbench_multi=9500,  # 9500 / 9500 = 100.0%
        raw_specs={"chipset": "Snapdragon 8 Elite"}
    )
    base_spec = evaluate_soc_score(str(phone_flagship.raw_specs))
    hybrid_score = evaluate_hybrid_soc_score(phone_flagship)

    expected = (100.0 * 0.55) + (base_spec * 0.45)
    assert abs(hybrid_score - expected) < 0.01


def test_hybrid_soc_with_antutu_fallback():
    """Verify AnTuTu v10 benchmark fusion when Geekbench is absent."""
    phone_mid = PhoneDetails(
        id=505,
        name="iQOO Neo 9 Pro",
        brand="iQOO",
        price=34999.0,
        price_numeric=34999.0,
        antutu_v10_score=1500000,  # 1.5M / 3.0M = 50.0%
        raw_specs={"chipset": "Snapdragon 8 Gen 2"}
    )
    base_spec = evaluate_soc_score(str(phone_mid.raw_specs))
    hybrid_score = evaluate_hybrid_soc_score(phone_mid)

    expected = (50.0 * 0.50) + (base_spec * 0.50)
    assert abs(hybrid_score - expected) < 0.01


def test_hybrid_display_and_battery():
    """Verify Display (DxOMark) and Battery (GSMArena Active Use Hours) fusion."""
    phone = PhoneDetails(
        id=506,
        name="Samsung Galaxy S24 Ultra",
        brand="Samsung",
        price=129999.0,
        price_numeric=129999.0,
        dxomark_display_score=155.0,
        gsmarena_battery_hours=16.7,
        raw_specs={
            "display": "Dynamic AMOLED 2X 120Hz LTPO 2600 nits QHD+",
            "battery": "5000 mAh 45W"
        }
    )

    disp_hybrid = evaluate_hybrid_display_score(phone)
    bat_hybrid = evaluate_hybrid_battery_score(phone)

    assert 0.0 <= disp_hybrid <= 100.0
    assert 0.0 <= bat_hybrid <= 100.0


def test_extract_hardware_spec_vector_bounds():
    """Verify all 5 dimensions of hardware vector are bounded in [0.0, 100.0]."""
    phone = PhoneDetails(
        id=507,
        name="Apple iPhone 16 Pro Max",
        brand="Apple",
        price=144900.0,
        price_numeric=144900.0,
        dxomark_camera_score=157.0,
        dxomark_display_score=159.0,
        geekbench_multi=8620,
        gsmarena_battery_hours=17.5,
        raw_specs={
            "chipset": "Apple A18 Pro",
            "camera": "48MP OIS 5x periscope telephoto 4K120 Dolby Vision",
            "display": "Super Retina XDR OLED 120Hz Promotion 2000 nits",
            "battery": "4685 mAh",
            "build": "IP68 grade 5 titanium ceramic shield"
        }
    )

    vec = extract_hardware_spec_vector(phone)
    for dim, val in vec.items():
        assert 0.0 <= val <= 100.0, f"Dimension {dim} value {val} out of bounds"


def test_recommender_benchmark_lab_citations():
    """Verify that phones with lab benchmarks include lab citations in recommendation reasons."""
    benchmarked_phone = PhoneDetails(
        id=508,
        name="Vivo X200 Pro 5G",
        brand="Vivo",
        price=94999.0,
        price_numeric=94999.0,
        launch_year=2025,
        dxomark_camera_score=160.0,
        geekbench_multi=9100,
        gsmarena_battery_hours=17.8,
        raw_specs={"chipset": "Dimensity 9400", "camera": "50MP ZEISS 200MP APO", "display": "120Hz AMOLED"}
    )

    scored = ml_score_phones([benchmarked_phone], persona="Photography", budget=100000.0)
    assert len(scored) == 1
    reasons = scored[0]["match_reasons"]

    # Verify presence of lab citations
    assert any("DxOMark Lab Certified" in r for r in reasons)
    assert any("Geekbench 6 Flagship Compute" in r for r in reasons)
    assert any("GSMArena Lab Verified" in r for r in reasons)
    assert 50.0 <= scored[0]["score"] <= 99.0
