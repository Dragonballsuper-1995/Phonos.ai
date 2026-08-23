import sqlite3
import pandas as pd
import json
import re
import os
import sys
from typing import Dict, Any, Optional, Tuple

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
DB_PATH = os.path.join(DATA_DIR, 'phonos_ai.db')

print("=================================================================")
print(" PHONOS.AI - COMPREHENSIVE DATABASE SCAN & RECTIFICATION ENGINE ")
print("=================================================================")

# Load reference datasets for high-fidelity cross-validation
print("Loading reference datasets for cross-referencing...")

# 1. GSMArena dataset
gsm_df = pd.read_csv(os.path.join(DATA_DIR, 'raw_gsmarena.csv'), low_memory=False)
gsm_map = {}
for _, row in gsm_df.iterrows():
    oem = str(row['oem']).strip().lower() if pd.notna(row['oem']) else ''
    model = str(row['model']).strip().lower() if pd.notna(row['model']) else ''
    if oem and model:
        gsm_map[(oem, model)] = row
        # Also map model without oem prefix if present
        if model.startswith(oem + ' '):
            gsm_map[(oem, model[len(oem)+1:].strip())] = row

print(f"Loaded {len(gsm_map)} GSMArena model references.")

# 2. Smartprix dataset (6002 rows)
sp_path = os.path.join(DATA_DIR, 'Analysed and Cleaned Mobiles Dataset from Smartprix.csv')
sp_map = {}
if os.path.exists(sp_path):
    sp_df = pd.read_csv(sp_path, low_memory=False)
    for _, row in sp_df.iterrows():
        b = str(row['Brand']).strip().lower() if 'Brand' in row and pd.notna(row['Brand']) else ''
        n = str(row['Product_Name']).strip().lower() if 'Product_Name' in row and pd.notna(row['Product_Name']) else ''
        if not n and 'Name' in row and pd.notna(row['Name']):
            n = str(row['Name']).strip().lower()
        if b and n:
            sp_map[(b, n)] = row
            if n.startswith(b + ' '):
                sp_map[(b, n[len(b)+1:].strip())] = row
print(f"Loaded {len(sp_map)} Smartprix model references.")

# 3. Structured device specs dataset
struct_path = os.path.join(DATA_DIR, 'device_specs_structured_dataset.csv')
struct_map = {}
if os.path.exists(struct_path):
    struct_df = pd.read_csv(struct_path, low_memory=False)
    for _, row in struct_df.iterrows():
        b = str(row['brand']).strip().lower() if pd.notna(row['brand']) else ''
        n = str(row['phone_name']).strip().lower() if pd.notna(row['phone_name']) else ''
        if b and n:
            struct_map[(b, n)] = row
            if n.startswith(b + ' '):
                struct_map[(b, n[len(b)+1:].strip())] = row
print(f"Loaded {len(struct_map)} structured dataset references.")

# Connect to database
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT rowid, brand, name, price, price_numeric, os, source, released_in_india, launch_year, raw_specs FROM phones")
all_rows = cursor.fetchall()
print(f"\nTotal phones in Master Database: {len(all_rows)}")

# Brand normalizations
BRAND_CASE_MAP = {
    'iqoo': 'iQOO',
    'oneplus': 'OnePlus',
    'realme': 'realme',
    'cmf': 'CMF',
    'samsung': 'Samsung',
    'apple': 'Apple',
    'motorola': 'Motorola',
    'google': 'Google',
    'xiaomi': 'Xiaomi',
    'redmi': 'Redmi',
    'poco': 'Poco',
    'vivo': 'Vivo',
    'oppo': 'Oppo',
    'lava': 'Lava',
    'tecno': 'Tecno',
    'infinix': 'Infinix',
    'nothing': 'Nothing',
    'honor': 'Honor',
    'hmd': 'HMD',
    'asus': 'Asus',
    'acer': 'Acer',
    'nokia': 'Nokia',
    'wobble': 'Wobble',
    'ai+': 'Ai+'
}

