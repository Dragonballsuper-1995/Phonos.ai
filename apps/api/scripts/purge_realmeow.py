"""
purge_realmeow.py — Purge Mascot & Brand Character Scraps
=========================================================
Permanently deletes 'realmeow' (ID 16877) and any other non-phone merchandise/mascots
from SQLite DB (fone_master.db) and CSV catalogues.
"""

import sqlite3
import re
import glob
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/fone_master.db'))

MASCOT_PATTERNS = [
    r'\brealmeow\b',
    r'\bmascot\b',
    r'\btoy\b',
    r'\bhoodie\b',
    r'\bt-shirt\b',
    r'\bbackpack\b',
]

MASCOT_REGEX = re.compile('|'.join(MASCOT_PATTERNS), re.IGNORECASE)

def purge_db():
    if not os.path.exists(DB_PATH):
        print(f"[Purge] Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    rows = cursor.execute("SELECT rowid, brand, name, price FROM phones").fetchall()
    to_delete = []

    for rowid, brand, name, price in rows:
        name_str = (name or '').strip()
        brand_str = (brand or '').strip()

        if MASCOT_REGEX.search(name_str) or name_str.lower() in ('realmeow', 'ow'):
            to_delete.append((rowid, brand_str, name_str))

    print(f"[Purge DB] Found {len(to_delete)} mascot / non-phone scrap rows to delete.")
    for r in to_delete:
        print(f"  Deleting ID {r[0]}: [{r[1]}] '{r[2]}'")

    if to_delete:
        ids = [r[0] for r in to_delete]
        cursor.executemany("DELETE FROM phones WHERE rowid = ?", [(i,) for i in ids])
        conn.commit()
        print(f"[Purge DB] Deleted {len(ids)} rows from fone_master.db.")

    try:
        cursor.execute("DELETE FROM phones_fts")
        cursor.execute("INSERT INTO phones_fts(rowid, name, brand) SELECT rowid, name, brand FROM phones")
        conn.commit()
        print("[Purge DB] Successfully rebuilt phones_fts FTS5 search index.")
    except Exception as e:
        print(f"[Purge DB] FTS5 notice: {e}")

    conn.close()

def purge_csvs():
    search_paths = [
        os.path.join(ROOT_DIR, 'scraped_official_catalogues', '*.csv'),
        os.path.join(ROOT_DIR, 'data_engine', '*.csv'),
        os.path.join(os.path.dirname(DB_PATH), '*.csv'),
    ]

    total_cleaned = 0
    for pattern in search_paths:
        for filepath in glob.glob(pattern):
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as fp:
                    lines = fp.readlines()

                if not lines:
                    continue

                header = lines[0]
                cleaned = [header]
                deleted = 0

                for line in lines[1:]:
                    if MASCOT_REGEX.search(line):
                        deleted += 1
                    else:
                        cleaned.append(line)

                if deleted > 0:
                    with open(filepath, 'w', encoding='utf-8') as fp:
                        fp.writelines(cleaned)
                    print(f"[Purge CSV] '{os.path.basename(filepath)}': Purged {deleted} mascot rows.")
                    total_cleaned += deleted
            except Exception as e:
                print(f"[Purge CSV] Error in {filepath}: {e}")

    print(f"[Purge CSV] Total rows purged across CSV catalogues: {total_cleaned}")

if __name__ == "__main__":
    print("=== Purging Mascot Scraps ===")
    purge_db()
    purge_csvs()
    print("=== Purge Finished ===")
