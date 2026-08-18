"""
Data Quality Fix Script for Phonos.ai Database
================================================
Fixes:
1. Marks 2027 phantom phones (not-yet-released) as released_in_india=0
2. Strips RAM/ROM specs from phone names (e.g. "(16GB RAM + 256GB)")
3. Fixes brand casing (Iqoo → iQOO, Oneplus → OnePlus, Cmf → CMF, etc.)
4. Removes phones that are NOT available in India based on known list
5. Marks truly wrong launch_year values for ancient phones tagged as 2026

Run: python scripts/fix_data_quality.py
"""

import sqlite3
import re
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/fone_master.db'))

# ─── Known phones NOT available in India (China-only or not launched yet) ────
# These must be excluded from recommendations
NOT_IN_INDIA = {
    # iQOO China-only
    "IQOO Z11 Turbo",           # China launch Jan 2026, import-only in India
    "IQOO Z11 Turbo Pro",       # Not launched in India, speculative
    "IQOO Z11 Turbo Plus",      # China only
    
    # Vivo wrong name
    "Vivo V70e",                # Does not exist in India; correct is Vivo V70 FE
    
    # 2027 phantom phones (don't exist yet)
    "Samsung Galaxy S27 Ultra 5G",
    "Samsung Galaxy S27 Ultra",
    "Samsung Galaxy S27 Pro",
    "Samsung Galaxy S27 5G",
    "Samsung Galaxy S27 Plus 5G",
    "Xiaomi 18 Ultra",
    "Xiaomi 18 5G",
    "OnePlus 17",
    "Oppo Find X10 Ultra",
    
    # Other known China-only phones
    "Xiaomi 18",                # China only as of June 2026
    "Oppo Find X10 Pro Max 5G", # China only
    "Vivo X300 Ultra",          # China only
    "Vivo X300 Pro",            # China only
}

# ─── Brand casing corrections ─────────────────────────────────────────────────
BRAND_CORRECTIONS = {
    "Iqoo": "iQOO",
    "Oneplus": "OnePlus",
    "Cmf": "CMF",
    "Realme": "realme",
    "Nothing": "Nothing",
    "Motorola": "Motorola",
    "Samsung": "Samsung",
    "Apple": "Apple",
    "Google": "Google",
}

# ─── RAM/ROM regex pattern ────────────────────────────────────────────────────
# Matches: (16GB RAM + 256GB), (8GB + 128GB), (3GB RAM), etc.
RAM_ROM_PATTERN = re.compile(
    r'\s*\(\d+GB\s+RAM\s*\+\s*\d+GB\)'    # (16GB RAM + 256GB)
    r'|\s*\(\d+GB\s*\+\s*\d+GB\)'          # (8GB + 128GB)
    r'|\s*\(\d+GB\s+RAM\)',                 # (8GB RAM)
    re.IGNORECASE
)

def fix_database():
    print(f"Connecting to: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # ── Step 1: Mark NOT_IN_INDIA phones as released_in_india = 0 ────────────
    print("\n[Step 1] Marking known NOT-IN-INDIA phones...")
    flagged = 0
    for phone_name in NOT_IN_INDIA:
        cursor.execute(
            "UPDATE phones SET released_in_india = 0 WHERE name = ? AND released_in_india = 1",
            (phone_name,)
        )
        if cursor.rowcount > 0:
            print(f"  [X] Excluded from India: {phone_name} ({cursor.rowcount} rows)")
            flagged += cursor.rowcount
    print(f"  Total excluded: {flagged} phones")

    # ── Step 2: Fix all 2027-tagged phones ───────────────────────────────────
    print("\n[Step 2] Fixing 2027 phantom phones...")
    cursor.execute(
        "UPDATE phones SET released_in_india = 0 WHERE launch_year = 2027"
    )
    print(f"  Fixed: {cursor.rowcount} phones with launch_year=2027 → released_in_india=0")

    # ── Step 3: Strip RAM/ROM from phone names ────────────────────────────────
    print("\n[Step 3] Stripping RAM/ROM specs from phone names...")
    cursor.execute("SELECT rowid, name FROM phones")
    all_rows = cursor.fetchall()
    stripped = 0
    for row in all_rows:
        orig_name = row['name']
        if orig_name and RAM_ROM_PATTERN.search(orig_name):
            clean_name = RAM_ROM_PATTERN.sub('', orig_name).strip()
            cursor.execute(
                "UPDATE phones SET name = ? WHERE rowid = ?",
                (clean_name, row['rowid'])
            )
            stripped += 1
    print(f"  Stripped RAM/ROM from: {stripped} phone names")

    # ── Step 4: Fix brand casing ──────────────────────────────────────────────
    print("\n[Step 4] Fixing brand casing...")
    for wrong, correct in BRAND_CORRECTIONS.items():
        cursor.execute(
            "UPDATE phones SET brand = ? WHERE brand = ?",
            (correct, wrong)
        )
        if cursor.rowcount > 0:
            print(f"  Fixed brand: '{wrong}' → '{correct}' ({cursor.rowcount} rows)")

    # ── Step 5: Fix ancient phones wrongly tagged as launch_year=2026 ─────────
    # Any phone that has name patterns of old phones should be excluded
    print("\n[Step 5] Removing ancient phones wrongly tagged as launch_year=2026...")
    cursor.execute(
        """
        SELECT rowid, name, brand, launch_year, raw_specs, price_numeric
        FROM phones 
        WHERE launch_year = 2026 AND released_in_india = 1
        ORDER BY price_numeric ASC 
        LIMIT 100
        """
    )
    ancient_candidates = cursor.fetchall()
    ancient_fixed = 0
    for row in ancient_candidates:
        raw = str(row['raw_specs'] or '').lower()
        name = (row['name'] or '').lower()
        price = float(row['price_numeric'] or 0)
        # Heuristics: detect old phones by name pattern or raw specs year markers
        is_ancient = (
            'nokia asha' in name or
            'galaxy sl' in name or
            ('nokia c20' in name and price < 8000) or
            ('lenovo a3' in name) or
            ('lenovo a6' in name) or
            ('2010' in raw) or ('2011' in raw) or ('2012' in raw) or
            ('2013' in raw) or ('2014' in raw) or ('2015' in raw)
        )
        if is_ancient:
            cursor.execute(
                "UPDATE phones SET released_in_india = 0 WHERE rowid = ?",
                (row['rowid'],)
            )
            ancient_fixed += 1
    print(f"  Removed: {ancient_fixed} ancient phones from India recommendations")

    # ── Commit ────────────────────────────────────────────────────────────────
    conn.commit()
    
    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n[Summary]")
    cursor.execute("SELECT COUNT(*) FROM phones")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phones WHERE released_in_india = 1")
    india = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phones WHERE released_in_india = 0")
    not_india = cursor.fetchone()[0]
    cursor.execute("SELECT launch_year, COUNT(*) as cnt FROM phones WHERE released_in_india = 1 GROUP BY launch_year ORDER BY launch_year DESC LIMIT 8")
    dist = cursor.fetchall()
    
    print(f"  Total phones: {total}")
    print(f"  India released: {india}")
    print(f"  Not India / excluded: {not_india}")
    print(f"\n  Launch year distribution (India phones):")
    for row in dist:
        print(f"    {int(row[0]) if row[0] else 'N/A'}: {row[1]} phones")
    
    conn.close()
    print("\n✅ Database fix complete!")

if __name__ == "__main__":
    fix_database()
