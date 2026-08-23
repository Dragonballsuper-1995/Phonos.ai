import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'phonos_ai.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print(f"=== Database: {db_path} ===")

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in DB:", [t['name'] for t in tables])

for table in tables:
    t_name = table['name']
    cursor.execute(f"PRAGMA table_info({t_name})")
    cols = cursor.fetchall()
    print(f"\n--- Columns in {t_name} ---")
    for col in cols:
        print(f"  {col['cid']}: {col['name']} ({col['type']})")
    
    cursor.execute(f"SELECT COUNT(*) as total FROM {t_name}")
    print(f"Total rows in {t_name}: {cursor.fetchone()['total']}")

# Let's inspect phones table specifically
cursor.execute("SELECT COUNT(*) as total FROM phones")
total_phones = cursor.fetchone()['total']

cursor.execute("SELECT COUNT(*) as total FROM phones WHERE released_in_india = 1")
india_phones = cursor.fetchone()['total']

cursor.execute("SELECT COUNT(*) as total FROM phones WHERE released_in_india = 0")
non_india_phones = cursor.fetchone()['total']

cursor.execute("SELECT COUNT(*) as total FROM phones WHERE released_in_india IS NULL")
null_india_phones = cursor.fetchone()['total']

print(f"\nPhones summary:\n  Total: {total_phones}\n  India=1: {india_phones}\n  India=0: {non_india_phones}\n  India=NULL: {null_india_phones}")

# Launch Year Distribution
cursor.execute("SELECT launch_year, COUNT(*) as cnt FROM phones GROUP BY launch_year ORDER BY launch_year DESC")
print("\nLaunch Year Distribution (All phones):")
for r in cursor.fetchall():
    print(f"  Year {r['launch_year']}: {r['cnt']}")

# India = 1 Launch Year Distribution
cursor.execute("SELECT launch_year, COUNT(*) as cnt FROM phones WHERE released_in_india = 1 GROUP BY launch_year ORDER BY launch_year DESC")
print("\nLaunch Year Distribution (released_in_india = 1):")
for r in cursor.fetchall():
    print(f"  Year {r['launch_year']}: {r['cnt']}")

# Check upcoming or future phones (> 2026 or status like 'Rumored' / 'Upcoming' / 'Exp. announcement')
cursor.execute("SELECT name, brand, launch_year, price_numeric, released_in_india, status FROM phones WHERE launch_year > 2026 OR status LIKE '%rumor%' OR status LIKE '%upcoming%' OR status LIKE '%exp%' LIMIT 50")
upcoming = cursor.fetchall()
print(f"\nUpcoming / Future / Rumored sample count found: {len(upcoming)}")
for r in upcoming[:20]:
    print(f"  {r['name']} | Brand: {r['brand']} | Year: {r['launch_year']} | Price: {r['price_numeric']} | India: {r['released_in_india']} | Status: {r['status']}")

# Check pre-2023 phones with released_in_india = 1
cursor.execute("SELECT COUNT(*) as cnt FROM phones WHERE released_in_india = 1 AND (launch_year < 2023 OR launch_year IS NULL)")
pre_2023_active = cursor.fetchone()['cnt']
print(f"\nActive phones with launch_year < 2023 or NULL: {pre_2023_active}")

conn.close()
