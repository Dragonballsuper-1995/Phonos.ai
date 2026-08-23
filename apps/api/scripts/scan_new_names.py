import sqlite3
import re
import glob
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

db_path = 'data/phonos_ai.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Find in SQLite DB
db_matches = cursor.execute("SELECT rowid, name, brand FROM phones WHERE name LIKE '%NEW%'").fetchall()
print(f"Total phones in DB matching '%NEW%': {len(db_matches)}")
for r in db_matches[:15]:
    cleaned = re.sub(r'\bNEW\b|(?<=[a-zA-Z0-9])NEW(?=[\s\(\-_]|$)', '', r[1]).strip()
    print(f"  ID {r[0]}: \"{r[1]}\" -> \"{cleaned}\"")

print("\n--- Scanning CSV files in data/ ---")
csv_files = glob.glob('data/*.csv')
for f in csv_files:
    with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
        content = fp.read()
        matches = re.findall(r'(\w+[\s\-_]*1[0-9]+R?NEW\b|\w+NEW\b)', content)
        if matches:
            print(f"File {f}: Found {len(matches)} occurrences of pattern: {set(matches[:10])}")
