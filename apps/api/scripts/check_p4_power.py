import sqlite3
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect('data/phonos_ai.db')
cursor = conn.cursor()
rows = cursor.execute("SELECT rowid, brand, name, price, raw_specs, gsmarena_battery_hours FROM phones WHERE name LIKE '%P4 Power%' OR name LIKE '%P4%'").fetchall()
print(f"Found {len(rows)} matching phones:")
for r in rows:
    print(f"  ID {r[0]}: [{r[1]}] '{r[2]}' (Price: {r[3]}, BattAUS: {r[5]})")
    if r[4]:
        raw = json.loads(r[4]) if isinstance(r[4], str) else r[4]
        print(f"    Battery: {raw.get('Battery.Size')}, Charging: {raw.get('Battery.Fast Charging')}, Chipset: {raw.get('Technical.Chipset')}")
