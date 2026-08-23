import sqlite3
import json
import re
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('apps/api/data/phonos_ai.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT rowid, brand, name, price, price_numeric, os, source, released_in_india, launch_year, raw_specs FROM phones")
all_phones = cursor.fetchall()
print(f"Total phones in database: {len(all_phones)}")

typos = []
pre_2023_active = []
non_india_active = []
upcoming_active = []
price_anomalies = []
brand_distribution = {}
year_distribution = {}

# Brands that should be completely removed or disabled
DELETED_BRANDS = {
    'acer', 'wobble', 'ai+', 'sony', 'sharp', 'leitz', 'meizu', 'blu', 'kyocera',
    'archos', 'wiko', 'kazam', 'gigabyte', 'plum', 'verykool', 'alcatel', 'toshiba',
    'panasonic', 'yota', 'black shark', 'cat', 'coolpad', 'doogee', 'elephone',
    'fairphone', 'gionee', 'htc', 'huawei', 'leeco', 'letv', 'lg', 'micromax',
    'microsoft', 'oukitel', 'philips', 'tcl', 'ulefone', 'umidigi', 'unihertz', 'zte'
}

for r in all_phones:
    rowid = r['rowid']
    brand = str(r['brand'] or '')
    name = str(r['name'] or '')
    price_num = r['price_numeric']
    in_india = r['released_in_india']
    launch_yr = r['launch_year']
    os_val = str(r['os'] or '')
    specs_str = r['raw_specs']
    
    brand_distribution[brand] = brand_distribution.get(brand, 0) + 1
    yr_key = int(launch_yr) if launch_yr else 'NULL'
    year_distribution[yr_key] = year_distribution.get(yr_key, 0) + 1
    
    # Check typos
    if 'samaung' in name.lower() or 'samaung' in brand.lower():
        typos.append((rowid, brand, name, 'Typo Samaung'))
    if 'xiomi' in name.lower() or 'redme' in name.lower():
        typos.append((rowid, brand, name, 'Typo Xiaomi/Redmi'))
        
    # Check pre-2023 active
    if in_india == 1:
        if launch_yr and launch_yr < 2023:
            pre_2023_active.append((rowid, brand, name, launch_yr, price_num))
        # Check if year is in name or specs indicating pre-2023
        name_years = re.findall(r'\b(19\d\d|20[01]\d|202[012])\b', name)
        if name_years:
            pre_2023_active.append((rowid, brand, name, name_years[0], price_num))
            
        # Check feature phone active
        if any(kw in f"{name} {os_val}".lower() for kw in ['kkt', 'guru', 'duos', 'keystone', 'metro 312', 'champ', 'kaios', 'symbian', 'java', 'proprietary']):
            pre_2023_active.append((rowid, brand, name, 'Feature Phone', price_num))
            
        # Check upcoming active
        if any(kw in name.lower() for kw in ['s27', 'xiaomi 18', 'pixel 11', 'iphone 18', 'find x10', 'y600 turbo']):
            upcoming_active.append((rowid, brand, name, launch_yr, price_num))
            
        # Check non-india active
        if brand.lower() in DELETED_BRANDS:
            non_india_active.append((rowid, brand, name, 'Deleted/Non-India Brand', price_num))
        if any(kw in name.lower() for kw in ['(china)', 'china only', 'z11 turbo', 'v70e', 'x300 ultra', 'x300 pro']):
            non_india_active.append((rowid, brand, name, 'China only', price_num))
            
        # Check price anomalies
        if price_num is None or price_num <= 0:
            price_anomalies.append((rowid, brand, name, price_num))

print(f"\n--- Audit Summary ---")
print(f"Typos found: {len(typos)}")
for t in typos:
    print(f"  Row {t[0]}: {t[1]} - {t[2]} ({t[3]})")

print(f"\nPre-2023 / Feature phones currently active (released_in_india=1): {len(pre_2023_active)}")
for p in pre_2023_active[:15]:
    print(f"  Row {p[0]}: {p[1]} {p[2]} | Year/Type: {p[3]} | Price: ₹{p[4]}")

print(f"\nUpcoming / Concept phones currently active (released_in_india=1): {len(upcoming_active)}")
for p in upcoming_active[:15]:
    print(f"  Row {p[0]}: {p[1]} {p[2]} | Year: {p[3]} | Price: ₹{p[4]}")

print(f"\nNon-India / China-only / Deleted brands active (released_in_india=1): {len(non_india_active)}")
for p in non_india_active[:15]:
    print(f"  Row {p[0]}: {p[1]} {p[2]} | Reason: {p[3]} | Price: ₹{p[4]}")

print(f"\nActive phones with missing/0 price: {len(price_anomalies)}")
for p in price_anomalies[:15]:
    print(f"  Row {p[0]}: {p[1]} {p[2]} | Price: {p[3]}")

conn.close()
