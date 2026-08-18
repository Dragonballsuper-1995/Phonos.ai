import sqlite3
import json
import re
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
DB_PATH = os.path.join(DATA_DIR, 'fone_master.db')

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("================================================================================")
print("  EXPLICIT MODEL-LEVEL GROUND TRUTH AUDIT & RECTIFICATION (AUGUST 16, 2026)    ")
print("================================================================================")

cursor.execute("SELECT rowid, brand, name, price, price_numeric, launch_year, source, raw_specs, released_in_india FROM phones")
all_phones = cursor.fetchall()
print(f"Total phones in database: {len(all_phones)}")

# ─── 1. EXPLICIT DISQUALIFICATION / EXCLUSION LIST ───────────────────────────
NON_INDIA_BRANDS = {
    'ai+', 'acer', 'wobble', 'sony', 'sharp', 'kyocera', 'archos', 'wiko',
    'leeco', 'letv', 'lg', 'htc', 'huawei', 'micromax', 'zte', 'alcatel',
    'panasonic', 'gionee', 'karbonn', 'intex', 'blackberry', 'cat'
}

# Exact substrings / patterns that MUST be flagged released_in_india = 0
EXCLUDED_EXACT_MODELS = [
    # Samsung unreleased
    "Galaxy S27", "Galaxy S28", "Z Fold 8", "Z Flip 8", "Z Fold8", "Z Flip8", "Z Tri Fold",
    # Apple unreleased
    "iPhone 18", "iPhone 19", "iPhone 20",
    # Xiaomi unreleased / non-India
    "Xiaomi 16", "Xiaomi 18", "Xiaomi 19", "Mix Fold", "Mix Flip", "Xiaomi Civi",
    # Vivo unreleased / China-only
    "Vivo X500", "Vivo X400", "Vivo X450", "Vivo S18", "Vivo S19", "Vivo S20", "Vivo S50", "Vivo U5x",
    # Oppo non-India foldables & unreleased
    "Find N4", "Find N5", "Find N6", "Oppo Tri Fold", "Oppo F33",
    # Motorola unreleased / invalid
    "Moto X70", "Moto G56", "Moto G57", "Moto G06", "Razr 70 Plus",
    # POCO non-India / unreleased
    "POCO F8 Ultra", "Poco F8 Ultra", "Poco C66", "Poco C63", "Poco C77",
    # OnePlus unreleased / China-only
    "OnePlus 14", "OnePlus 15", "OnePlus 16", "OnePlus 17", "OnePlus Ace", "OnePlus Open 2", "OnePlus V Fold",
    # Realme China-only
    "Realme GT 9", "Realme GT 8", "Realme GT 7", "Realme V70", "Realme V60", "Realme Narzo N57",
    # China imports
    "(China)", "China only", "China Edition"
]

