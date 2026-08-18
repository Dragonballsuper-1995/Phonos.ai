import sqlite3

db_path = 'C:/Users/sujal/Documents/Projects/Phonos.ai/apps/api/data/fone_master.db'
brands_to_delete = {'Cellecor', 'Good One', 'Ikall', 'Itel', 'Nubia', 'Lenovo', 'Jio'}

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Convert set to lowercase for case-insensitive match
brands_to_delete_lower = {b.lower() for b in brands_to_delete}

c.execute('SELECT DISTINCT brand FROM phones')
existing_brands = [row[0] for row in c.fetchall() if row[0]]

deleted_count = 0
for brand in existing_brands:
    if brand.strip().lower() in brands_to_delete_lower:
        c.execute('DELETE FROM phones WHERE brand = ?', (brand,))
        deleted_count += 1

conn.commit()
c.execute("INSERT INTO phones_fts(phones_fts, rank) VALUES('rebuild', 0)")
conn.commit()

c.execute('SELECT DISTINCT brand FROM phones ORDER BY brand')
remaining_brands = [row[0] for row in c.fetchall() if row[0]]

c.execute('SELECT COUNT(*) FROM phones')
total_phones = c.fetchone()[0]

conn.close()

print(f"Deleted {deleted_count} brands.")
print(f"Total phones remaining: {total_phones}")
print("REMAINING_BRANDS:")
for b in remaining_brands:
    print(b)
