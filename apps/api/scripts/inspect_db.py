import sqlite3
import json

conn = sqlite3.connect('data/fone_master.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# S27 check
cursor.execute('SELECT name, brand, launch_year, raw_specs FROM phones WHERE name LIKE ? LIMIT 3', ('%Samsung Galaxy S27%',))
rows = cursor.fetchall()
for r in rows:
    d = dict(r)
    specs_preview = str(d['raw_specs'])[:400] if d['raw_specs'] else 'NO SPECS'
    print("name:", d['name'], "| launch_year:", d['launch_year'])
    print("specs_preview:", specs_preview)
    print()

print("--- BRAND vs NAME check (brand repeating) ---")
cursor.execute('SELECT name, brand FROM phones WHERE released_in_india = 1 ORDER BY launch_year DESC, rowid DESC LIMIT 20')
for r in cursor.fetchall():
    d = dict(r)
    brand_lc = d['brand'].lower() if d['brand'] else ''
    name_lc = d['name'].lower() if d['name'] else ''
    repeats = name_lc.startswith(brand_lc)
    marker = " <<< REPEATS" if repeats else ""
    print("brand:", d['brand'], "| name:", d['name'], marker)

print()
print("--- Count: names that start with brand ---")
cursor.execute('SELECT brand, name FROM phones WHERE released_in_india = 1')
rows = cursor.fetchall()
repeat_count = 0
total = 0
for r in rows:
    d = dict(r)
    total += 1
    if d['name'] and d['brand'] and d['name'].lower().startswith(d['brand'].lower()):
        repeat_count += 1
print("Total India phones:", total)
print("Names starting with brand:", repeat_count)

# Check launch years distribution
print()
print("--- Launch year distribution for India phones ---")
cursor.execute('SELECT launch_year, COUNT(*) as cnt FROM phones WHERE released_in_india = 1 GROUP BY launch_year ORDER BY launch_year DESC LIMIT 10')
for r in cursor.fetchall():
    d = dict(r)
    print("year:", d['launch_year'], "| count:", d['cnt'])

# Check phones with launch_year 2027 (future)
print()
print("--- 2027 phones (shouldn't exist!) ---")
cursor.execute('SELECT name, brand, launch_year, source FROM phones WHERE launch_year = 2027 AND released_in_india = 1')
rows = cursor.fetchall()
for r in rows:
    print(dict(r))

conn.close()
