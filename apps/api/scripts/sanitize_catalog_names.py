"""
sanitize_catalog_names.py — Database & CSV Phone Name Sanitizer
==============================================================
1. Scans and strips 'NEW', 'New', 'new' suffix artifacts from phone names.
   (e.g., 'iQOO 15NEW' -> 'iQOO 15', 'OPPO Reno16 5GNew' -> 'OPPO Reno16 5G')
2. Deletes scraped DOM junk records from SQLite DB.
3. Cleans CSV files in data/ and scraped_official_catalogues/ directories.
4. Rebuilds the FTS5 full-text search index.
"""

import sqlite3
import re
import glob
import os
import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/fone_master.db'))

def clean_name_string(name: str) -> str:
    if not name:
        return ""
    
    # Clean glued "NEW", "New", "new" at word boundaries or before parentheses/spaces
    # e.g. "iQOO 15NEW", "iQOO 15Rnew", "OPPO Reno16 5GNew (12GB RAM)"
    cleaned = re.sub(r'(?<=[a-zA-Z0-9])NEW(?=[\s\(\-_]|$)', '', name, flags=re.IGNORECASE)
    cleaned = re.sub(r'\bNEW\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def sanitize_database():
    if not os.path.exists(DB_PATH):
        print(f"[Sanitize] Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Delete DOM scrape junk records and tablets
    cursor.execute("DELETE FROM phones WHERE name LIKE 'FiltersFiltersSort%' OR name LIKE '%Apply sortclose%' OR name LIKE '%OPPO Pad%' OR name LIKE '%Enco Air%' OR name LIKE '%BubbleNew%'")
    deleted_count = cursor.rowcount
    print(f"[Sanitize DB] Deleted {deleted_count} DOM scrape junk and non-phone rows.")

    # 2. Clean phone names in SQLite
    rows = cursor.execute("SELECT rowid, name, brand, raw_specs FROM phones").fetchall()
    updated_count = 0

    for rowid, name, brand, raw_specs_str in rows:
        cleaned_name = clean_name_string(name)
        
        # Also clean inside raw_specs if present
        raw_specs = {}
        specs_changed = False
        if raw_specs_str:
            try:
                raw_specs = json.loads(raw_specs_str) if isinstance(raw_specs_str, str) else raw_specs_str
                if isinstance(raw_specs, dict):
                    for k in ['Name', 'Product_Name', 'Product Name']:
                        if k in raw_specs and isinstance(raw_specs[k], str):
                            c_val = clean_name_string(raw_specs[k])
                            if c_val != raw_specs[k]:
                                raw_specs[k] = c_val
                                specs_changed = True
            except Exception:
                pass

        if cleaned_name != name or specs_changed:
            new_raw_str = json.dumps(raw_specs) if specs_changed else raw_specs_str
            cursor.execute(
                "UPDATE phones SET name = ?, raw_specs = ? WHERE rowid = ?",
                (cleaned_name, new_raw_str, rowid)
            )
            updated_count += 1

    conn.commit()
    print(f"[Sanitize DB] Updated {updated_count} phone names in fone_master.db.")

    # 3. Rebuild FTS5 index
    try:
        cursor.execute("DELETE FROM phones_fts")
        cursor.execute("INSERT INTO phones_fts(rowid, name, brand) SELECT rowid, name, brand FROM phones")
        conn.commit()
        print("[Sanitize DB] Rebuilt phones_fts FTS5 search index.")
    except Exception as e:
        print(f"[Sanitize DB] FTS5 index update note: {e}")

    conn.close()

def sanitize_csv_files():
    search_paths = [
        os.path.join(ROOT_DIR, 'scraped_official_catalogues', '*.csv'),
        os.path.join(ROOT_DIR, 'data_engine', '*.csv'),
        os.path.join(ROOT_DIR, 'data', '*.csv'),
    ]

    total_csv_cleaned = 0
    for pattern in search_paths:
        for filepath in glob.glob(pattern):
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                
                # Replace 'NEW', 'New', 'new' after digits or model letters
                # e.g. "iQOO 15NEW" -> "iQOO 15"
                new_content = re.sub(r'(?<=[a-zA-Z0-9])NEW(?=[\s\(\-_,\"]|$)', '', content, flags=re.IGNORECASE)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as fp:
                        fp.write(new_content)
                    print(f"[Sanitize CSV] Cleaned '{os.path.basename(filepath)}'")
                    total_csv_cleaned += 1
            except Exception as e:
                print(f"[Sanitize CSV] Error on {filepath}: {e}")

    print(f"[Sanitize CSV] Total CSV files sanitized: {total_csv_cleaned}")

if __name__ == "__main__":
    print("=== Starting Catalog Sanitization ===")
    sanitize_database()
    sanitize_csv_files()
    print("=== Catalog Sanitization Completed ===")
