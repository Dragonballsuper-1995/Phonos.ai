import sqlite3
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect('data/fone_master.db')
cursor = conn.cursor()

# Find any remaining mascot, brand scrap, or suspicious entries
suspicious = [
    'realmeow', 'mascot', 'toy', 'figure', 'gift', 'box', 'coupon', 'voucher',
    'hoodie', 't-shirt', 'bag', 'backpack', 'bottle', 'umbrella', 'sticker',
    'service', 'care', 'protect', 'warranty', 'screen protect', 'card'
]

for s in suspicious:
    rows = cursor.execute("SELECT rowid, brand, name, price FROM phones WHERE name LIKE ?", (f'%{s}%',)).fetchall()
    if rows:
        print(f"Pattern '{s}': found {len(rows)} rows:")
        for r in rows:
            print(f"  ID {r[0]}: [{r[1]}] '{r[2]}' (Price: {r[3]})")
