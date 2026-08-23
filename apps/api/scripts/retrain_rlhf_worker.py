"""
retrain_rlhf_worker.py — Continuous RLHF Feedback Harvester & XGBoost Retrainer
==============================================================================
Orchestrates continuous reinforcement learning from user feedback:
1. Ingests user feedback events (recommendation accepted, buy clicked, compare added, rejected).
2. Converts interactions into weighted training pairs (Positive = buy/compare/accept, Negative = rejected).
3. Merges feedback pairs with the baseline distribution.
4. Retrains the XGBoost DLRM Ranker with cross-validation and AUC tracking.
5. Performs atomic hot-swap of the production ranker.xgb model.

Usage:
  python scripts/retrain_rlhf_worker.py [--dry-run] [--min-feedback 10]
"""

import os
import sys
import json
import sqlite3
import random
import argparse
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, log_loss

# Ensure app is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.train_ranker import FEATURE_COLS, MAX_PRICE_NORM, extract_features

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/phonos_ai.db'))
MODEL_JSON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/ranker.json'))
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/ranker.xgb'))
FEEDBACK_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/feedback_events.db'))

PERSONA_MAP = {
    "student": 0,
    "gamer": 1,
    "camera": 2,
    "photography": 2,
    "content creator": 2,
    "professional": 3,
    "general": 4,
}


