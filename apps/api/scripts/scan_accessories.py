import sqlite3
import re
import glob
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

db_path = 'data/fone_master.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Patterns of non-smartphone junk:
junk_patterns = [
    r'\b(?:adapter|charger|cable|cooling|clip|smart pen|type-c|hub|power adapter|supervooc cable)\b',
    r'\b(?:care\+|coins|vip|reward|benefits|next ai|ui|series|phones|magnetic|exchange|upgrade|warranty)\b',
    r'^(?:ow|new|phones|realme|oppo|vivo|xiaomi|samsung|apple|oneplus|iqoo|narzo)$',
    r'\b(?:buds|earbuds|tws|headphone|earphone|watch|band|strap|case|cover)\b',
]

combined_regex = re.compile('|'.join(junk_patterns), re.IGNORECASE)

rows = cursor.execute("SELECT rowid, brand, name, price FROM phones").fetchall()
matched_rows = []
for r in rows:
    name = (r[2] or '').strip()
    if combined_regex.search(name) or len(name) <= 2:
        matched_rows.append(r)

print(f"Total matching non-smartphone / scrap rows found in DB: {len(matched_rows)}")
for r in matched_rows[:35]:
    print(f"  ID {r[0]}: [{r[1]}] '{r[2]}' (Price: {r[3]})")

print("\n--- Scanning CSV files ---")
csv_files = glob.glob('../../scraped_official_catalogues/*.csv') + glob.glob('data/*.csv')
for f in csv_files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            lines = fp.readlines()
        junk_lines = [line.strip() for line in lines if combined_regex.search(line)]
        if junk_lines:
            print(f"File {f}: Found {len(junk_lines)} matching junk lines. Samples: {junk_lines[:5]}")
