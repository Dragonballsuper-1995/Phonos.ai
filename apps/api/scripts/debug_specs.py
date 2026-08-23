import sqlite3
import json

conn = sqlite3.connect('data/phonos_ai.db')
cursor = conn.cursor()

phones = cursor.execute("""
    SELECT rowid, name, brand, price_numeric, launch_year, dxomark_camera_score, geekbench_multi, antutu_v10_score, gsmarena_battery_hours, vcx_camera_score, raw_specs 
    FROM phones 
    WHERE name LIKE '%Galaxy S25%' OR name LIKE '%Galaxy S26%' OR name LIKE '%OnePlus 15%' OR name LIKE '%OnePlus 13%'
    LIMIT 10
""").fetchall()

for p in phones:
    print(f"ID: {p[0]} | Name: {p[1]} | Brand: {p[2]} | Price: {p[3]} | Year: {p[4]}")
    print(f"  Benchmarks -> DxO: {p[5]} | GB6: {p[6]} | AnTuTu: {p[7]} | Batt: {p[8]}h | VCX: {p[9]}")
    raw = json.loads(p[10]) if p[10] else {}
    print(f"  Raw Keys: {list(raw.keys())[:12]}")
    sample_details = {k: raw[k] for k in list(raw.keys())[:10] if isinstance(raw[k], (str, int, float))}
    print(f"  Sample: {sample_details}")
    print("-" * 70)
