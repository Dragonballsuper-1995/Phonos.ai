import sqlite3
import json
import os
import re

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'phonos_ai.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT rowid, brand, name, price, price_numeric, os, source, released_in_india, launch_year, raw_specs, ai_verified FROM phones")
rows = cursor.fetchall()

release_dates_sample = []
years_from_all_sources = {}
future_phones = []
legacy_phones = []
no_release_info = []

for r in rows:
    row_id = r['rowid']
    brand = r['brand']
    name = r['name']
    price = r['price']
    price_num = r['price_numeric']
    launch_yr = r['launch_year']
    specs_str = r['raw_specs']
    
    specs = {}
    if specs_str:
        try:
            specs = json.loads(specs_str)
        except Exception:
            pass

    rel_date = specs.get('Release_Date') or specs.get('General.Release Date') or specs.get('Release Date') or specs.get('release_date') or ''
    rel_year = specs.get('Release_Year') or specs.get('Release Year')
    
    # Try finding year from everywhere
    text_to_search = f"{name} {rel_date} {rel_year} {launch_yr} {specs.get('Last modified', '')} {specs.get('Last_Modified_Date', '')}"
    
    # Look for 4 digit year 1990-2035
    found_years = re.findall(r'\b(19\d\d|20\d\d)\b', text_to_search)
    best_year = None
    if rel_year and str(rel_year).isdigit():
        best_year = int(rel_year)
    elif launch_yr:
        best_year = int(launch_yr)
    elif rel_date:
        y_match = re.search(r'\b(19\d\d|20\d\d)\b', str(rel_date))
        if y_match:
            best_year = int(y_match.group(1))
    elif found_years:
        best_year = int(found_years[0])
        
    if best_year:
        years_from_all_sources[best_year] = years_from_all_sources.get(best_year, 0) + 1
        if best_year < 2023:
            legacy_phones.append((row_id, brand, name, best_year, price_num, r['released_in_india'], rel_date))
        elif best_year > 2026:
            future_phones.append((row_id, brand, name, best_year, price_num, r['released_in_india'], rel_date))
    else:
        no_release_info.append((row_id, brand, name, price_num, r['released_in_india']))

print(f"Total phones: {len(rows)}")
print(f"Years found across all sources:")
for y in sorted(years_from_all_sources.keys(), reverse=True):
    print(f"  {y}: {years_from_all_sources[y]}")

print(f"Phones with NO year detected: {len(no_release_info)}")

print(f"\n--- Phones with Year > 2026 (Future/Upcoming concepts) ({len(future_phones)}) ---")
for p in future_phones[:25]:
    print(f"  ID: {p[0]} | {p[1]} {p[2]} | Year: {p[3]} | Price: {p[4]} | India: {p[5]} | Date: {p[6]}")

print(f"\n--- Phones with Year < 2023 (Legacy) ({len(legacy_phones)}) ---")
for p in legacy_phones[:25]:
    print(f"  ID: {p[0]} | {p[1]} {p[2]} | Year: {p[3]} | Price: {p[4]} | India: {p[5]} | Date: {p[6]}")

conn.close()
