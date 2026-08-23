import sqlite3
import pandas as pd
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('apps/api/data/phonos_ai.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT rowid, brand, name, price, price_numeric, os, source, released_in_india, launch_year, raw_specs FROM phones WHERE price_numeric IS NULL AND released_in_india = 1")
rows = cursor.fetchall()
print(f"Total active India phones with NULL price: {len(rows)}")

for r in rows:
    name = r['name']
    brand = r['brand']
    specs = json.loads(r['raw_specs']) if r['raw_specs'] else {}
    print(f"ID={r['rowid']} | Brand={brand} | Name={name}")

conn.close()
