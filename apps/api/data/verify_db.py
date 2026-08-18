import sqlite3

db_path = 'C:/Users/sujal/Documents/Projects/Phonos.ai/apps/api/data/fone_master.db'

try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('SELECT COUNT(DISTINCT brand) FROM phones')
    total_brands = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM phones')
    total_phones = c.fetchone()[0]

    c.execute('SELECT DISTINCT brand FROM phones ORDER BY brand')
    brands = [row[0] for row in c.fetchall() if row[0]]

    print(f"Total Phones: {total_phones}")
    print(f"Total Unique Brands: {total_brands}")
    print("\nBrands List:")
    for b in brands:
        print(b)

except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
