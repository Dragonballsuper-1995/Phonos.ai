import sqlite3
import pandas as pd
import numpy as np
import xgboost as xgb
import os
import random
import re

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/fone_master.db'))
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/ranker.xgb'))

# ── CANONICAL FEATURE SCHEMA (must match recommender.py exactly) ──────────────
MAX_PRICE_NORM = 200000  # global price normalisation ceiling

FEATURE_COLS = [
    'persona',       # float 0-4 (0=Student, 1=Gamer, 2=Camera, 3=Professional, 4=General)
    'budget_ratio',  # price / budget (0.0 – 1.05)
    'price_ratio',   # price / MAX_PRICE_NORM (0.0 – 1.0)
    'battery_norm',  # battery_mah / 7000 (0.0 – 1.0)
    'ram_norm',      # ram_gb / 24 (0.0 – 1.0)
    'hz_norm',       # refresh_hz / 165 (0.0 – 1.0)
    'perf_tier',     # 0.1 / 0.25 / 0.5 / 0.75 / 1.0 (5 tiers)
]

def extract_features(row, persona: int, budget: float) -> list:
    """Canonical 7-feature extractor. MUST match recommender.py exactly."""
    price = row[3]
    if not price:
        price = 0.0
    elif isinstance(price, str):
        try:
            nums = re.findall(r'\d+', price.replace('₹', '').replace(',', ''))
            price = float(nums[0]) if nums else 0.0
        except Exception:
            price = 0.0
    else:
        price = float(price)

    raw_html = str(row[4] or '').lower()

    battery = 5000
    if '7300' in raw_html or '7000' in raw_html: battery = 7000
    elif '6500' in raw_html or '6000' in raw_html: battery = 6000
    elif '5500' in raw_html: battery = 5500
    elif '4500' in raw_html: battery = 4500
    elif '4000' in raw_html: battery = 4000

    ram = 8
    if '24gb ram' in raw_html: ram = 24
    elif '16gb ram' in raw_html: ram = 16
    elif '12gb ram' in raw_html: ram = 12
    elif '4gb ram'  in raw_html: ram = 4

    hz = 60
    if '165hz' in raw_html: hz = 165
    elif '144hz' in raw_html: hz = 144
    elif '120hz' in raw_html: hz = 120
    elif '90hz'  in raw_html: hz = 90

    perf = 0.25
    if any(k in raw_html for k in ['snapdragon 8 elite', 'dimensity 9400', 'a18 pro', 'a18']): perf = 1.0
    elif any(k in raw_html for k in ['snapdragon 8 gen 3', 'dimensity 9300', 'a17 pro', 'a17']): perf = 0.75
    elif any(k in raw_html for k in ['snapdragon 7', 'dimensity 8']): perf = 0.5
    elif any(k in raw_html for k in ['snapdragon 6', 'dimensity 7']): perf = 0.25
    else: perf = 0.1

    budget_ratio = min(1.05, price / budget) if budget > 0 else 0.5
    price_ratio = min(1.0, price / MAX_PRICE_NORM)
    battery_norm = min(1.0, battery / 7000)
    ram_norm = min(1.0, ram / 24)
    hz_norm = min(1.0, hz / 165)

    return [float(persona), budget_ratio, price_ratio, battery_norm, ram_norm, hz_norm, perf]


def main():
    print("Loading phones...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, name, brand, price, raw_specs FROM phones WHERE released_in_india=1")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No phones found.")
        return

    print(f"Loaded {len(rows)} phones from database.")
    print("Synthesizing 15,000 user interactions (RLHF Simulation)...")
    # Personas: 0: Student, 1: Gamer, 2: Camera, 3: Professional, 4: General
    BUDGET_TIERS = [10000, 15000, 20000, 25000, 30000, 40000, 50000, 70000, 100000, 150000, 200000]

    X = []
    y = []  # 1 = clicked/purchased, 0 = ignored

    for _ in range(15000):
        row = random.choice(rows)
        persona = random.randint(0, 4)
        budget = random.choice(BUDGET_TIERS)

        feats = extract_features(row, persona, budget)
        persona_val, budget_ratio, price_ratio, battery_norm, ram_norm, hz_norm, perf = feats
        price = price_ratio * MAX_PRICE_NORM

        # Out of budget
        if price > budget * 1.05 or price <= 0:
            click = 0
        else:
            # Calculate probability based on persona & budget utilization
            prob = 0.15  # Base probability

            # Penalize severely underutilizing budget (< 60%)
            if budget_ratio < 0.60:
                prob -= 0.25
            # Reward sweet spot budget utilization (75% - 100%)
            elif 0.75 <= budget_ratio <= 1.0:
                prob += 0.20

            # Persona specific utility
            if persona == 0:  # Student (Value, Battery, Decent RAM)
                if budget_ratio <= 0.85: prob += 0.15
                if battery_norm >= 5000 / 7000: prob += 0.20
                if price <= 25000: prob += 0.10
            elif persona == 1:  # Gamer (Perf, Hz, RAM)
                if perf >= 0.75: prob += 0.30
                if hz_norm >= 120 / 165: prob += 0.20
                if ram_norm >= 12 / 24: prob += 0.15
            elif persona == 2:  # Camera (High specs / Flagship optics)
                if price >= 35000: prob += 0.25
                if perf >= 0.5: prob += 0.15
            elif persona == 3:  # Professional (Build, Balanced Flagship, Smoothness)
                if perf >= 0.75: prob += 0.20
                if budget_ratio >= 0.80: prob += 0.15
                if battery_norm >= 5000 / 7000: prob += 0.10
            else:  # General
                if 0.70 <= budget_ratio <= 1.0: prob += 0.15
                if perf >= 0.25: prob += 0.10

            click = 1 if random.random() < max(0.01, min(0.95, prob)) else 0

        X.append(feats)
        y.append(click)

    print("Training XGBoost DLRM Ranking Model with Canonical Schema...")
    df_X = pd.DataFrame(X, columns=FEATURE_COLS)
    sr_y = pd.Series(y)

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.08,
        eval_metric='logloss',
        random_state=42
    )
    model.fit(df_X, sr_y)

    print(f"Saving model to {MODEL_PATH}...")
    model.save_model(MODEL_PATH)
    print("Phase 1 Ranker training complete!")

if __name__ == "__main__":
    main()

