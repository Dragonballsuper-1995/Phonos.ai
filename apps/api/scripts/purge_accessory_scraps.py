"""
purge_accessory_scraps.py — Deep Accessory & Website UI Scrape Purger
====================================================================
Permanently deletes non-smartphone accessories and website navigation scraps
from SQLite DB (fone_master.db) and CSV catalogues in scraped_official_catalogues/ and data/.
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

# Comprehensive regex of non-smartphone accessories, store navigation, and UI junk
JUNK_NAME_PATTERNS = [
    r'\b(?:adapter|charger|cable|cooling clip|magnetic cooling|cooling card|smart pen|type-c hub|power adapter|supervooc cable)\b',
    r'\b(?:care\+|coins|coins reward|vip|vipenjoy|benefits|next ai|series|exchange|upgrade|warranty|accessories)\b',
    r'^(?:ow|new|phones|realme|oppo|vivo|xiaomi|samsung|apple|oneplus|iqoo|narzo|ui|test)$',
    r'\b(?:buds|earbuds|tws|headphone|earphone|watch|smartwatch|band|strap|case|cover|clip)\b',
    r'^(?:realme|oppo|vivo|honor|infinix|xiaomi|redmi)\s+(?:ui|coins|care\+|vip|phones|series|next ai|ow)$',
    r'^(?:narzo|gt|find x|find n|reno|f|k|a|n|x|note|hot|smart)\s+series$',
]

COMBINED_JUNK_REGEX = re.compile('|'.join(JUNK_NAME_PATTERNS), re.IGNORECASE)

def purge_database():
    if not os.path.exists(DB_PATH):
        print(f"[Purge DB] Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    rows = cursor.execute("SELECT rowid, brand, name, price FROM phones").fetchall()
    to_delete = []

    for rowid, brand, name, price in rows:
        name_str = (name or '').strip()
        brand_str = (brand or '').strip()

        # Check against junk regex
        if COMBINED_JUNK_REGEX.search(name_str):
            to_delete.append((rowid, brand_str, name_str))
        elif len(name_str) <= 2:
            to_delete.append((rowid, brand_str, name_str))
        elif name_str.lower() in ("ow", "new", "realme ui", "realme coins", "realme vip", "realme phones", "next ai"):
            to_delete.append((rowid, brand_str, name_str))

    print(f"[Purge DB] Found {len(to_delete)} non-smartphone / scrap rows to delete.")
    for r in to_delete[:20]:
        print(f"  Deleting ID {r[0]}: [{r[1]}] '{r[2]}'")

    if to_delete:
        ids_to_del = [r[0] for r in to_delete]
        cursor.executemany("DELETE FROM phones WHERE rowid = ?", [(i,) for i in ids_to_del])
        conn.commit()
        print(f"[Purge DB] Successfully deleted {len(ids_to_del)} scrap rows from fone_master.db.")

    # Rebuild FTS5 full text search index
    try:
        cursor.execute("DELETE FROM phones_fts")
        cursor.execute("INSERT INTO phones_fts(rowid, name, brand) SELECT rowid, name, brand FROM phones")
        conn.commit()
        print("[Purge DB] Successfully rebuilt phones_fts FTS5 search index.")
    except Exception as e:
        print(f"[Purge DB] FTS5 rebuild notice: {e}")

    conn.close()

def purge_csv_catalogues():
    search_paths = [
        os.path.join(ROOT_DIR, 'scraped_official_catalogues', '*.csv'),
        os.path.join(ROOT_DIR, 'data_engine', '*.csv'),
    ]

    total_csv_cleaned = 0
    for pattern in search_paths:
        for filepath in glob.glob(pattern):
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as fp:
                    lines = fp.readlines()

                if not lines:
                    continue

                header = lines[0]
                cleaned_lines = [header]
                deleted_in_file = 0

                for line in lines[1:]:
                    # Check first 3 columns (e.g. brand, model_name, full_name)
                    parts = line.split(',')
                    model_col = parts[2] if len(parts) > 2 else ""
                    full_col = parts[3] if len(parts) > 3 else ""
                    check_str = f"{model_col} {full_col}".strip()

                    if COMBINED_JUNK_REGEX.search(check_str) or len(model_col.strip()) <= 2 or model_col.strip().lower() in ("ow", "ui", "coins", "vip"):
                        deleted_in_file += 1
                    else:
                        cleaned_lines.append(line)

                if deleted_in_file > 0:
                    with open(filepath, 'w', encoding='utf-8') as fp:
                        fp.writelines(cleaned_lines)
                    print(f"[Purge CSV] '{os.path.basename(filepath)}': Purged {deleted_in_file} junk rows.")
                    total_csv_cleaned += deleted_in_file
            except Exception as e:
                print(f"[Purge CSV] Error on {filepath}: {e}")

    print(f"[Purge CSV] Total rows purged across CSV catalogues: {total_csv_cleaned}")

if __name__ == "__main__":
    print("=== Starting Accessory & Scrap Purge ===")
    purge_database()
    purge_csv_catalogues()
    print("=== Purge Completed Successfully ===")