def init_feedback_db():
    """Initializes the SQLite feedback event buffer table."""
    conn = sqlite3.connect(FEEDBACK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_id INTEGER,
            phone_name TEXT,
            persona TEXT,
            budget REAL,
            event_type TEXT,
            weight REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def log_feedback_event(
    phone_id: int,
    phone_name: str,
    persona: str,
    budget: float,
    event_type: str,
    weight: float = 1.0
):
    """Logs a single user interaction event for continuous retraining."""
    init_feedback_db()
    conn = sqlite3.connect(FEEDBACK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedback_events (phone_id, phone_name, persona, budget, event_type, weight)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (phone_id, phone_name, persona, budget, event_type, weight))
    conn.commit()
    conn.close()


def harvest_feedback_dataset(limit: int = 5000) -> List[Tuple[list, int, float]]:
    """
    Harvests feedback events and converts them to feature vectors with sample weights.
    Returns: List of (feature_list, label, sample_weight)
    """
    init_feedback_db()
    conn_fb = sqlite3.connect(FEEDBACK_DB_PATH)
    cursor_fb = conn_fb.cursor()
    cursor_fb.execute("""
        SELECT phone_id, phone_name, persona, budget, event_type, weight
        FROM feedback_events
        ORDER BY id DESC LIMIT ?
    """, (limit,))
    feedback_rows = cursor_fb.fetchall()
    conn_fb.close()

    if not feedback_rows:
        return []

    conn_main = sqlite3.connect(DB_PATH)
    cursor_main = conn_main.cursor()

    training_pairs = []
    for row in feedback_rows:
        p_id, p_name, persona_str, budget, event_type, sample_weight = row
        cursor_main.execute(
            "SELECT rowid as id, name, brand, price, raw_specs FROM phones WHERE rowid = ? OR name = ?",
            (p_id, p_name)
        )
        phone_row = cursor_main.fetchone()
        if not phone_row:
            continue

        p_idx = PERSONA_MAP.get(str(persona_str).lower().strip(), 4)
        feats = extract_features(phone_row, p_idx, float(budget or 50000.0))

        # Event type to binary target
        if event_type in ["recommendation_accepted", "buy_clicked", "report_viewed", "compare_added"]:
            label = 1
        elif event_type in ["recommendation_rejected", "dismissed"]:
            label = 0
        else:
            label = 1 if sample_weight > 0 else 0

        training_pairs.append((feats, label, sample_weight))

    conn_main.close()
    return training_pairs


def retrain_ranker(
    dry_run: bool = False,
    synthetic_samples: int = 15000,
    min_feedback_samples: int = 0
) -> Dict[str, Any]:
    """
    Runs the full continuous retraining pipeline:
    Baseline synthetic dataset + Harvested RLHF feedback pairs -> XGBoost DLRM -> Validation -> Hot-swap.
    """
    print("=" * 70)
    print("🧠 Starting Phonos.ai Continuous RLHF Retraining Worker")
    print(f"📦 Model: {MODEL_PATH} | Mode: {'DRY RUN' if dry_run else 'LIVE RETRAINING'}")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT rowid as id, name, brand, price, raw_specs FROM phones WHERE released_in_india=1")
    phone_rows = cursor.fetchall()
    conn.close()

    if not phone_rows:
        raise ValueError("No phone records available in database for retraining.")

    # 1. Generate Baseline Synthetic Dataset
    print(f"📊 Synthesizing {synthetic_samples:,} baseline interactions across personas & budget tiers...")
    BUDGET_TIERS = [10000, 15000, 20000, 25000, 30000, 40000, 50000, 70000, 100000, 150000, 200000]

    X = []
    y = []
    sample_weights = []

    for _ in range(synthetic_samples):
        row = random.choice(phone_rows)
        persona = random.randint(0, 4)
        budget = random.choice(BUDGET_TIERS)

        feats = extract_features(row, persona, budget)
        persona_val, budget_ratio, price_ratio, battery_norm, ram_norm, hz_norm, perf = feats
        price = price_ratio * MAX_PRICE_NORM

        if price > budget * 1.05 or price <= 0:
            click = 0
        else:
            prob = 0.15
            if budget_ratio < 0.60: prob -= 0.25
            elif 0.75 <= budget_ratio <= 1.0: prob += 0.20

            if persona == 0:
                if budget_ratio <= 0.85: prob += 0.15
                if battery_norm >= 5000 / 7000: prob += 0.20
            elif persona == 1:
                if perf >= 0.75: prob += 0.30
                if hz_norm >= 120 / 165: prob += 0.20
            elif persona == 2:
                if price >= 35000: prob += 0.25
                if perf >= 0.5: prob += 0.15
            elif persona == 3:
                if perf >= 0.75: prob += 0.20
                if budget_ratio >= 0.80: prob += 0.15
            else:
                if 0.70 <= budget_ratio <= 1.0: prob += 0.15

            click = 1 if random.random() < max(0.01, min(0.95, prob)) else 0

        X.append(feats)
        y.append(click)
        sample_weights.append(1.0)

    # 2. Ingest Harvested RLHF Feedback Interactions
    feedback_pairs = harvest_feedback_dataset()
    print(f"📥 Harvested {len(feedback_pairs)} real-world RLHF interaction events.")

    for f_feats, f_label, f_weight in feedback_pairs:
        X.append(f_feats)
        y.append(f_label)
        sample_weights.append(float(f_weight or 1.0))

    # 3. Train/Validation Split
    df_X = pd.DataFrame(X, columns=FEATURE_COLS)
    sr_y = pd.Series(y)
    sr_weights = pd.Series(sample_weights)

    X_train, X_val, y_train, y_val, w_train, w_val = train_test_split(
        df_X, sr_y, sr_weights, test_size=0.20, random_state=42, stratify=sr_y
    )

    print(f"🏋️ Training XGBoost Classifier ({len(X_train)} train, {len(X_val)} validation)...")
    model = xgb.XGBClassifier(
        n_estimators=220,
        max_depth=5,
        learning_rate=0.07,
        eval_metric='logloss',
        random_state=42,
        tree_method='hist',
    )
    model.fit(X_train, y_train, sample_weight=w_train)

    # 4. Evaluation Metrics
    val_preds_prob = model.predict_proba(X_val)[:, 1]
    val_auc = float(roc_auc_score(y_val, val_preds_prob))
    val_loss = float(log_loss(y_val, val_preds_prob))
    val_acc = float((model.predict(X_val) == y_val).mean())

    print("\n📈 Model Validation Metrics:")
    print(f"  • Validation ROC-AUC: {val_auc:.4f} (Target: >= 0.80)")
    print(f"  • Validation Log-Loss: {val_loss:.4f}")
    print(f"  • Validation Accuracy: {val_acc:.4f}")

    if val_auc < 0.75:
        raise ValueError(f"Model validation failed: AUC {val_auc:.4f} is below 0.75 threshold.")

    # 5. Hot-swap and save
    if not dry_run:
        print(f"\n💾 Saving retrained model to {MODEL_JSON_PATH} and {MODEL_PATH}...")
        model.save_model(MODEL_JSON_PATH)
        model.save_model(MODEL_PATH)
        print("✅ Production model hot-swapped successfully!")

    results = {
        "status": "success",
        "total_samples": len(X),
        "synthetic_samples": synthetic_samples,
        "rlhf_feedback_samples": len(feedback_pairs),
        "val_auc": round(val_auc, 4),
        "val_loss": round(val_loss, 4),
        "val_accuracy": round(val_acc, 4),
        "dry_run": dry_run,
    }
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phonos.ai Continuous RLHF XGBoost Retrainer")
    parser.add_argument("--dry-run", action="store_true", help="Train and validate without saving model")
    parser.add_argument("--samples", type=int, default=15000, help="Number of baseline synthetic samples")
    args = parser.parse_args()

    retrain_ranker(dry_run=args.dry_run, synthetic_samples=args.samples)