# ─── 2. EXPLICIT CONFIRMED INDIA MODEL PATTERNS (2023 - AUG 2026) ─────────────
CONFIRMED_INDIA_MODELS = [
    # Samsung
    "Galaxy S26", "Galaxy S26+", "Galaxy S26 Ultra",
    "Galaxy S25", "Galaxy S25+", "Galaxy S25 Ultra", "Galaxy S25 FE", "Galaxy S25 Edge",
    "Galaxy S24", "Galaxy S24+", "Galaxy S24 Ultra", "Galaxy S24 FE",
    "Galaxy S23", "Galaxy S23+", "Galaxy S23 Ultra", "Galaxy S23 FE",
    "Z Fold 7", "Z Fold7", "Z Flip 7", "Z Flip7", "Z Fold 6", "Z Flip 6", "Z Fold 5", "Z Flip 5",
    "Galaxy A55", "Galaxy A35", "Galaxy A15", "Galaxy A16", "Galaxy A54", "Galaxy A34",
    "Galaxy M55", "Galaxy M35", "Galaxy M15", "Galaxy M54", "Galaxy M34", "Galaxy M14",
    "Galaxy F55", "Galaxy F15", "Galaxy F54", "Galaxy F34", "Galaxy F14",

    # Apple
    "iPhone 17", "iPhone 17 Pro", "iPhone 17 Pro Max", "iPhone Air",
    "iPhone 16", "iPhone 16 Plus", "iPhone 16 Pro", "iPhone 16 Pro Max",
    "iPhone 15", "iPhone 15 Plus", "iPhone 15 Pro", "iPhone 15 Pro Max",
    "iPhone 14", "iPhone 14 Plus", "iPhone 14 Pro", "iPhone 14 Pro Max", "iPhone SE",

    # Xiaomi & Redmi
    "Xiaomi 17", "Xiaomi 17 Ultra", "Xiaomi 17T",
    "Xiaomi 15", "Xiaomi 15 Pro", "Xiaomi 14", "Xiaomi 14 Ultra", "Xiaomi 14 Civi", "Xiaomi 13 Pro",
    "Redmi Note 17", "Redmi Note 15", "Redmi Note 15 Pro+", "Redmi Note 15 Pro",
    "Redmi Note 14", "Redmi Note 14 Pro+", "Redmi Note 14 Pro", "Redmi Note 13", "Redmi Note 13 Pro", "Redmi Note 13 Pro+",
    "Redmi Note 12", "Redmi Note 12 Pro", "Redmi 15", "Redmi 14", "Redmi 13", "Redmi 13C", "Redmi 12",

    # Vivo
    "Vivo V70", "Vivo V60", "Vivo V50", "Vivo V40", "Vivo V40 Pro", "Vivo V30", "Vivo V30 Pro", "Vivo V29", "Vivo V27",
    "Vivo X300", "Vivo X300 Pro", "Vivo X300 FE",
    "Vivo X200", "Vivo X200 Pro", "Vivo X200 FE", "Vivo X100", "Vivo X100 Pro", "Vivo X90", "Vivo X90 Pro",
    "Vivo T3", "Vivo T3x", "Vivo T3 Pro", "Vivo T4x", "Vivo T2", "Vivo T2x",
    "Vivo Y200", "Vivo Y28", "Vivo Y18", "Vivo Y58", "Vivo Y19s",

    # OPPO
    "Reno 15", "Reno 15 Pro", "Reno 14", "Reno 14 Pro", "Reno 13", "Reno 13 Pro",
    "Reno 12", "Reno 12 Pro", "Reno 11", "Reno 11 Pro", "Reno 10", "Reno 10 Pro",
    "Find N3 Flip", "Find N2 Flip", "Find N3",
    "Oppo F27", "Oppo F27 Pro", "Oppo F27 Pro+", "Oppo F25 Pro", "Oppo F23",
    "Oppo A79", "Oppo A78", "Oppo A3 Pro",

    # Motorola
    "Edge 70", "Edge 70 Pro", "Edge 70 Fusion", "Edge 70 Pro Plus", "Edge 70 Max",
    "Edge 60", "Edge 60 Pro", "Edge 60 Fusion", "Edge 60 Stylus", "Edge 60s",
    "Edge 50", "Edge 50 Pro", "Edge 50 Fusion", "Edge 50 Ultra", "Edge 50 Neo",
    "Edge 40", "Edge 40 Neo", "Edge 40 Pro",
    "Razr 70", "Razr 70 Ultra", "Razr 60", "Razr 60 Ultra", "Razr 50", "Razr 50 Ultra", "Razr 40", "Razr 40 Ultra",
    "Moto G96", "Moto G87", "Moto G85", "Moto G64", "Moto G54", "Moto G45", "Moto G34", "Moto G24", "Moto G04",

    # POCO
    "POCO F8", "POCO F8 Pro", "POCO F7", "POCO F6", "POCO F6 Pro", "POCO F5", "POCO F5 Pro",
    "POCO X6", "POCO X6 Pro", "POCO X5", "POCO X5 Pro",
    "POCO M8", "POCO M7", "POCO M6", "POCO M6 Pro",
    "POCO C85", "POCO C75", "POCO C71", "POCO C65",

    # OnePlus
    "OnePlus 13", "OnePlus 13R", "OnePlus 12", "OnePlus 12R", "OnePlus 11", "OnePlus 11R",
    "OnePlus Open",
    "OnePlus Nord 4", "OnePlus Nord 3", "OnePlus Nord CE 4", "OnePlus Nord CE 4 Lite", "OnePlus Nord CE 3",

    # Google Pixel
    "Pixel 9", "Pixel 9 Pro", "Pixel 9 Pro XL", "Pixel 9 Pro Fold",
    "Pixel 8", "Pixel 8a", "Pixel 8 Pro", "Pixel 7a", "Pixel 7", "Pixel 7 Pro",

    # Nothing / CMF
    "Nothing Phone (3)", "Nothing Phone (3a)", "Nothing Phone (3a) Pro",
    "Nothing Phone (2)", "Nothing Phone (2a)", "Nothing Phone (2a) Plus",
    "CMF Phone 1", "CMF Phone 2",

    # iQOO
    "iQOO 13", "iQOO 12", "iQOO 11", "iQOO 9",
    "iQOO Neo 10", "iQOO Neo 9 Pro", "iQOO Neo 7", "iQOO Neo 7 Pro",
    "iQOO Z9", "iQOO Z9x", "iQOO Z9s", "iQOO Z9s Pro", "iQOO Z7", "iQOO Z7 Pro",

    # Realme
    "Realme GT 6", "Realme GT 6T", "Realme GT 5",
    "Realme 13", "Realme 13 Pro", "Realme 13 Pro+", "Realme 13+",
    "Realme 12", "Realme 12 Pro", "Realme 12 Pro+", "Realme 12x", "Realme 12 4G",
    "Realme 14x", "Realme 14 Pro", "Realme 14 Pro+",
    "Realme 11", "Realme 11 Pro", "Realme 11 Pro+",
    "Realme P2 Pro", "Realme P1", "Realme P1 Pro", "Realme P1 Speed",
    "Realme Narzo 70", "Realme Narzo 70 Pro", "Realme Narzo 70 Turbo", "Realme Narzo 70x", "Realme Narzo 60",

    # Lava & Infinix & Tecno
    "Lava Agni 3", "Lava Agni 2", "Lava Blaze Curve", "Lava Blaze 2", "Lava Yuva 3",
    "Infinix GT 20 Pro", "Infinix GT 10 Pro", "Infinix Zero 30", "Infinix Note 40 Pro", "Infinix Note 40",
    "Tecno Camon 30", "Tecno Camon 30 Premier", "Tecno Camon 20", "Tecno Pova 6 Pro", "Tecno Phantom V Fold"
]

