import sqlite3
import json
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect('data/phonos_ai.db')
cursor = conn.cursor()

def extract_variant(name, raw_specs_json):
    raw = {}
    if raw_specs_json:
        try:
            raw = json.loads(raw_specs_json) if isinstance(raw_specs_json, str) else raw_specs_json
        except:
            raw = {}
    
    # Try regex on raw Name (e.g. 'Realme P4 Power 5G (8GB RAM + 256GB)')
    raw_name = raw.get('Name', name)
    m = re.search(r'\((\d+GB(?:\s*RAM)?\s*(?:\+\s*\d+(?:GB|TB))?)\)', raw_name, re.I)
    if m:
        v = m.group(1).replace(' RAM', '').replace(' ', '')
        return v
    
    # Fallback to Memory.RAM + Memory.Storage
    ram = raw.get('Memory.RAM', '').strip()
    storage = raw.get('Memory.Storage', '').strip()
    if ram and storage:
        ram_clean = re.sub(r'\s+', '', ram)
        storage_clean = re.sub(r'\s+', '', storage)
        return f"{ram_clean} + {storage_clean}"
    elif storage:
        return storage
    elif ram:
        return ram
    return ""

rows = cursor.execute("SELECT rowid, brand, name, price, raw_specs FROM phones WHERE name LIKE '%P4 Power%' OR name LIKE '%S26%' OR name LIKE '%OnePlus 15%' LIMIT 20").fetchall()
for r in rows:
    v = extract_variant(r[2], r[4])
    print(f"ID {r[0]}: [{r[1]}] '{r[2]}' | Variant='{v}' | Price={r[3]}")
