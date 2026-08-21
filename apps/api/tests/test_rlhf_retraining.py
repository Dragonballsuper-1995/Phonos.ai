"""
test_rlhf_retraining.py — Phase 6 Test Suite for Continuous RLHF & PostgreSQL Migration
========================================================================================
Validates:
1. RLHF user feedback logging and feature harvesting.
2. XGBoost ranker continuous retraining with cross-validation and AUC verification.
3. PostgreSQL / Supabase pgvector schema generation and SQL dump integrity.
4. /api/v1/recommend/feedback and /api/v1/recommend/retrain API endpoints.
"""

import os
import pytest
import httpx
from app.main import app
from scripts.retrain_rlhf_worker import (
    log_feedback_event,
    harvest_feedback_dataset,
    retrain_ranker,
    FEEDBACK_DB_PATH
)
from scripts.migrate_to_postgres import generate_postgres_migration


def test_feedback_logging_and_harvesting():
    """Verify user feedback events are logged and transformed into weighted training pairs."""
    # Log sample interactions
    log_feedback_event(
        phone_id=1,
        phone_name="Samsung Galaxy S25 Ultra",
        persona="camera",
        budget=120000.0,
        event_type="buy_clicked",
        weight=2.0
    )
    log_feedback_event(
        phone_id=2,
        phone_name="OnePlus 13",
        persona="gamer",
        budget=70000.0,
        event_type="compare_added",
        weight=1.5
    )
    log_feedback_event(
        phone_id=3,
        phone_name="Generic Phone",
        persona="student",
        budget=15000.0,
        event_type="recommendation_rejected",
        weight=2.0
    )

    pairs = harvest_feedback_dataset(limit=10)
    assert len(pairs) >= 2
    # Check feature dimensions
    for feats, label, weight in pairs:
        assert len(feats) == 7
        assert label in [0, 1]
        assert weight > 0


def test_retrain_ranker_dry_run():
    """Verify continuous retraining pipeline validates model AUC and returns metrics."""
    results = retrain_ranker(dry_run=True, synthetic_samples=1500)

    assert results["status"] == "success"
    assert results["val_auc"] >= 0.75
    assert results["total_samples"] >= 1500
    assert "val_loss" in results
    assert "val_accuracy" in results


def test_postgres_supabase_migration_dump(tmp_path):
    """Verify PostgreSQL / Supabase SQL generator creates valid DDL and inserts with pgvector."""
    out_sql = str(tmp_path / "test_dump.sql")
    res = generate_postgres_migration(output_sql_path=out_sql)

    assert res["status"] == "success"
    assert res["exported_phones"] > 0
    assert os.path.exists(out_sql)

    with open(out_sql, "r", encoding="utf-8") as f:
        content = f.read()

    assert "CREATE EXTENSION IF NOT EXISTS vector;" in content
    assert "CREATE TABLE phones" in content
    assert "dxomark_camera_score" in content
    assert "hardware_vector vector(5)" in content
    assert "INSERT INTO phones" in content


@pytest.mark.asyncio
async def test_feedback_and_retrain_endpoints():
    """Verify /feedback and /retrain API endpoints."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Feedback endpoint
        fb_resp = await client.post("/api/v1/recommend/feedback", json={
            "phone_name": "OnePlus 13",
            "persona": "gamer",
            "budget": 70000.0,
            "event_type": "buy_clicked",
            "weight": 2.0
        })
        assert fb_resp.status_code == 200
        assert fb_resp.json().get("status") == "recorded"

        # 2. Retrain endpoint
        retrain_resp = await client.post("/api/v1/recommend/retrain?dry_run=true&samples=1000")
        assert retrain_resp.status_code == 200
        data = retrain_resp.json()
        assert data.get("status") == "success"
        assert data.get("val_auc") >= 0.75
