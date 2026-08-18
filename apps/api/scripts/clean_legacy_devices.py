import sqlite3
import json

conn = sqlite3.connect('data/fone_master.db')
c = conn.cursor()

# 1. Update phones that are obviously keypad/feature phones or vintage models
feature_keywords = [
    'Metro', 'Duos', 'Corby', 'Guru', 'S3310', 'C6112', 'B3313', 'W259',
    'KKT', 'A1 Tejas', 'A3 Power', 'Champ', 'Star 3', 'Keystone', 'Rocker',
    'Flip Phone 2G', 'Keypad', 'Feature Phone', 'Tuf', 'Hero 600', 'Captain',
    'Poco C3', 'Micromax Canvas'
]

conditions = []
params = []

for kw in feature_keywords:
    conditions.append("name LIKE ?")
    params.append(f"%{kw}%")

query = f"""
UPDATE phones
SET released_in_india = 0
WHERE price_numeric < 4500
   OR ({' OR '.join(conditions)})
   OR os LIKE '%Feature%'
   OR os LIKE '%Proprietary%'
   OR os LIKE '%Symbian%'
   OR os LIKE '%Java%'
   OR os LIKE '%KaiOS%'
"""

c.execute(query, params)
updated_count = c.rowcount
conn.commit()

print(f"Successfully marked {updated_count} legacy/feature devices as released_in_india = 0")

# 2. Count remaining active modern smartphones
c.execute("SELECT count(*) FROM phones WHERE released_in_india = 1")
active_count = c.fetchone()[0]
print(f"Remaining active genuine modern smartphones in database: {active_count}")

conn.close()
