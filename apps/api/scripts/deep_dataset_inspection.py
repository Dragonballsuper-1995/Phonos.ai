import sqlite3
import json
import os
import re

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'fone_master.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT rowid, brand, name, price, price_numeric, os, source, released_in_india, launch_year, raw_specs, ai_verified FROM phones")
rows = cursor.fetchall()
print(f"Total phones loaded: {len(rows)}")

sample_specs = None
all_raw_keys = set()
pre_2023 = []
upcoming_rumored = []
india_active_issues = []
brand_name_issues = []
price_issues = []
parsed_years = {}

for r in rows:
    row_id = r['rowid']
    brand = r['brand']
    name = r['name']
    price = r['price']
    price_num = r['price_numeric']
    source = r['source']
    rel_in_india = r['released_in_india']
    launch_yr = r['launch_year']
    specs_str = r['raw_specs']
    
    specs = {}
    if specs_str:
        try:
            specs = json.loads(specs_str)
            for k in specs.keys():
                all_raw_keys.add(k)
        except Exception as e:
            pass

    # Extract status / launch details from specs
    status_val = str(specs.get('status', '') or specs.get('Status', '') or specs.get('Launch Status', '') or '')
    announced_val = str(specs.get('announced', '') or specs.get('Announced', '') or specs.get('Launch Announced', '') or '')
    
    # Try to extract year from announced or name or specs
    detected_year = launch_yr
    year_match = re.search(r'\b(19\d\d|20\d\d)\b', f"{announced_val} {status_val} {name}")
    if year_match:
        y = int(year_match.group(1))
        parsed_years[y] = parsed_years.get(y, 0) + 1
        if detected_year is None:
            detected_year = y

    # Check for upcoming / rumored / unannounced
    is_upcoming = False
    status_lower = (status_val + ' ' + announced_val).lower()
    if any(kw in status_lower for kw in ['rumored', 'coming soon', 'exp. release', 'exp. announcement', 'not yet', 'expected']):
        is_upcoming = True
        upcoming_rumored.append((row_id, name, brand, detected_year, price_num, rel_in_india, status_lower[:60]))
    elif detected_year and detected_year > 2026:
        is_upcoming = True
        upcoming_rumored.append((row_id, name, brand, detected_year, price_num, rel_in_india, f"Future year {detected_year}"))

    # Check pre-2023
    if detected_year and detected_year < 2023:
        pre_2023.append((row_id, name, brand, detected_year, price_num, rel_in_india, announced_val))

    # Check price issues
    if price_num is None or price_num <= 0:
        price_issues.append((row_id, name, brand, price, price_num, rel_in_india))

    # Check brand in name duplication
    if brand and name and name.strip().lower().startswith(brand.strip().lower() + ' '):
        brand_name_issues.append((row_id, brand, name))

print(f"\nDiscovered Raw Specs Keys: {sorted(list(all_raw_keys))}")
print(f"\n--- Parsed Year Distribution across entire dataset ---")
for y in sorted(parsed_years.keys(), reverse=True):
    print(f"  Year {y}: {parsed_years[y]}")

print(f"\n--- Pre-2023 phones found ({len(pre_2023)}) ---")
for p in pre_2023[:15]:
    print(f"  ID: {p[0]} | {p[2]} {p[1]} | Year: {p[3]} | Price: {p[4]} | India: {p[5]} | Announced: {p[6]}")

print(f"\n--- Upcoming / Rumored phones found ({len(upcoming_rumored)}) ---")
for p in upcoming_rumored[:15]:
    print(f"  ID: {p[0]} | {p[2]} {p[1]} | Year: {p[3]} | Price: {p[4]} | India: {p[5]} | Status: {p[6]}")

print(f"\n--- Price Issues (None or <= 0) ({len(price_issues)}) ---")
for p in price_issues[:15]:
    print(f"  ID: {p[0]} | {p[2]} {p[1]} | PriceStr: {p[3]} | PriceNum: {p[4]} | India: {p[5]}")

print(f"\n--- Brand duplication in name count: {len(brand_name_issues)} ---")
for p in brand_name_issues[:10]:
    print(f"  ID: {p[0]} | Brand: '{p[1]}' | Name: '{p[2]}'")

conn.close()
