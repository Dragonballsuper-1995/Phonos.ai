"""
build_hardware_vectors.py
=========================
Precomputes L2-normalized hardware vectors for all phones in phonos_ai.db.
Run this after any database re-seed:
  python scripts/build_hardware_vectors.py

The hardware_vector column stores 5 × float32 = 20 bytes per phone.
At 10,000 phones this adds ~200 KB to the database.
"""
import sqlite3
import json
import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models.phone import PhoneDetails
from app.services.hardware_scorer import normalize_hardware_vector

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/phonos_ai.db'))

def migrate(conn):
    try:
        conn.execute("ALTER TABLE phones ADD COLUMN hardware_vector BLOB")
        conn.commit()
        print("[Migration] Added hardware_vector BLOB column.")
    except Exception:
        print("[Migration] hardware_vector column already exists — skipping.")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    migrate(conn)

    rows = conn.execute(
        "SELECT rowid AS id, brand, name, price, price_numeric, raw_specs, "
        "released_in_india, launch_year, is_current_catalogue "
        "FROM phones WHERE released_in_india = 1"
    ).fetchall()

    print(f"[HardwareVectors] Building vectors for {len(rows)} phones...")
    ok, skip = 0, 0

    for row in rows:
        d = dict(row)
        if isinstance(d.get('raw_specs'), str):
            try:
                d['raw_specs'] = json.loads(d['raw_specs'])
            except Exception:
                d['raw_specs'] = {}
        try:
            phone = PhoneDetails(**d)
            vec = normalize_hardware_vector(phone)   # float32[5], L2-norm=1.0
            conn.execute(
                "UPDATE phones SET hardware_vector = ? WHERE rowid = ?",
                (vec.tobytes(), d['id'])
            )
            ok += 1
        except Exception as e:
            print(f"  [WARN] Skipped rowid={d.get('id')}: {e}")
            skip += 1

    conn.commit()
    conn.close()
    print(f"[HardwareVectors] Done. {ok} updated, {skip} skipped.")

if __name__ == "__main__":
    main()
