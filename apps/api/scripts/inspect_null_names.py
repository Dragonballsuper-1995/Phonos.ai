import sqlite3
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('apps/api/data/phonos_ai.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Let's inspect phones with launch_year is NULL (mostly from AllPhones.csv)
cursor.execute("SELECT rowid, brand, name, price, price_numeric, os, source, released_in_india, launch_year, raw_specs FROM phones WHERE launch_year IS NULL")
null_year_rows = cursor.fetchall()
print(f"Total phones with launch_year = NULL: {len(null_year_rows)}")

# Let's inspect the names of these null year phones
sample_names = [r['name'] for r in null_year_rows]
print("Sample 50 null year phone names:")
for i, name in enumerate(sample_names[:50]):
    print(f"  {i+1}. {name}")

conn.close()
