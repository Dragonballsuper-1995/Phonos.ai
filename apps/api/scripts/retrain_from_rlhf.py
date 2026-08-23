"""
retrain_from_rlhf.py
====================
Fetches real user interaction events (buy_clicked, phone_rejected) from PostHog,
constructs training rows using the canonical 7-feature schema, merges them with
a synthetic baseline, and retrains ranker.xgb with sample weighting.

Usage:
  python scripts/retrain_from_rlhf.py [--days 60] [--min-events 10] [--force-retrain]
"""
import argparse
import json
import os
import random
import re
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple

import pandas as pd
import requests
import xgboost as xgb

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

from app.models.phone import PhoneDetails
from app.services.recommender import extract_features, FEATURE_COLS, MAX_PRICE_NORM, persona_name_to_idx

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/phonos_ai.db'))
MODEL_JSON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/ranker.json'))
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/ranker.xgb'))

POSTHOG_KEY = os.getenv("POSTHOG_API_KEY", "")
POSTHOG_HOST = os.getenv("POSTHOG_HOST", "https://eu.i.posthog.com")

def fetch_posthog_events(days_back: int = 60) -> List[Dict]:
    """Fetch buy_clicked and phone_rejected events from PostHog."""
    if not POSTHOG_KEY:
        print("[RLHF] No PostHog API key configured in .env.")
        return []

    after = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = f"{POSTHOG_HOST}/api/projects/@current/events"
    headers = {"Authorization": f"Bearer {POSTHOG_KEY}"}
    events = []

    for event_name in ["buy_clicked", "phone_rejected"]:
        try:
            params = {"event": event_name, "after": after, "limit": 1000}
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                events.extend(results)
                print(f"[RLHF] Fetched {len(results)} '{event_name}' events from PostHog.")
            else:
                print(f"[RLHF] PostHog API returned status {resp.status_code} for '{event_name}'.")
        except Exception as e:
            print(f"[RLHF] Error querying PostHog for '{event_name}': {e}")

    return events

def build_phone_lookup(conn: sqlite3.Connection) -> Dict[str, PhoneDetails]:
    """Builds a lookup dict of normalized phone names to PhoneDetails objects."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT rowid as id, brand, name, price, price_numeric, raw_specs, "
        "released_in_india, launch_year, is_current_catalogue "
        "FROM phones WHERE released_in_india = 1"
    )
    rows = cursor.fetchall()

    lookup = {}
    for r in rows:
        d = {
            "id": r[0],
            "brand": r[1],
            "name": r[2],
            "price": r[3],
            "price_numeric": r[4],
            "raw_specs": json.loads(r[5]) if isinstance(r[5], str) and r[5].startswith('{') else r[5],
            "released_in_india": r[6],
            "launch_year": r[7],
            "is_current_catalogue": r[8]
        }
        try:
            phone = PhoneDetails(**d)
            name_clean = str(phone.name or "").lower().strip()
            lookup[name_clean] = phone
            # Also index by brand + model
            brand_model = f"{phone.brand} {phone.name}".lower().strip()
            lookup[brand_model] = phone
        except Exception:
            continue
    return lookup

def events_to_training_data(events: List[Dict], phone_lookup: Dict[str, PhoneDetails]) -> Tuple[List[List[float]], List[int]]:
    """Converts PostHog interaction events into 7-feature training vectors."""
    X_real = []
    y_real = []

    for ev in events:
        props = ev.get("properties", {})
        phone_name = str(props.get("phone_name") or props.get("phone_model") or "").lower().strip()
        persona_str = str(props.get("persona") or "General")
        budget = float(props.get("budget") or 35000.0)
        label = 1 if ev.get("event") == "buy_clicked" else 0

        # Find matching phone
        phone = phone_lookup.get(phone_name)
        if not phone:
            # Fuzzy match
            for k, p in phone_lookup.items():
                if k in phone_name or phone_name in k:
                    phone = p
                    break

        if not phone:
            continue

        persona_idx = persona_name_to_idx(persona_str)
        feats = extract_features(phone, persona_idx, budget)
        X_real.append(feats)
        y_real.append(label)

    return X_real, y_real

def generate_synthetic_baseline(conn: sqlite3.Connection, n: int = 5000) -> Tuple[List[List[float]], List[int]]:
    """Generates synthetic baseline interactions for model stability."""
    from scripts.train_ranker import extract_features as extract_row_feats
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, name, brand, price, raw_specs FROM phones WHERE released_in_india=1")
    rows = cursor.fetchall()

    if not rows:
        return [], []

    BUDGET_TIERS = [10000, 15000, 20000, 25000, 30000, 40000, 50000, 70000, 100000, 150000, 200000]
    X_synth = []
    y_synth = []

    for _ in range(n):
        row = random.choice(rows)
        persona = random.randint(0, 4)
        budget = random.choice(BUDGET_TIERS)
        feats = extract_row_feats(row, persona, budget)
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
            elif persona == 3:
                if perf >= 0.75: prob += 0.20
            else:
                if 0.70 <= budget_ratio <= 1.0: prob += 0.15

            click = 1 if random.random() < max(0.01, min(0.95, prob)) else 0

        X_synth.append(feats)
        y_synth.append(click)

    return X_synth, y_synth

def main():
    parser = argparse.ArgumentParser(description="RLHF retraining from PostHog events.")
    parser.add_argument("--days", type=int, default=60, help="Days of events to fetch.")
    parser.add_argument("--min-events", type=int, default=10, help="Minimum real events required.")
    parser.add_argument("--force-retrain", action="store_true", help="Retrain even if zero real events.")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    phone_lookup = build_phone_lookup(conn)

    events = fetch_posthog_events(days_back=args.days)
    X_real, y_real = events_to_training_data(events, phone_lookup)
    print(f"[RLHF] Mapped {len(X_real)} real interaction rows.")

    if len(X_real) < args.min_events and not args.force_retrain:
        print(f"[RLHF] Total real events ({len(X_real)}) is below threshold ({args.min_events}).")
        print("[RLHF] Existing production model preserved without changes.")
        conn.close()
        return

    print("[RLHF] Synthesizing baseline data (5,000 interactions)...")
    X_synth, y_synth = generate_synthetic_baseline(conn, n=5000)
    conn.close()

    # Blend datasets with sample weights (real user actions weighted 3x over synthetic)
    X_all = X_real + X_synth
    y_all = y_real + y_synth
    sample_weights = [1.0] * len(X_real) + [0.33] * len(X_synth)

    print(f"[RLHF] Training XGBoost on {len(X_real)} real + {len(X_synth)} synthetic rows...")
    df_X = pd.DataFrame(X_all, columns=FEATURE_COLS)
    sr_y = pd.Series(y_all)

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.08,
        eval_metric='logloss',
        random_state=42
    )
    model.fit(df_X, sr_y, sample_weight=sample_weights)

    print(f"[RLHF] Saving retrained ranker to {MODEL_JSON_PATH} and {MODEL_PATH}...")
    model.save_model(MODEL_JSON_PATH)
    model.save_model(MODEL_PATH)
    print("✅ [RLHF] Retraining complete!")

if __name__ == "__main__":
    main()