# Brands that do not officially sell or are completely obsolete in Indian smartphone market
NON_INDIA_BRANDS = {
    'acer', 'sharp', 'sony', 'leitz', 'meizu', 'blu', 'kyocera', 'archos', 'wiko',
    'kazam', 'gigabyte', 'plum', 'verykool', 'alcatel', 'toshiba', 'panasonic',
    'yota', 'black shark', 'cat', 'coolpad', 'doogee', 'elephone', 'fairphone',
    'gionee', 'htc', 'huawei', 'leeco', 'letv', 'lg', 'micromax', 'microsoft',
    'oukitel', 'philips', 'tcl', 'ulefone', 'umidigi', 'unihertz', 'zte', 'vaio'
}

# China-only models or phantom concept models known not to be released in India
KNOWN_NON_INDIA_OR_PHANTOM_MODELS = {
    "iqoo z11 turbo", "iqoo z11 turbo pro", "iqoo z11 turbo plus", "vivo v70e",
    "samsung galaxy s27 ultra 5g", "samsung galaxy s27 ultra", "samsung galaxy s27 pro",
    "samsung galaxy s27 5g", "samsung galaxy s27 plus 5g", "xiaomi 18 ultra",
    "xiaomi 18 5g", "oneplus 17", "oppo find x10 ultra", "xiaomi 18",
    "oppo find x10 pro max 5g", "vivo x300 ultra", "vivo x300 pro",
    "realme gt6 (china)", "oppo a5 (china)", "oppo a3 (china)", "oppo a3x (china)",
    "oppo a5 pro (china)"
}

# Known model year heuristic map for accurate fallback
KNOWN_MODEL_YEARS = {
    's26': 2026, 's25': 2025, 's24': 2024, 's23': 2023, 's22': 2022, 's21': 2021, 's20': 2020,
    'iphone 18': 2026, 'iphone 17': 2025, 'iphone 16': 2024, 'iphone 15': 2023,
    'iphone 14': 2022, 'iphone 13': 2021, 'iphone 12': 2020, 'iphone 11': 2019,
    'pixel 11': 2026, 'pixel 10': 2025, 'pixel 9': 2024, 'pixel 8': 2023, 'pixel 7': 2022,
    'pixel 6': 2021, 'pixel 5': 2020, 'pixel 4': 2019,
    'phone (3)': 2025, 'phone (2a)': 2024, 'phone (2)': 2023, 'phone (1)': 2022,
    'oneplus 13': 2024, 'oneplus 12': 2024, 'oneplus 11': 2023, 'oneplus 10': 2022,
    'oneplus 9': 2021, 'oneplus 8': 2020,
    'find x8': 2024, 'find x7': 2024, 'find x6': 2023,
    'x200': 2024, 'x100': 2023, 'x90': 2022, 'x80': 2022,
    'reno 13': 2025, 'reno 12': 2024, 'reno 11': 2024, 'reno 10': 2023, 'reno 9': 2022,
    'redmi note 14': 2024, 'redmi note 13': 2024, 'redmi note 12': 2023, 'redmi note 11': 2022
}

def clean_name_string(brand: str, raw_name: str) -> str:
    if not raw_name:
        return ""
    name = str(raw_name).strip()
    
    # Strip RAM/ROM spec patterns: (16GB RAM + 256GB), (8GB + 128GB), (3GB RAM)
    name = re.sub(r'\s*\(\d+GB\s+RAM\s*\+\s*\d+GB\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\(\d+GB\s*\+\s*\d+GB\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\(\d+GB\s+RAM\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\(\d+GB\)', '', name, flags=re.IGNORECASE)
    
    # Remove duplicate brand prefix: "Samsung Samsung Galaxy" -> "Samsung Galaxy"
    brand_lower = brand.strip().lower()
    words = name.split()
    if len(words) >= 2 and words[0].lower() == brand_lower and words[1].lower() == brand_lower:
        words.pop(0)
        name = " ".join(words)
    elif len(words) >= 2 and words[0].lower() == words[1].lower():
        words.pop(0)
        name = " ".join(words)
        
    return name.strip()

