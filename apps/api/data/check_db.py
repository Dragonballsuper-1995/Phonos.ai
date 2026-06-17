import sqlite3
import json

conn = sqlite3.connect('C:/Users/sujal/Documents/Projects/fone.ai/apps/api/data/fone_master.db')
cursor = conn.cursor()
cursor.execute("SELECT brand, name, raw_specs FROM phones")

count_2026 = 0
count_2025 = 0

for brand, name, raw_specs in cursor.fetchall():
    if raw_specs:
        raw_str = str(raw_specs).lower()
        if '2026' in raw_str:
            count_2026 += 1
        elif '2025' in raw_str:
            count_2025 += 1

print(f"2026 phones: {count_2026}")
print(f"2025 phones: {count_2025}")
