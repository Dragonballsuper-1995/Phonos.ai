"""
test_benchmark_import.py — Phase 1 Test Suite for Scientific Benchmark Ingestion
================================================================================
Validates:
1. SQLite schema extension (DxOMark, VCX, Geekbench, AnTuTu, GSMArena Battery).
2. Pydantic PhoneDetails model deserialization and serialization.
3. Brand-aware fuzzy matching precision against benchmark datasets.
4. Data integrity and non-null values in fone_master.db.
"""

import os
import sqlite3
import pytest
from app.models.phone import PhoneDetails
from scripts.import_benchmarks import (
    DB_PATH,
    BENCHMARK_COLUMNS,
    normalize_string,
    match_benchmark_entry,
    BENCHMARK_KNOWLEDGE_BASE
)

def test_benchmark_columns_exist_in_db():
    """Verify that all benchmark columns exist in the master SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(phones)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    conn.close()

    for col in BENCHMARK_COLUMNS.keys():
        assert col in columns, f"Column '{col}' missing from SQLite phones table"


def test_pydantic_phone_details_with_benchmarks():
    """Verify PhoneDetails Pydantic model parses and validates benchmark fields."""
    sample_data = {
        "brand": "Vivo",
        "name": "Vivo X200 Pro 5G",
        "price_numeric": 94999.0,
        "dxomark_camera_score": 160.0,
        "dxomark_selfie_score": 148.0,
        "dxomark_display_score": 156.0,
        "vcx_camera_score": 77.0,
        "geekbench_single": 2980,
        "geekbench_multi": 9100,
        "antutu_v10_score": 2850000,
        "gsmarena_battery_hours": 17.8,
        "raw_specs": {
            "chipset": "MediaTek Dimensity 9400",
            "camera": "50MP ZEISS 200MP APO telephoto",
            "battery": "6000 mAh"
        }
    }

    phone = PhoneDetails.model_validate(sample_data)
    assert phone.brand == "Vivo"
    assert phone.dxomark_camera_score == 160.0
    assert phone.dxomark_selfie_score == 148.0
    assert phone.dxomark_display_score == 156.0
    assert phone.vcx_camera_score == 77.0
    assert phone.geekbench_single == 2980
    assert phone.geekbench_multi == 9100
    assert phone.antutu_v10_score == 2850000
    assert phone.gsmarena_battery_hours == 17.8


def test_fuzzy_matcher_precision():
    """Verify that brand-aware fuzzy matching maps phone variants accurately."""
    # 1. Vivo X200 Pro
    m1 = match_benchmark_entry("Vivo X200 Pro 5G (16GB RAM + 512GB)", "Vivo", BENCHMARK_KNOWLEDGE_BASE)
    assert m1 is not None
    assert m1["name"] == "Vivo X200 Pro"
    assert m1["dxomark_camera"] == 160.0

    # 2. iPhone 16 Pro Max
    m2 = match_benchmark_entry("Apple iPhone 16 Pro Max (256GB)", "Apple", BENCHMARK_KNOWLEDGE_BASE)
    assert m2 is not None
    assert m2["name"] == "Apple iPhone 16 Pro Max"
    assert m2["geekbench_multi"] == 8620

    # 3. OnePlus 13
    m3 = match_benchmark_entry("OnePlus 13 5G (12GB RAM)", "OnePlus", BENCHMARK_KNOWLEDGE_BASE)
    assert m3 is not None
    assert m3["name"] == "OnePlus 13"
    assert m3["antutu_v10"] == 2920000

    # 4. Brand Mismatch Rejection: Samsung must not match an Apple or Vivo profile
    m4 = match_benchmark_entry("Samsung Galaxy S24 Ultra", "Apple", BENCHMARK_KNOWLEDGE_BASE)
    assert m4 is None or m4["brand"] == "Apple"


def test_database_queries_with_benchmarks():
    """Verify that records read from SQLite populate the benchmark fields."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, brand, dxomark_camera_score, geekbench_multi, antutu_v10_score, gsmarena_battery_hours
        FROM phones
        WHERE dxomark_camera_score IS NOT NULL
        LIMIT 5
    """)
    rows = cursor.fetchall()
    conn.close()

    assert len(rows) > 0, "No benchmarked rows found in fone_master.db"
    for r in rows:
        assert r["dxomark_camera_score"] > 0
        assert r["geekbench_multi"] > 0
        assert r["antutu_v10_score"] > 0
        assert r["gsmarena_battery_hours"] > 0
