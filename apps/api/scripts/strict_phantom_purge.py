import sqlite3
import json
import re
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
DB_PATH = os.path.join(DATA_DIR, 'phonos_ai.db')

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("================================================================================")
print("     STRICT VALIDATION & PURGE OF PHANTOM / CHINA-ONLY / UNRELEASED PHONES      ")
print("================================================================================")

cursor.execute("SELECT rowid, brand, name, price, price_numeric, launch_year, source, raw_specs, released_in_india FROM phones")
all_phones = cursor.fetchall()
print(f"Total phones in DB: {len(all_phones)}")

# Definite patterns that DO NOT exist in India or are speculative concept models
PHANTOM_AND_NON_INDIA_PATTERNS = [
    # China-only series
    r'\bMix Fold\b', r'\bMix Flip\b', r'\bXiaomi Civi\b',
    r'\bVivo S\d+', r'\bVivo S1\d', r'\bVivo S2\d', r'\bVivo S3\d', r'\bVivo S4\d', r'\bVivo S5\d', # Vivo S-series is China only
    r'\bRealme V\d+', r'\bRealme Q\d+', # Realme V and Q series are China only
    r'\bOnePlus Ace\b', r'\bOnePlus V Fold\b', r'\bOnePlus Open 2\b',
    r'\biQOO Z\d+ Turbo\b', r'\biQOO Neo\s*\d+\s*SE\b',
    r'\(China\)', r'China only', r'China Edition',
    
    # Speculative / Unreleased Future Generations
    r'Samsung Galaxy S2[6-9]', r'Galaxy S2[6-9]',
    r'Galaxy Z Fold [7-9]', r'Galaxy Z Flip [7-9]',
    r'iPhone 1[7-9]', r'iPhone 2\d', r'iPhone Air', r'iPhone Ultra',
    r'Pixel 1[0-9]', r'Pixel 2\d',
    r'Xiaomi 1[6-9]', r'Xiaomi 2\d', r'Redmi Note 1[5-9]', r'Redmi 1[5-9]',
    r'OnePlus 1[4-9]', r'OnePlus 2\d',
    r'Vivo V[5-9]\d', r'Vivo V[1-9]\d\d', r'Vivo X[3-9]\d\d', r'Vivo X5\d\d', r'Vivo Y[6-9]\d\d', r'Vivo X Fold [4-9]',
    r'Oppo Reno 1[3-9]', r'Oppo Reno [2-9]\d', r'Oppo Find X[8-9]', r'Oppo Find X1\d', r'Oppo Find N[4-9]', r'Oppo A[6-9]',
    r'Realme 1[4-9]', r'Realme 2\d', r'Realme GT [7-9]', r'Realme GT Neo [7-9]', r'Realme C[7-9]\d', r'Realme P[3-9]', r'Realme Narzo [8-9]\d',
    r'Moto X7\d', r'Moto X[8-9]\d', r'Edge 6\d', r'Edge 7\d', r'Razr 6\d', r'Razr 7\d', r'Moto G[6-9]\d', r'Moto G57', r'Moto G06', r'Moto S5\d',
    r'Poco F[7-9]', r'Poco X[7-9]', r'Poco M[7-9]', r'Poco C[7-9]\d', r'Poco C7\d', r'Poco C8\d'
]

compiled_patterns = [re.compile(p, re.IGNORECASE) for p in PHANTOM_AND_NON_INDIA_PATTERNS]

purged_count = 0
purged_list = []

for row in all_phones:
    row_id = row['rowid']
    name = str(row['name'] or '')
    brand = str(row['brand'] or '')
    specs_str = str(row['raw_specs'] or '')
    in_india = row['released_in_india']
    
    is_phantom = False
    reason = ""
    
    # Check 1: Match against regex patterns
    for p in compiled_patterns:
        m = p.search(name)
        if m:
            is_phantom = True
            reason = f"Matches speculative pattern: '{m.group(0)}'"
            break
            
    # Check 2: Check raw specs for explicit 'expected' / 'rumored' / 'unannounced'
    if not is_phantom and in_india == 1:
        specs_lower = specs_str.lower()
        if any(w in specs_lower for w in ['(expected)', 'expected release', 'exp. release', 'rumored', 'rumoured', 'not officially announced', 'coming soon. exp.']):
            is_phantom = True
            reason = "Raw specs contain unreleased / expected release date"
            
    # Check 3: Launch year > 2025
    launch_yr = row['launch_year']
    if not is_phantom and launch_yr and launch_yr > 2025:
        # Check if it's already past June 2026 or a fake future date
        # If it's tagged 2026 but has 'expected' or high model numbering
        if '2026' in str(launch_yr) and ('expected' in specs_str.lower() or 'rumor' in specs_str.lower()):
            is_phantom = True
            reason = f"Future concept tagged year {launch_yr}"
            
    if is_phantom and in_india == 1:
        purged_count += 1
        purged_list.append((row_id, brand, name, row['price_numeric'], reason))
        cursor.execute("UPDATE phones SET released_in_india = 0 WHERE rowid = ?", (row_id,))

conn.commit()

# Synchronize FTS5 Search table
cursor.execute("DELETE FROM phones_fts")
cursor.execute("INSERT INTO phones_fts(rowid, name, brand) SELECT rowid, name, brand FROM phones")
conn.commit()

print(f"\nSuccessfully purged {purged_count} speculative/phantom/China-only devices from India active pool.")
print(f"\nSample 30 Purged Devices:")
for p in purged_list[:30]:
    print(f"  [PURGED] ID={p[0]} | {p[1]} {p[2]} | ₹{p[3]} | Reason: {p[4]}")

cursor.execute("SELECT COUNT(*) FROM phones WHERE released_in_india = 1")
remaining_active = cursor.fetchone()[0]
print(f"\nTotal Verified, Genuine, Modern Indian Smartphones Remaining: {remaining_active}")

# Check breakdown by brand for remaining active
cursor.execute("SELECT brand, COUNT(*) as cnt FROM phones WHERE released_in_india = 1 GROUP BY brand ORDER BY cnt DESC")
print("\nCleaned Active Indian Smartphone Count by Brand:")
for r in cursor.fetchall():
    print(f"  • {r['brand']}: {r['cnt']} phones")

conn.close()
