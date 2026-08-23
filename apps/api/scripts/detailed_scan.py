import sqlite3
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('apps/api/data/phonos_ai.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT rowid, brand, name, price, price_numeric, os, source, released_in_india, launch_year, raw_specs FROM phones")
all_phones = cursor.fetchall()

print(f"Total phones in DB: {len(all_phones)}")

# Let's inspect phone models, specs, dates, and identify all anomalies
pre_2023_list = []
upcoming_list = []
non_india_active = []
weird_price_list = []
name_duplication_list = []
feature_phones_list = []

for r in all_phones:
    rowid = r['rowid']
    brand = r['brand']
    name = r['name']
    price = r['price']
    price_num = r['price_numeric']
    os_val = r['os'] or ''
    source = r['source']
    in_india = r['released_in_india']
    launch_yr = r['launch_year']
    raw_specs_str = r['raw_specs']
    
    specs = {}
    if raw_specs_str:
        try:
            specs = json.loads(raw_specs_str)
        except Exception:
            pass
            
    # Check all fields for launch/release date
    rel_date = specs.get('Release_Date') or specs.get('General.Release Date') or specs.get('Release Date') or specs.get('release_date') or ''
    rel_year = specs.get('Release_Year') or specs.get('Release Year')
    status_str = specs.get('status') or specs.get('Status') or specs.get('Launch Status') or ''
    announced_str = specs.get('announced') or specs.get('Announced') or specs.get('Launch Announced') or ''
    
    all_text = f"{name} {rel_date} {rel_year} {status_str} {announced_str} {os_val}"
    
    # Try finding exact year
    year = launch_yr
    if not year or year < 1900:
        # search in name or rel_date
        m = re.findall(r'\b(19\d\d|20\d\d)\b', f"{rel_date} {announced_str} {name}")
        if m:
            year = int(m[0])
            
    # Check pre-2023
    if year and year < 2023:
        pre_2023_list.append((rowid, brand, name, year, in_india, price_num, source))
        
    # Check upcoming / rumors / future
    is_upcoming = False
    status_ann_lower = f"{status_str} {announced_str} {name} {rel_date}".lower()
    if any(k in status_ann_lower for k in ['rumored', 'rumoured', 'exp. release', 'exp. announcement', 'expected launch', 'upcoming', 'coming soon', 'not yet announced']):
        is_upcoming = True
    if year and year > 2026:
        is_upcoming = True
    if is_upcoming:
        upcoming_list.append((rowid, brand, name, year, in_india, price_num, status_ann_lower[:50]))
        
    # Check feature / keypad phones
    is_feature = False
    if any(k in f"{name} {os_val}".lower() for k in ['kaios', 'symbian', 'java', 'proprietary', 'feature phone', 'keypad', 'guru', 'duos', 'keystone', 'metro 312', 'champ', 'kkt']):
        is_feature = True
        feature_phones_list.append((rowid, brand, name, year, in_india, price_num, os_val))
        
    # Check name duplication (e.g. Samsung Samsung Galaxy)
    if brand and name and name.strip().lower().startswith(brand.strip().lower() + ' '):
        # e.g. "Samsung Samsung Galaxy" vs "Samsung Galaxy"
        # If the second word is also the brand:
        words = name.strip().split()
        if len(words) > 1 and words[0].lower() == words[1].lower():
            name_duplication_list.append((rowid, brand, name))

print(f"\n1. Pre-2023 phones: {len(pre_2023_list)} found")
for p in pre_2023_list[:10]:
    print(f"   ID={p[0]} | {p[1]} | {p[2]} | Year={p[3]} | India={p[4]} | Price={p[5]}")

print(f"\n2. Upcoming / Rumored / Concept phones: {len(upcoming_list)} found")
for p in upcoming_list[:10]:
    print(f"   ID={p[0]} | {p[1]} | {p[2]} | Year={p[3]} | India={p[4]} | Price={p[5]} | Status={p[6]}")

print(f"\n3. Feature / Legacy Keypad phones: {len(feature_phones_list)} found")
for p in feature_phones_list[:10]:
    print(f"   ID={p[0]} | {p[1]} | {p[2]} | Year={p[3]} | India={p[4]} | Price={p[5]} | OS={p[6]}")

print(f"\n4. Exact double brand prefix (e.g. 'Samsung Samsung ...'): {len(name_duplication_list)} found")
for p in name_duplication_list[:10]:
    print(f"   ID={p[0]} | Brand='{p[1]}' | Name='{p[2]}'")

conn.close()