# Classification buckets
phones_pre_2023 = []
phones_not_in_india = []
phones_upcoming = []
phones_valid_india = []

# Update payloads
updates_to_apply = []

for row in all_rows:
    row_id = row['rowid']
    brand_raw = str(row['brand'] or '').strip()
    name_raw = str(row['name'] or '').strip()
    price_str = row['price']
    price_num = row['price_numeric']
    os_str = str(row['os'] or '').strip()
    source = str(row['source'] or '').strip()
    india_flag = row['released_in_india']
    launch_yr = row['launch_year']
    specs_str = row['raw_specs']
    
    specs = {}
    if specs_str:
        try:
            specs = json.loads(specs_str)
        except Exception:
            specs = {}
            
    # Clean brand casing
    clean_brand = BRAND_CASE_MAP.get(brand_raw.lower(), brand_raw.capitalize() if brand_raw else 'Unknown')
    # Clean phone name
    clean_name = clean_name_string(clean_brand, name_raw)
    
    # Check reference sources for true launch year & release status
    key1 = (clean_brand.lower(), clean_name.lower())
    clean_model_only = clean_name
    if clean_name.lower().startswith(clean_brand.lower() + ' '):
        clean_model_only = clean_name[len(clean_brand)+1:].strip()
    key2 = (clean_brand.lower(), clean_model_only.lower())
    
    gsm_ref = gsm_map.get(key1) if key1 in gsm_map else gsm_map.get(key2)
    sp_ref = sp_map.get(key1) if key1 in sp_map else sp_map.get(key2)
    struct_ref = struct_map.get(key1) if key1 in struct_map else struct_map.get(key2)
    
    # 1. Resolve Launch Year
    resolved_year = None
    
    # Check GSMArena announced/status
    if gsm_ref is not None:
        ann = str(gsm_ref.get('launch_announced', ''))
        st = str(gsm_ref.get('launch_status', ''))
        # extract year
        ym = re.findall(r'\b(19\d\d|20\d\d)\b', f"{ann} {st}")
        if ym:
            valid_ym = [int(y) for y in ym if 1995 <= int(y) <= 2030]
            if valid_ym:
                resolved_year = max(valid_ym)
                
    # Check Smartprix ref
    if not resolved_year and sp_ref is not None:
        sp_yr = sp_ref.get('Release_Year')
        sp_dt = str(sp_ref.get('Release_Date', ''))
        if pd.notna(sp_yr) and str(sp_yr).isdigit():
            resolved_year = int(sp_yr)
        elif sp_dt:
            ym = re.findall(r'\b(20\d\d)\b', sp_dt)
            if ym:
                resolved_year = int(ym[0])
                
    # Check struct ref
    if not resolved_year and struct_ref is not None:
        ldt = str(struct_ref.get('launch_date', ''))
        ym = re.findall(r'\b(20\d\d)\b', ldt)
        if ym:
            resolved_year = int(ym[0])
            
    # Check raw_specs within DB
    if not resolved_year:
        for k in ['Release_Year', 'Release Year', 'General.Release Date', 'Release_Date', 'status', 'announced']:
            if k in specs and specs[k]:
                ym = re.findall(r'\b(19\d\d|20\d\d)\b', str(specs[k]))
                if ym:
                    valid_ym = [int(y) for y in ym if 1995 <= int(y) <= 2030]
                    if valid_ym:
                        resolved_year = max(valid_ym)
                        break
                        
    # Check model year heuristic map
    if not resolved_year:
        name_l = clean_name.lower()
        for pat, yr in KNOWN_MODEL_YEARS.items():
            if pat in name_l:
                resolved_year = yr
                break
                
    # Check explicit year in name: "Moto G (2025)" -> 2025
    if not resolved_year:
        ym = re.findall(r'\b(202\d|201\d|200\d)\b', clean_name)
        if ym:
            resolved_year = int(ym[0])
            
    # Fallback to existing launch_year if sensible
    if not resolved_year and launch_yr and 2000 <= launch_yr <= 2026:
        resolved_year = int(launch_yr)
        
    # Anomaly fix: e.g. Vivo X100 year was 2000 due to nits parser
    if 'vivo x100' in clean_name.lower():
        resolved_year = 2023
    elif 'vivo x200' in clean_name.lower():
        resolved_year = 2024
    elif 'vivo x90' in clean_name.lower():
        resolved_year = 2022
    elif 'vivo x80' in clean_name.lower():
        resolved_year = 2022
        
    # 2. Check Price Accuracy & Conversions
    resolved_price_num = price_num
    resolved_price_str = price_str
    
    if (resolved_price_num is None or resolved_price_num <= 0) and sp_ref is not None:
        cp = sp_ref.get('Current_Price') or sp_ref.get('Original_Price')
        if pd.notna(cp) and str(cp).replace('.', '', 1).isdigit():
            resolved_price_num = float(cp)
            resolved_price_str = f"₹{int(resolved_price_num):,}"
            
    if (resolved_price_num is None or resolved_price_num <= 0) and struct_ref is not None:
        p_inr = struct_ref.get('price_inr') or struct_ref.get('list_price_inr')
        if pd.notna(p_inr) and str(p_inr).replace('.', '', 1).isdigit():
            resolved_price_num = float(p_inr)
            resolved_price_str = f"₹{int(resolved_price_num):,}"
            
    # 3. Check Upcoming / Rumored Status
    is_upcoming = False
    status_ann_text = ""
    if gsm_ref is not None:
        status_ann_text += f" {gsm_ref.get('launch_announced', '')} {gsm_ref.get('launch_status', '')}"
    if sp_ref is not None:
        status_ann_text += f" {sp_ref.get('Release_Date', '')} {sp_ref.get('Status', '')}"
    for k in ['status', 'Status', 'Launch Status', 'announced', 'Announced', 'General.Release Date', 'Release_Date']:
        if k in specs:
            status_ann_text += f" {specs[k]}"
            
    status_lower = status_ann_text.lower()
    if any(kw in status_lower for kw in ['rumored', 'rumoured', 'exp. release', 'exp. announcement', 'not yet announced', 'coming soon']):
        is_upcoming = True
    if resolved_year and resolved_year > 2026:
        is_upcoming = True
    if any(ph in clean_name.lower() for ph in ['s27', 'xiaomi 18', 'pixel 11', 'iphone 18', 'find x10']):
        is_upcoming = True
        
    # 4. Check Feature / Legacy Phone Status
    is_feature = False
    feature_keywords = ['kaios', 'symbian', 'java', 'proprietary', 'feature phone', 'keypad', 'guru', 'duos', 'keystone', 'metro 312', 'champ', 'kkt', 'hero 600', 'a1 tejas', 'a3 power', 'rocker', 'tuf']
    if any(k in f"{clean_name} {os_str}".lower() for k in feature_keywords):
        is_feature = True
    if resolved_price_num and resolved_price_num < 4500 and clean_brand.lower() in ['lava', 'samsung', 'hmd', 'nokia', 'itel']:
        is_feature = True
        
    # 5. Check India Release Status
    is_india = False
    
    # If it's a non-India brand, definitely 0
    if clean_brand.lower() in NON_INDIA_BRANDS:
        is_india = False
    elif clean_name.lower() in KNOWN_NON_INDIA_OR_PHANTOM_MODELS or any(ph in clean_name.lower() for ph in ['(china)', 'china only']):
        is_india = False
    elif is_upcoming or is_feature:
        is_india = False
    elif resolved_year and resolved_year < 2023:
        is_india = False
    else:
        # Check positive India signals
        if source == 'Smartprix' or sp_ref is not None or struct_ref is not None:
            is_india = True
        elif 'india' in f"{specs_str}".lower() or 'india' in str(row['source']).lower():
            is_india = True
        elif resolved_price_str and ('₹' in str(resolved_price_str) or 'rs' in str(resolved_price_str).lower() or 'inr' in str(resolved_price_str).lower()):
            is_india = True
        elif clean_brand.lower() in ['samsung', 'apple', 'oneplus', 'xiaomi', 'redmi', 'poco', 'realme', 'vivo', 'oppo', 'motorola', 'iqoo', 'infinix', 'tecno', 'nothing', 'honor', 'cmf', 'google']:
            # Mainstream brand with INR price and modern launch year (2023-2026)
            if resolved_price_num and resolved_price_num >= 4500 and resolved_year and 2023 <= resolved_year <= 2026:
                # Disqualify if only EUR/USD and no India proof
                if source == 'AllPhones.csv' and not ('₹' in str(price_str) or 'india' in str(specs_str).lower()):
                    is_india = False
                else:
                    is_india = True
                    
    # Categorize
    if resolved_year and resolved_year < 2023:
        phones_pre_2023.append({
            'id': row_id, 'brand': clean_brand, 'name': clean_name, 'year': resolved_year,
            'price': resolved_price_num, 'source': source, 'is_feature': is_feature
        })
    elif is_upcoming:
        phones_upcoming.append({
            'id': row_id, 'brand': clean_brand, 'name': clean_name, 'year': resolved_year,
            'price': resolved_price_num, 'source': source, 'status': status_lower[:60]
        })
    elif not is_india:
        phones_not_in_india.append({
            'id': row_id, 'brand': clean_brand, 'name': clean_name, 'year': resolved_year,
            'price': resolved_price_num, 'source': source, 'reason': 'Global/China exclusive, non-India brand, or unconfirmed'
        })
    else:
        phones_valid_india.append({
            'id': row_id, 'brand': clean_brand, 'name': clean_name, 'year': resolved_year,
            'price': resolved_price_num, 'source': source
        })
        
    # Queue update
    new_released_in_india = 1 if is_india else 0
    updates_to_apply.append((
        clean_brand, clean_name, resolved_price_str, resolved_price_num,
        resolved_year, new_released_in_india, row_id
    ))

