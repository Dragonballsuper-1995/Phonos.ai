import sqlite3
import pandas as pd
import json
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
DB_PATH = os.path.join(DATA_DIR, 'phonos_ai.db')

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Load raw GSMArena to create a lookup map
print("Loading raw_gsmarena lookup...")
gsm_df = pd.read_csv(os.path.join(DATA_DIR, 'raw_gsmarena.csv'), low_memory=False)
print(f"GSM rows: {len(gsm_df)}")

# Create normalized lookup dictionary: (brand.lower(), model_clean.lower()) -> gsm_row
gsm_lookup = {}
for idx, row in gsm_df.iterrows():
    oem = str(row['oem']).strip().lower() if pd.notna(row['oem']) else ''
    model = str(row['model']).strip().lower() if pd.notna(row['model']) else ''
    if oem and model:
        # Also clean model if it starts with oem
        model_cleaned = model
        if model.startswith(oem + ' '):
            model_cleaned = model[len(oem)+1:].strip()
        gsm_lookup[(oem, model)] = row
        gsm_lookup[(oem, model_cleaned)] = row

print(f"GSM lookup populated with {len(gsm_lookup)} entries.")

cursor.execute("SELECT rowid, brand, name, price, price_numeric, os, source, released_in_india, launch_year, raw_specs FROM phones")
all_phones = cursor.fetchall()
print(f"Master phones count: {len(all_phones)}")

matched_gsm = 0
found_years_gsm = 0

for p in all_phones:
    brand = str(p['brand']).strip().lower()
    name = str(p['name']).strip().lower()
    # clean name if it starts with brand
    name_clean = name
    if name.startswith(brand + ' '):
        name_clean = name[len(brand)+1:].strip()
        
    gsm_data = gsm_lookup.get((brand, name)) or gsm_lookup.get((brand, name_clean))
    if gsm_data is not None:
        matched_gsm += 1
        announced = str(gsm_data['launch_announced'])
        status = str(gsm_data['launch_status'])
        # check if year found
        y_m = re.findall(r'\b(19\d\d|20\d\d)\b', f"{announced} {status}")
        if y_m:
            found_years_gsm += 1

print(f"Matched with GSMArena: {matched_gsm} / {len(all_phones)}")
print(f"Years extractable from GSMArena: {found_years_gsm}")

conn.close()
