import sqlite3
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('apps/api/data/phonos_ai.db')
c = conn.cursor()
c.execute('SELECT rowid, brand, name FROM phones')
rows = c.fetchall()

dup_count = 0
for rowid, brand, name in rows:
    if not name or not brand:
        continue
    words = name.strip().split()
    if len(words) >= 2 and words[0].lower() == words[1].lower():
        dup_count += 1
        if dup_count <= 10:
            print(f"Row {rowid}: brand='{brand}', name='{name}'")

print(f"\nTotal names with consecutive duplicate words (e.g. 'Samsung Samsung'): {dup_count}")

# Check if name doesn't start with brand
no_brand_prefix = 0
for rowid, brand, name in rows:
    if not name or not brand:
        continue
    if not name.lower().startswith(brand.lower()):
        no_brand_prefix += 1
        if no_brand_prefix <= 5:
            print(f"No brand prefix: brand='{brand}', name='{name}'")

print(f"Total names not starting with brand: {no_brand_prefix}")

conn.close()
