import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('apps/api/data/phonos_ai.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

queries = [
    '%Mix Fold%', '%X70 Air%', '%Edge 60s%', '%Razr 60%', '%S50%', '%V70%', '%Reno 14%', '%Reno 15%'
]

print("=== Investigating Phantom / Unreleased in India Models ===")
for q in queries:
    c.execute("SELECT rowid, name, brand, source, price_numeric, launch_year, raw_specs, released_in_india FROM phones WHERE name LIKE ?", (q,))
    rows = c.fetchall()
    print(f"\nQuery '{q}': {len(rows)} rows found")
    for r in rows:
        d = dict(r)
        specs = json.loads(d['raw_specs']) if d['raw_specs'] else {}
        print(f"  ID={d['rowid']} | {d['name']} ({d['brand']}) | ₹{d['price_numeric']} | Year={d['launch_year']} | India={d['released_in_india']} | Source={d['source']}")
        for k in ['Release_Date', 'General.Release Date', 'Status', 'Launch Status', 'Prices', 'Price', 'Country_Of_Origin']:
            if k in specs:
                print(f"      {k}: {specs[k]}")

conn.close()
