import sqlite3
import pandas as pd
import numpy as np
import xgboost as xgb
import os
import random
import pickle

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/fone_master.db'))
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/ranker.xgb'))

# Simple heuristic features for synthesis
def extract_features(row):
    # row: (rowid, name, brand, price, raw_specs)
    price = row[3]
    if not price: price = 0
    elif isinstance(price, str):
        try: price = float(price.replace('₹', '').replace(',', ''))
        except: price = 0
        
    raw_html = str(row[4]).lower()
    
    is_feature_phone = price < 4000.0 or "feature phone" in raw_html or "keypad" in raw_html
    
    # Extract battery
    battery = 1200 if is_feature_phone else 5000
    if '6000' in raw_html: battery = 6000
    elif '4500' in raw_html: battery = 4500
    elif '4000' in raw_html: battery = 4000
    
    # Extract RAM
    ram = 0.032 if is_feature_phone else 8
    if '16gb ram' in raw_html: ram = 16
    elif '12gb ram' in raw_html: ram = 12
    elif '4gb ram' in raw_html: ram = 4
    
    # Extract Display Hz
    hz = 30 if is_feature_phone else 60
    if '144hz' in raw_html: hz = 144
    elif '120hz' in raw_html: hz = 120
    elif '90hz' in raw_html: hz = 90
    
    # Heuristic performance tier (0 to 3)
    perf = 0 if is_feature_phone else 1
    if 'snapdragon 8' in raw_html or 'dimensity 9' in raw_html or 'a18' in raw_html: perf = 3
    elif 'snapdragon 7' in raw_html or 'dimensity 8' in raw_html: perf = 2
    elif 'snapdragon 6' in raw_html or 'dimensity 7' in raw_html: perf = 1
    
    return [price, battery, ram, hz, perf, is_feature_phone]


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
        
    print("Extracting features...")
    phone_features = {}
    for r in rows:
        phone_features[str(r[0])] = extract_features(r)

    print("Synthesizing 10,000 user interactions (RLHF Simulation)...")
    # Personas: 0: Student, 1: Gamer, 2: Camera, 3: General
    # We will simulate clicks.
    
    X = []
    y = [] # 1 = clicked/purchased, 0 = ignored
    
    for _ in range(10000):
        # Pick random phone
        row = random.choice(rows)
        p_id = str(row[0])
        feats = phone_features[p_id]
        
        persona = random.randint(0, 3)
        budget = random.choice([15000, 30000, 50000, 100000, 150000])
        
        price, battery, ram, hz, perf, is_feature_phone = feats
        
        # Out of budget
        if price > budget * 1.1 or price == 0:
            click = 0
        else:
            # Calculate probability based on persona
            prob = 0.1 # Base prob
            
            # Penalize underutilizing budget (e.g., spending less than 60% of budget)
            if price < budget * 0.6:
                prob -= 0.2
            
            # Boost utilizing budget well (e.g., between 75% and 100%)
            if budget * 0.75 <= price <= budget:
                prob += 0.15
                
            # Block feature phones if budget is high
            if is_feature_phone and budget >= 8000:
                prob = -1.0
            
            if persona == 0: # Student (Value, Battery)
                if price <= budget * 0.8: prob += 0.1
                if battery >= 5000: prob += 0.2
            elif persona == 1: # Gamer (Perf, Hz)
                if perf >= 2: prob += 0.3
                if hz >= 120: prob += 0.2
                if ram >= 12: prob += 0.1
            elif persona == 2: # Camera
                if price > 50000: prob += 0.3 # Premium phones have better cameras
            else: # General
                if price <= budget: prob += 0.1
                
            click = 1 if random.random() < prob else 0
            
        # Feature vector: [persona, budget, price, battery, ram, hz, perf]
        X.append([persona, budget, price, battery, ram, hz, perf])
        y.append(click)
        
    print("Training XGBoost DLRM Ranking Model...")
    df_X = pd.DataFrame(X, columns=['persona', 'budget', 'price', 'battery', 'ram', 'hz', 'perf'])
    sr_y = pd.Series(y)
    
    model = xgb.XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1)
    model.fit(df_X, sr_y)
    
    print(f"Saving model to {MODEL_PATH}...")
    model.save_model(MODEL_PATH)
    
    print("Phase 1 Ranker training complete!")

if __name__ == "__main__":
    main()
