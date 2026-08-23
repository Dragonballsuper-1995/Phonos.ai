import sqlite3

conn = sqlite3.connect('data/phonos_ai.db')
c = conn.cursor()

# Find phones that are feature phones, vintage phones, or have prices < 4000
query = """
SELECT rowid, name, brand, price_numeric, launch_year, os, raw_specs
FROM phones
WHERE price_numeric < 4000
   OR name LIKE '%Metro%'
   OR name LIKE '%Duos%'
   OR name LIKE '%Corby%'
   OR name LIKE '%Guru%'
   OR name LIKE '%S3310%'
   OR name LIKE '%C6112%'
   OR name LIKE '%B3313%'
   OR name LIKE '%W259%'
   OR os LIKE '%Feature%'
   OR os LIKE '%Proprietary%'
   OR os LIKE '%Symbian%'
   OR os LIKE '%Java%'
"""

c.execute(query)
rows = c.fetchall()
print(f"Total vintage / feature phones found: {len(rows)}")
for r in rows[:20]:
    print(f"ID={r[0]} | {r[1]} ({r[2]}) | Rs. {r[3]} | Year: {r[4]} | OS: {r[5]}")

conn.close()
