import pytest
import os
import csv
import sqlite3
from app.services.scrapers.official_catalogues import (
    SCRAPERS_REGISTRY,
    ScrapedPhoneModel,
    BrandMetadata,
)
from app.services.scrapers.official_catalogues.csv_exporter import export_catalogues_to_csv, CSV_COLUMNS
from app.services.catalogue_matcher import normalize_phone_name, CatalogueMatcher

def test_canonical_20_brands_present():
    """Verifies that all 20 canonical consumer brands exist in registry."""
    expected_brands = {
        "Apple", "ASUS", "Google", "HMD", "HONOR", "Infinix", "iQOO", "Lava",
        "Motorola", "Nothing", "CMF", "OnePlus", "OPPO", "POCO", "realme",
        "Redmi", "Samsung", "TECNO", "vivo", "Xiaomi"
    }
    registered = set(SCRAPERS_REGISTRY.keys())
    assert registered == expected_brands, f"Missing or extra brands: {expected_brands ^ registered}"

def test_nokia_not_in_active_brands():
    """Verifies Nokia is not treated as an active smartphone brand in India."""
    assert "Nokia" not in SCRAPERS_REGISTRY

def test_asus_is_active_limited():
    """Verifies ASUS is flagged as ACTIVE_LIMITED."""
    scraper_cls = SCRAPERS_REGISTRY["ASUS"]
    scraper = scraper_cls()
    assert scraper.brand_status == "ACTIVE_LIMITED"

def test_tecno_pova_8_pro_launch_handling():
    """Verifies TECNO scraper handles POVA 8 Pro 5G launch status and date."""
    scraper_cls = SCRAPERS_REGISTRY["TECNO"]
    scraper = scraper_cls()
    phones = scraper.scrape()
    pova_8 = next((p for p in phones if "POVA 8 Pro" in p.model_name), None)
    assert pova_8 is not None
    assert pova_8.launch_status == "announced_in_india"
    assert pova_8.sale_start_date == "2026-08-21"

def test_normalization_removes_noise_and_brackets():
    """Verifies string normalization strips RAM/ROM, 5G, and punctuation cleanly."""
    assert normalize_phone_name("Galaxy S26 Ultra 5G (12GB+256GB)", "Samsung") == "galaxy s26 ultra"
    assert normalize_phone_name("OnePlus Nord 4 5G (8GB RAM)", "OnePlus") == "nord 4"
    assert normalize_phone_name("Redmi Note 15 Pro+ 5G", "Redmi") == "note 15 pro plus"
    assert normalize_phone_name("Phone (4a)", "Nothing") == "phone (4a)"

def test_csv_export_groups(tmp_path):
    """Verifies CSV generation partitions correctly by ecosystem and generates master CSV."""
    sample_phones = [
        ScrapedPhoneModel(
            brand="Xiaomi",
            parent_ecosystem="Xiaomi Corporation",
            model_name="Xiaomi 17",
            full_name="Xiaomi 17",
            price_inr=74999.0
        ),
        ScrapedPhoneModel(
            brand="POCO",
            parent_ecosystem="Xiaomi Corporation",
            model_name="POCO X8 Pro",
            full_name="POCO X8 Pro",
            price_inr=27999.0
        ),
        ScrapedPhoneModel(
            brand="vivo",
            parent_ecosystem="BBK Ecosystem",
            model_name="X300 Pro",
            full_name="vivo X300 Pro",
            price_inr=99999.0
        ),
        ScrapedPhoneModel(
            brand="Nothing",
            parent_ecosystem="Nothing Ecosystem",
            model_name="Phone (3)",
            full_name="Nothing Phone (3)",
            price_inr=49999.0
        ),
        ScrapedPhoneModel(
            brand="HMD",
            parent_ecosystem="HMD Global",
            model_name="HMD Skyline",
            full_name="HMD Skyline",
            price_inr=35999.0
        ),
        ScrapedPhoneModel(
            brand="Apple",
            parent_ecosystem="Mainstream & Flagship",
            model_name="iPhone 16 Pro",
            full_name="Apple iPhone 16 Pro",
            price_inr=119900.0
        ),
    ]

    out_dir = str(tmp_path)
    exported = export_catalogues_to_csv(sample_phones, out_dir)

    assert "Xiaomi_Corporation_Phones.csv" in exported
    assert "BBK_Ecosystem_Phones.csv" in exported
    assert "Nothing_Ecosystem_Phones.csv" in exported
    assert "HMD_Global_Phones.csv" in exported
    assert "Mainstream_and_Flagship_Phones.csv" in exported
    assert "Combined_Official_India_Smartphones_Catalogue.csv" in exported

    # Check combined contains all 6 models + brand separator rows
    with open(exported["Combined_Official_India_Smartphones_Catalogue.csv"], mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        data_rows = [r for r in rows if r["brand"]]
        assert len(data_rows) == 6
        for col in CSV_COLUMNS:
            assert col in reader.fieldnames