print(f"\n==================== SCAN & AUDIT RESULTS ====================")
print(f"1. Phones Released Before 2023 (Legacy / Feature / Vintage): {len(phones_pre_2023)}")
print(f"2. Phones Not Released in India (China / US / EU only / Non-India brands): {len(phones_not_in_india)}")
print(f"3. Phones Releasing Upcoming (Rumored / Unreleased / Future concepts): {len(phones_upcoming)}")
print(f"4. Valid Modern Released Smartphones in India (2023 - 2026): {len(phones_valid_india)}")
print(f"==============================================================")

# Show detailed breakdown samples
print("\n--- SAMPLE: Phones Released Before 2023 (First 15) ---")
for p in phones_pre_2023[:15]:
    print(f"  [Pre-2023] ID={p['id']} | {p['brand']} {p['name']} | Year: {p['year']} | Price: ₹{p['price']} | Feature: {p['is_feature']}")

print("\n--- SAMPLE: Phones Releasing Upcoming (First 15) ---")
for p in phones_upcoming[:15]:
    print(f"  [Upcoming] ID={p['id']} | {p['brand']} {p['name']} | Year: {p['year']} | Status: {p['status']}")

print("\n--- SAMPLE: Phones Not Released in India (First 15) ---")
for p in phones_not_in_india[:15]:
    print(f"  [Not in India] ID={p['id']} | {p['brand']} {p['name']} | Year: {p['year']} | Reason: {p['reason']}")

print("\n--- SAMPLE: Valid Modern Indian Smartphones (First 15) ---")
for p in phones_valid_india[:15]:
    print(f"  [India 2023-2026] ID={p['id']} | {p['brand']} {p['name']} | Year: {p['year']} | Price: ₹{p['price']}")

conn.close()
