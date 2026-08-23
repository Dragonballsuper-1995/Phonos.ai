import sqlite3
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'phonos_ai.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Group by source
cursor.execute("SELECT source, COUNT(*) as cnt, COUNT(launch_year) as with_year FROM phones GROUP BY source")
print("=== Sources breakdown ===")
for r in cursor.fetchall():
    print(f"Source: {r['source']} | Total: {r['cnt']} | With launch_year: {r['with_year']}")

# Let's inspect AllPhones.csv phones specs keys
cursor.execute("SELECT rowid, brand, name, price, price_numeric, os, source, released_in_india, launch_year, raw_specs FROM phones WHERE source LIKE '%AllPhones%' LIMIT 10")
rows = cursor.fetchall()
print("\n=== Sample AllPhones.csv records ===")
for r in rows:
    d = dict(r)
    specs = json.loads(d['raw_specs']) if d['raw_specs'] else {}
    print(f"\nID={d['rowid']} | Brand={d['brand']} | Name={d['name']} | Price={d['price_numeric']}")
    # print keys that might have dates
    for k, v in specs.items():
        if any(w in k.lower() for w in ['date', 'year', 'month', 'launch', 'announce', 'status', 'time']):
            print(f"  {k}: {v}")

conn.close()
