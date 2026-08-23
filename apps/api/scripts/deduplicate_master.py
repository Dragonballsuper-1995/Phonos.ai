import sqlite3

conn = sqlite3.connect('data/phonos_ai.db')
c = conn.cursor()

# 1. Clean names where brand is duplicated in model, e.g. "Vivo iQOO Neo 10R" -> "iQOO Neo 10R"
c.execute("""
UPDATE phones
SET name = 'iQOO Neo 10R', brand = 'iQOO'
WHERE name LIKE '%Vivo iQOO Neo%'
""")

c.execute("""
UPDATE phones
SET name = 'iQOO Z9s Pro', brand = 'iQOO'
WHERE name LIKE '%Vivo iQOO Z9s%'
""")

c.execute("""
UPDATE phones
SET name = 'iQOO 12', brand = 'iQOO'
WHERE name LIKE '%Vivo iQOO 12%'
""")

c.execute("""
UPDATE phones
SET name = 'iQOO 13', brand = 'iQOO'
WHERE name LIKE '%Vivo iQOO 13%'
""")

# 2. De-duplicate exact phone names keeping the latest/highest quality record
c.execute("""
SELECT name, COUNT(*) as cnt
FROM phones
WHERE released_in_india = 1
GROUP BY LOWER(TRIM(name))
HAVING cnt > 1
""")
dupes = c.fetchall()
print(f"Total duplicate name groups: {len(dupes)}")

for name, cnt in dupes:
    # Find all rows for this name
    c.execute("SELECT rowid, price_numeric, source FROM phones WHERE LOWER(TRIM(name)) = LOWER(TRIM(?)) AND released_in_india = 1 ORDER BY rowid DESC", (name,))
    rows = c.fetchall()
    # Keep the first row, mark the others released_in_india = 0
    keep_id = rows[0][0]
    for r in rows[1:]:
        c.execute("UPDATE phones SET released_in_india = 0 WHERE rowid = ?", (r[0],))

conn.commit()

c.execute("SELECT count(*) FROM phones WHERE released_in_india = 1")
print(f"Final active unique modern phones in database: {c.fetchone()[0]}")
conn.close()
