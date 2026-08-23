import sqlite3
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect('data/phonos_ai.db')
cursor = conn.cursor()

print("--- Searching for 'ow' or 'realme ow' in DB ---")
rows = cursor.execute("SELECT rowid, brand, name, price, raw_specs FROM phones WHERE name LIKE '%ow%' OR brand LIKE '%ow%'").fetchall()
print(f"Found {len(rows)} matching rows:")
for r in rows:
    if len(r[2].strip()) <= 10 or 'ow' in r[2].lower():
        print(f"  ID {r[0]}: [{r[1]}] '{r[2]}' (Price: {r[3]})")

print("\n--- Checking Realme P4 Power variants ---")
p4_rows = cursor.execute("SELECT rowid, brand, name, price, raw_specs FROM phones WHERE name LIKE '%P4 Power%'").fetchall()
for r in p4_rows:
    raw = json.loads(r[4]) if r[4] and isinstance(r[4], str) else (r[4] or {})
    ram = raw.get('Memory.RAM', '')
    storage = raw.get('Memory.Storage', '')
    raw_name = raw.get('Name', '')
    print(f"  ID {r[0]}: Name='{r[2]}', RawName='{raw_name}', Price={r[3]}, RAM='{ram}', Storage='{storage}'")
