import sqlite3
import re

db_path = 'C:/Users/sujal/Documents/Projects/Phonos.ai/apps/api/data/phonos_ai.db'
txt_path = 'C:/Users/sujal/Documents/Projects/Phonos.ai/brands_to_be_deleted_completely.txt'

brands_to_delete = set()
with open(txt_path, 'r', encoding='utf-8-sig') as f:
    for line in f:
        m = re.match(r'\d+\.\s+(.*)', line.strip())
        if m:
            brands_to_delete.add(m.group(1).strip().lower())
        else:
            print("Failed to match:", repr(line))

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('SELECT DISTINCT brand FROM phones')
existing_brands = [row[0] for row in c.fetchall() if row[0]]

deleted_count = 0
for brand in existing_brands:
    if brand.strip().lower() in brands_to_delete:
        c.execute('DELETE FROM phones WHERE brand = ?', (brand,))
        deleted_count += 1

conn.commit()
c.execute("INSERT INTO phones_fts(phones_fts, rank) VALUES('rebuild', 0)")
conn.commit()

c.execute('SELECT DISTINCT brand FROM phones ORDER BY brand')
remaining_brands = [row[0] for row in c.fetchall() if row[0]]
conn.close()

print(f"Deleted {deleted_count} more brands.")
print("REMAINING_BRANDS:")
for b in remaining_brands:
    print(b)