# Compile exclusion checks
compiled_exclusions = [re.compile(re.escape(x), re.IGNORECASE) for x in EXCLUDED_EXACT_MODELS]
compiled_confirmed = [re.compile(re.escape(c), re.IGNORECASE) for c in CONFIRMED_INDIA_MODELS]

updated_count = 0
active_models_list = []
excluded_models_list = []

for r in all_phones:
    row_id = r['rowid']
    name = str(r['name'] or '').strip()
    brand = str(r['brand'] or '').strip()
    price_num = r['price_numeric']
    launch_yr = r['launch_year']
    specs_str = str(r['raw_specs'] or '')
    
    # 1. Check if explicitly excluded
    is_excluded = False
    exclude_reason = ""
    
    if brand.lower() in NON_INDIA_BRANDS:
        is_excluded = True
        exclude_reason = f"Brand '{brand}' not an active Indian smartphone brand"
        
    if not is_excluded:
        for pat in compiled_exclusions:
            if pat.search(name):
                is_excluded = True
                exclude_reason = f"Explicit unreleased/China model pattern: '{pat.pattern}'"
                break
            
    if not is_excluded:
        # Check raw specs for 'expected' / 'rumored'
        if any(w in specs_str.lower() for w in ['expected', 'rumor', 'rumoured', 'not yet announced', 'coming soon. exp.']):
            is_excluded = True
            exclude_reason = "Raw specs indicate unreleased / expected status"
            
    if not is_excluded:
        # Check year bounds
        if launch_yr and (launch_yr < 2023 or launch_yr > 2026):
            is_excluded = True
            exclude_reason = f"Launch year {launch_yr} outside active 2023-2026 window"
            
    if not is_excluded:
        # Check price bounds
        if price_num is None or price_num < 4500:
            is_excluded = True
            exclude_reason = "Price missing or below smartphone floor (< ₹4,500)"

    # 2. Positive Verification: Match against confirmed India catalog
    is_confirmed_india = False
    if not is_excluded:
        for pat in compiled_confirmed:
            if pat.search(name):
                is_confirmed_india = True
                break
                
        # If not explicitly matched but mainstream brand with clean specs, check if valid
        if not is_confirmed_india:
            # If from Smartprix with verified INR price and modern launch year (2023-2026)
            if r['source'] == 'Smartprix' and '₹' in str(r['price']) and not any(w in name.lower() for w in ['air', 'tri fold', 'x70', 'g56', 'g57']):
                is_confirmed_india = True

    final_india_flag = 1 if (is_confirmed_india and not is_excluded) else 0
    
    cursor.execute("UPDATE phones SET released_in_india = ? WHERE rowid = ?", (final_india_flag, row_id))
    
    if final_india_flag == 1:
        active_models_list.append((row_id, brand, name, price_num, launch_yr))
    else:
        excluded_models_list.append((row_id, brand, name, price_num, exclude_reason or "Unverified model"))

conn.commit()

# Re-synchronize Full-Text Search index (phones_fts)
cursor.execute("DELETE FROM phones_fts")
cursor.execute("INSERT INTO phones_fts(rowid, name, brand) SELECT rowid, name, brand FROM phones")
conn.commit()

print(f"\nAudit complete!")
print(f"  • Confirmed & Active India Released Smartphones: {len(active_models_list)}")
print(f"  • Excluded / Unreleased / Global Devices:        {len(excluded_models_list)}")

print("\n--- Verified Active Models Breakdown by Brand ---")
cursor.execute("SELECT brand, COUNT(*) as cnt FROM phones WHERE released_in_india = 1 GROUP BY brand ORDER BY cnt DESC")
for r in cursor.fetchall():
    print(f"  • {r['brand']}: {r['cnt']} phones")

conn.close()
