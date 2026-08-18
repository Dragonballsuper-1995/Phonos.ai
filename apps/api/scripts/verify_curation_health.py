import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('apps/api/data/fone_master.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=========================================================")
print("             PHONOS.AI DATABASE AUDIT REPORT             ")
print("=========================================================")

c.execute("SELECT COUNT(*) FROM phones")
total_phones = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM phones WHERE released_in_india = 1")
active_india = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM phones WHERE released_in_india = 0")
inactive_phones = c.fetchone()[0]

print(f"Total Phones in DB:        {total_phones}")
print(f"Active India Smartphones:  {active_india}")
print(f"Inactive / Excluded:       {inactive_phones}")

print("\n--- Active India Phones by Launch Year ---")
c.execute("SELECT launch_year, COUNT(*) as cnt FROM phones WHERE released_in_india = 1 GROUP BY launch_year ORDER BY launch_year DESC")
for r in c.fetchall():
    print(f"  • {int(r['launch_year'])}: {r['cnt']} devices")

print("\n--- Active India Phones by Brand ---")
c.execute("SELECT brand, COUNT(*) as cnt FROM phones WHERE released_in_india = 1 GROUP BY brand ORDER BY cnt DESC")
for r in c.fetchall():
    print(f"  • {r['brand']}: {r['cnt']} devices")

print("\n--- Price Range Summary (Active India Phones) ---")
c.execute("SELECT MIN(price_numeric), AVG(price_numeric), MAX(price_numeric) FROM phones WHERE released_in_india = 1")
min_p, avg_p, max_p = c.fetchone()
print(f"  • Min Price: ₹{int(min_p):,}")
print(f"  • Avg Price: ₹{int(avg_p):,}")
print(f"  • Max Price: ₹{int(max_p):,}")

# Test FTS5 search
print("\n--- FTS5 Search Verification ---")
test_queries = ["Galaxy S24", "iPhone 16", "OnePlus 12", "Redmi Note 13", "Realme GT"]
for q in test_queries:
    clean_q = " ".join(f"{w}*" for w in q.split())
    c.execute("""
        SELECT p.name, p.brand, p.price_numeric, p.launch_year 
        FROM phones p 
        JOIN phones_fts f ON p.rowid = f.rowid 
        WHERE phones_fts MATCH ? AND p.released_in_india = 1
        LIMIT 3
    """, (clean_q,))
    rows = c.fetchall()
    print(f"\nQuery '{q}': {len(rows)} matches found")
    for row in rows:
        print(f"  - {row['name']} ({row['brand']}) | ₹{int(row['price_numeric']):,} | Year: {int(row['launch_year'])}")

conn.close()
