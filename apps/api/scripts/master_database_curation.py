import sqlite3
import pandas as pd
import json
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
DB_PATH = os.path.join(DATA_DIR, 'fone_master.db')

print("================================================================================")
print("       PHONOS.AI - SOTA MASTER DATABASE SCAN, CURATION & RECTIFICATION         ")
print("================================================================================")

# 1. Load Reference Datasets for Cross-Verification
print("\n[Step 1] Loading reference datasets for cross-verification...")

gsm_df = pd.read_csv(os.path.join(DATA_DIR, 'raw_gsmarena.csv'), low_memory=False)
gsm_map = {}
for _, row in gsm_df.iterrows():
    oem = str(row['oem']).strip().lower() if pd.notna(row['oem']) else ''
    model = str(row['model']).strip().lower() if pd.notna(row['model']) else ''
    if oem and model:
        gsm_map[(oem, model)] = row
        if model.startswith(oem + ' '):
            gsm_map[(oem, model[len(oem)+1:].strip())] = row
print(f"  -> GSMArena references: {len(gsm_map)}")

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
print(f"  -> Smartprix references: {len(sp_map)}")

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
print(f"  -> Structured dataset references: {len(struct_map)}")

# Brand normalization mappings
BRAND_NORMALIZATION = {
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

# Brands not active in Indian mainstream smartphone market
NON_INDIA_BRANDS = {
    'acer', 'wobble', 'ai+', 'sharp', 'sony', 'leitz', 'meizu', 'blu', 'kyocera',
    'archos', 'wiko', 'kazam', 'gigabyte', 'plum', 'verykool', 'alcatel', 'toshiba',
    'panasonic', 'yota', 'black shark', 'cat', 'coolpad', 'doogee', 'elephone',
    'fairphone', 'gionee', 'htc', 'huawei', 'leeco', 'letv', 'lg', 'micromax',
    'microsoft', 'oukitel', 'philips', 'tcl', 'ulefone', 'umidigi', 'unihertz', 'zte'
}

# Known China-only or speculative phantom concept models
NON_INDIA_MODELS = {
    "iqoo z11 turbo", "iqoo z11 turbo pro", "iqoo z11 turbo plus", "vivo v70e",
    "samsung galaxy s27 ultra 5g", "samsung galaxy s27 ultra", "samsung galaxy s27 pro",
    "samsung galaxy s27 5g", "samsung galaxy s27 plus 5g", "xiaomi 18 ultra",
    "xiaomi 18 5g", "oneplus 17", "oppo find x10 ultra", "xiaomi 18",
    "oppo find x10 pro max 5g", "vivo x300 ultra", "vivo x300 pro",
    "realme gt6 (china)", "oppo a5 (china)", "oppo a3 (china)", "oppo a3x (china)",
    "oppo a5 pro (china)", "vivo y38", "motorola s50 neo", "realme v60 pro",
    "realme gt neo6 se", "realme gt neo6"
}

# Exact model generation year anchors
MODEL_YEAR_ANCHORS = {
    's26': 2026, 's25': 2025, 's24': 2024, 's23': 2023, 's22': 2022, 's21': 2021, 's20': 2020,
    'iphone 18': 2026, 'iphone 17': 2025, 'iphone 16': 2024, 'iphone 15': 2023,
    'iphone 14': 2022, 'iphone 13': 2021, 'iphone 12': 2020, 'iphone 11': 2019, 'iphone x': 2017, 'iphone 8': 2017, 'iphone 7': 2016, 'iphone 6': 2014,
    'pixel 11': 2026, 'pixel 10': 2025, 'pixel 9': 2024, 'pixel 8': 2023, 'pixel 7': 2022,
    'pixel 6': 2021, 'pixel 5': 2020, 'pixel 4': 2019, 'pixel 3': 2018,
    'phone (3)': 2025, 'phone (2a)': 2024, 'phone (2)': 2023, 'phone (1)': 2022,
    'oneplus 13': 2024, 'oneplus 12': 2024, 'oneplus 11': 2023, 'oneplus 10': 2022,
    'oneplus 9': 2021, 'oneplus 8': 2020, 'oneplus 7': 2019, 'oneplus 6': 2018,
    'find x8': 2024, 'find x7': 2024, 'find x6': 2023, 'find x5': 2022,
    'x200': 2024, 'x100': 2023, 'x90': 2022, 'x80': 2022, 'x70': 2021, 'x60': 2021,
    'reno 13': 2025, 'reno 12': 2024, 'reno 11': 2024, 'reno 10': 2023, 'reno 9': 2022, 'reno 8': 2022,
    'redmi note 14': 2024, 'redmi note 13': 2024, 'redmi note 12': 2023, 'redmi note 11': 2022, 'redmi note 10': 2021
}

def clean_phone_name(brand: str, raw_name: str) -> str:
    if not raw_name:
        return ""
    name = str(raw_name).strip()
    
    # Fix explicit typos
    if name.lower().startswith('samaung '):
        name = 'Samsung ' + name[8:].strip()
        
    # Strip RAM/ROM spec patterns
    name = re.sub(r'\s*\(\d+GB\s+RAM\s*\+\s*\d+GB\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\(\d+GB\s*\+\s*\d+GB\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\(\d+GB\s+RAM\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\(\d+GB\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\(\d+MB\s+RAM\)', '', name, flags=re.IGNORECASE)
    
    # Clean whitespace
    name = ' '.join(name.split())
    
    # Ensure brand is capitalized correctly if at start
    brand_l = brand.strip().lower()
    words = name.split()
    if words:
        if len(words) >= 2 and words[0].lower() == brand_l and words[1].lower() == brand_l:
            words.pop(0)
            name = " ".join(words)
        elif not words[0].lower() == brand_l:
            # Add brand prefix if missing
            name = f"{brand} {name}"
            
    return name.strip()

# Connect to database
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT rowid, brand, name, price, price_numeric, os, source, released_in_india, launch_year, raw_specs FROM phones")
all_phones = cursor.fetchall()

print(f"\n[Step 2] Scanning {len(all_phones)} total phones in master database...")

# Buckets for reporting
pre_2023_phones = []
non_india_phones = []
upcoming_phones = []
valid_modern_india_phones = []

# List of DB update tuples
updates = []

for row in all_phones:
    row_id = row['rowid']
    brand_raw = str(row['brand'] or '').strip()
    name_raw = str(row['name'] or '').strip()
    price_str = row['price']
    price_num = row['price_numeric']
    os_str = str(row['os'] or '').strip()
    source = str(row['source'] or '').strip()
    launch_yr = row['launch_year']
    specs_str = row['raw_specs']
    
    specs = {}
    if specs_str:
        try:
            specs = json.loads(specs_str)
        except Exception:
            specs = {}
            
    # Clean Brand & Name
    clean_brand = BRAND_NORMALIZATION.get(brand_raw.lower(), brand_raw.capitalize() if brand_raw else 'Unknown')
    clean_name = clean_phone_name(clean_brand, name_raw)
    
    # Cross-reference keys
    key1 = (clean_brand.lower(), clean_name.lower())
    clean_model_only = clean_name
    if clean_name.lower().startswith(clean_brand.lower() + ' '):
        clean_model_only = clean_name[len(clean_brand)+1:].strip()
    key2 = (clean_brand.lower(), clean_model_only.lower())
    
    gsm_ref = gsm_map.get(key1) if key1 in gsm_map else gsm_map.get(key2)
    sp_ref = sp_map.get(key1) if key1 in sp_map else sp_map.get(key2)
    struct_ref = struct_map.get(key1) if key1 in struct_map else struct_map.get(key2)
    
    # ── 1. Accurately Resolve Launch Year ─────────────────────────────────────
    resolved_year = None
    
    # Specific known device corrections
    if 'vivo x100' in clean_name.lower():
        resolved_year = 2023
    elif 'vivo x200' in clean_name.lower():
        resolved_year = 2024
    elif 'vivo x90' in clean_name.lower():
        resolved_year = 2022
    elif 'vivo x80' in clean_name.lower():
        resolved_year = 2022
    elif 'samaung galaxy f70e' in name_raw.lower() or 'samsung galaxy f70e' in clean_name.lower():
        resolved_year = 2026
        
    # Check GSMArena Announced / Status
    if not resolved_year and gsm_ref is not None:
        ann = str(gsm_ref.get('launch_announced', ''))
        st = str(gsm_ref.get('launch_status', ''))
        ym = re.findall(r'\b(19\d\d|20\d\d)\b', f"{ann} {st}")
        if ym:
            valid_ym = [int(y) for y in ym if 1995 <= int(y) <= 2030]
            if valid_ym:
                resolved_year = max(valid_ym)
                
    # Check Smartprix Release Date / Year
    if not resolved_year and sp_ref is not None:
        sp_yr = sp_ref.get('Release_Year')
        sp_dt = str(sp_ref.get('Release_Date', ''))
        if pd.notna(sp_yr) and str(sp_yr).isdigit():
            resolved_year = int(sp_yr)
        elif sp_dt:
            ym = re.findall(r'\b(20\d\d)\b', sp_dt)
            if ym:
                resolved_year = int(ym[0])
                
    # Check Structured Dataset Launch Date
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
                        
    # Check Known Model Year Anchors
    if not resolved_year:
        name_l = clean_name.lower()
        for pat, yr in MODEL_YEAR_ANCHORS.items():
            if pat in name_l:
                resolved_year = yr
                break
                
    # Check explicit year in name: "Moto G (2025)" -> 2025
    if not resolved_year:
        ym = re.findall(r'\b(202\d|201\d|200\d)\b', clean_name)
        if ym:
            resolved_year = int(ym[0])
            
    # Fallback to existing launch_year
    if not resolved_year and launch_yr and 1995 <= launch_yr <= 2026:
        resolved_year = int(launch_yr)
        
    # Default for vintage/feature phones without year (e.g. Motorola Accompli, StarTAC, Samsung P940)
    if not resolved_year:
        if any(w in clean_name.lower() for w in ['startac', 'timeport', 'talkabout', 'accompli', 'v60', 'v50', 'c350', 'e398', 'mpx', 'guru', 'duos', 'metro 312', 'hero', 'kkt']):
            resolved_year = 2005
        else:
            resolved_year = 2024 # Modern default for recent catalog entries
            
    # ── 2. Accurately Resolve Price ──────────────────────────────────────────
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
            
    # ── 3. Detect Feature Phones / Keypad Devices ─────────────────────────────
    is_feature_phone = False
    feature_patterns = [
        'kaios', 'symbian', 'java', 'proprietary', 'feature phone', 'keypad', 'guru',
        'duos', 'keystone', 'metro 312', 'champ', 'kkt', 'hero 600', 'a1 tejas',
        'a3 power', 'rocker', 'tuf', 'c5212', 'e1100', 'e1200', 'star nano', 'c331',
        'c115', 'c116', 'c155', 'v171', 'v188', 'v226', 'startac', 'timeport', 'talkabout'
    ]
    if any(k in f"{clean_name} {os_str}".lower() for k in feature_patterns):
        is_feature_phone = True
    if resolved_price_num and resolved_price_num < 4500 and clean_brand.lower() in ['lava', 'samsung', 'hmd', 'nokia', 'itel']:
        is_feature_phone = True
        
    # ── 4. Detect Upcoming / Rumored / Future Phones ──────────────────────────
    is_upcoming = False
    status_text = ""
    if gsm_ref is not None:
        status_text += f" {gsm_ref.get('launch_announced', '')} {gsm_ref.get('launch_status', '')}"
    if sp_ref is not None:
        status_text += f" {sp_ref.get('Release_Date', '')} {sp_ref.get('Status', '')}"
    for k in ['status', 'Status', 'Launch Status', 'announced', 'Announced', 'General.Release Date', 'Release_Date']:
        if k in specs and specs[k]:
            status_text += f" {specs[k]}"
            
    st_lower = status_text.lower()
    if any(kw in st_lower for kw in ['rumored', 'rumoured', 'exp. release', 'exp. announcement', 'not yet announced', 'coming soon', 'expected launch']):
        is_upcoming = True
    if resolved_year and resolved_year > 2026:
        is_upcoming = True
    if any(ph in clean_name.lower() for ph in ['s27', 'xiaomi 18', 'pixel 11', 'iphone 18', 'find x10', 'y600 turbo', 'open 2', 'v fold']):
        is_upcoming = True
        
    # ── 5. Detect Non-India Devices ──────────────────────────────────────────
    is_not_in_india = False
    non_india_reason = ""
    
    if clean_brand.lower() in NON_INDIA_BRANDS:
        is_not_in_india = True
        non_india_reason = f"Brand '{clean_brand}' not active in Indian smartphone market"
    elif clean_name.lower() in NON_INDIA_MODELS or any(ph in clean_name.lower() for ph in ['(china)', 'china only']):
        is_not_in_india = True
        non_india_reason = "China-only or speculative unreleased model"
    elif source == 'AllPhones.csv' and not ('₹' in str(price_str) or 'india' in str(specs_str).lower() or sp_ref is not None):
        # Global phone with no Indian release / price
        is_not_in_india = True
        non_india_reason = "Global export without official Indian pricing"
        
    # ── 6. Final Category Classification & India Flag ────────────────────────
    # For a phone to be recommended in India:
    # - Must be released between 2023 and 2026
    # - Must NOT be upcoming / rumored
    # - Must NOT be a feature/keypad phone
    # - Must NOT be China/Global exclusive or discontinued/unsupported brand
    # - Must have a valid numeric price (>= ₹4,500)
    
    if resolved_year and resolved_year < 2023:
        # Pre-2023
        released_in_india_flag = 0
        pre_2023_phones.append({
            'id': row_id, 'brand': clean_brand, 'name': clean_name,
            'year': resolved_year, 'price': resolved_price_num, 'feature': is_feature_phone
        })
    elif is_upcoming:
        # Upcoming
        released_in_india_flag = 0
        upcoming_phones.append({
            'id': row_id, 'brand': clean_brand, 'name': clean_name,
            'year': resolved_year, 'price': resolved_price_num, 'status': st_lower[:60]
        })
    elif is_not_in_india or is_feature_phone or (resolved_price_num is None or resolved_price_num < 4500):
        # Not released in India / Feature / Missing Price
        released_in_india_flag = 0
        non_india_phones.append({
            'id': row_id, 'brand': clean_brand, 'name': clean_name,
            'year': resolved_year, 'price': resolved_price_num,
            'reason': non_india_reason or ('Feature/Keypad phone' if is_feature_phone else 'Price under ₹4,500 or unpriced')
        })
    else:
        # Confirmed Valid Modern Indian Smartphone (2023-2026)
        released_in_india_flag = 1
        valid_modern_india_phones.append({
            'id': row_id, 'brand': clean_brand, 'name': clean_name,
            'year': resolved_year, 'price': resolved_price_num
        })
        
    updates.append((
        clean_brand,
        clean_name,
        resolved_price_str,
        resolved_price_num,
        resolved_year,
        released_in_india_flag,
        row_id
    ))

print(f"\n[Step 3] Applying accurate updates across all {len(updates)} database records...")

# Apply updates in a transaction
cursor.executemany("""
    UPDATE phones
    SET brand = ?,
        name = ?,
        price = ?,
        price_numeric = ?,
        launch_year = ?,
        released_in_india = ?
    WHERE rowid = ?
""", updates)

conn.commit()
print("  -> Updated phones table successfully.")

# Rebuilding Full-Text Search Virtual Table (phones_fts)
print("\n[Step 4] Synchronizing FTS5 Full-Text Search Index...")
try:
    cursor.execute("DELETE FROM phones_fts")
    cursor.execute("INSERT INTO phones_fts(rowid, name, brand) SELECT rowid, name, brand FROM phones")
    conn.commit()
    print("  -> phones_fts search index fully rebuilt and synchronized.")
except Exception as e:
    print(f"  -> FTS Rebuild notice: {e}")

# ── Summary Report ────────────────────────────────────────────────────────────
print("\n================================================================================")
print("                           FINAL SCAN AUDIT REPORT                              ")
print("================================================================================")
print(f"Total Phones Scanned:                                     {len(all_phones)}")
print(f"--------------------------------------------------------------------------------")
print(f"1. Phones Released Before 2023 (Legacy / Vintage / Pre-2023): {len(pre_2023_phones):<6} (Flagged released_in_india=0)")
print(f"2. Phones Not Released in India (China / Global / Non-India): {len(non_india_phones):<6} (Flagged released_in_india=0)")
print(f"3. Phones Releasing Upcoming (Rumored / Unannounced concepts): {len(upcoming_phones):<6} (Flagged released_in_india=0)")
print(f"4. Confirmed Modern Smartphones in India (2023 - 2026):       {len(valid_modern_india_phones):<6} (Active released_in_india=1)")
print(f"================================================================================")

# Launch year distribution for active India phones
cursor.execute("SELECT launch_year, COUNT(*) as cnt FROM phones WHERE released_in_india = 1 GROUP BY launch_year ORDER BY launch_year DESC")
print("\nActive Indian Smartphone Launch Year Distribution:")
for r in cursor.fetchall():
    print(f"  • Year {int(r['launch_year'])}: {r['cnt']} phones")

# Verification of zero phantom 2027/pre-2023 in active pool
cursor.execute("SELECT COUNT(*) FROM phones WHERE released_in_india = 1 AND (launch_year < 2023 OR launch_year > 2026)")
invalid_active = cursor.fetchone()[0]
print(f"\nVerification Check: Phones with invalid launch year in active pool: {invalid_active} (Expected: 0)")

cursor.execute("SELECT COUNT(*) FROM phones WHERE released_in_india = 1 AND (price_numeric IS NULL OR price_numeric < 4500)")
invalid_prices = cursor.fetchone()[0]
print(f"Verification Check: Phones with invalid price (< ₹4,500) in active pool: {invalid_prices} (Expected: 0)")

conn.close()
print("\n✅ MASTER DATABASE SCAN, CURATION & SYNC COMPLETE!")
