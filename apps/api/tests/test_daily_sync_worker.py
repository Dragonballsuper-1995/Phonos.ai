"""
test_daily_sync_worker.py — Phase 5 Test Suite for Continuous Ingestion & Image Asset CDN
========================================================================================
Validates:
1. Image asset URL standardization and validation.
2. 5-step continuous ingestion sync pipeline (Scraping -> Catalog Upsert -> Benchmarks -> ABSA -> Image assets).
3. /api/v1/phones/sync/daily API trigger endpoint.
"""

import pytest
import httpx
from app.main import app
from app.services.image_optimizer import get_standard_image_url, validate_image_url
from scripts.daily_sync_worker import run_daily_sync


def test_image_optimizer_standard_url():
    """Verify image asset optimizer produces valid branded WebP/PNG placeholders."""
    url_apple = get_standard_image_url("iPhone 16 Pro", "Apple")
    url_samsung = get_standard_image_url("Galaxy S25 Ultra", "Samsung")
    url_custom = get_standard_image_url("Custom Phone", "OnePlus", existing_url="https://assets.phonos.ai/oneplus13.webp")

    assert validate_image_url(url_apple)
    assert validate_image_url(url_samsung)
    assert url_custom == "https://assets.phonos.ai/oneplus13.webp"
    assert "1D1D1F" in url_apple  # Apple theme
    assert "1428A0" in url_samsung  # Samsung theme


def test_image_optimizer_validation():
    """Verify image URL validator detects valid formats and rejects invalid strings."""
    assert validate_image_url("https://images.samsung.com/phone.jpg")
    assert validate_image_url("https://store.apple.com/iphone.png")
    assert validate_image_url("https://placehold.co/600x800/000/fff.png?text=Test")
    assert not validate_image_url("")
    assert not validate_image_url("invalid-url")
    assert not validate_image_url("ftp://example.com/file.exe")


def test_daily_sync_worker_dry_run():
    """Verify daily ingestion worker executes the full 5-step pipeline in dry-run mode."""
    stats = run_daily_sync(dry_run=True)

    assert isinstance(stats, dict)
    assert stats["scraped_models_total"] > 100
    assert stats["existing_models_updated"] > 0
    assert stats["benchmarks_linked"] > 0
    assert stats["sentiment_enriched"] >= 0
    assert stats["images_standardized"] >= 0


@pytest.mark.asyncio
async def test_daily_sync_api_endpoint():
    """Verify /api/v1/phones/sync/daily triggers worker pipeline and returns success payload."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/phones/sync/daily?dry_run=true")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "success"
        assert "stats" in data
        assert data["stats"]["scraped_models_total"] > 100
