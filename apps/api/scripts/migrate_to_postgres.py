"""
migrate_to_postgres.py — SQLite to PostgreSQL / Supabase pgvector Migration Engine
===================================================================================
Exports all phone catalog models, lab benchmarks (DxOMark, Geekbench, VCX, AnTuTu, Battery),
ABSA review sentiments, and 5D hardware embedding vectors to PostgreSQL / Supabase DDL dump.

Usage:
  python scripts/migrate_to_postgres.py [--output data/supabase_migration_dump.sql]
"""

import os
import sys
import json
import sqlite3
import argparse
from typing import Dict, Any, List

# Ensure app is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/fone_master.db'))
DEFAULT_SQL_DUMP = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/supabase_migration_dump.sql'))


POSTGRES_DDL = """-- ============================================================================
-- Phonos.ai PostgreSQL / Supabase Schema with pgvector
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DROP TABLE IF EXISTS phones CASCADE;

CREATE TABLE phones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(150),
    slug VARCHAR(255) UNIQUE,
    price VARCHAR(100),
    price_numeric NUMERIC(12,2),
    os VARCHAR(100),
    launch_year INTEGER,
    launch_status VARCHAR(50) DEFAULT 'available',
    is_current_catalogue BOOLEAN DEFAULT false,
    india_official_catalogue BOOLEAN DEFAULT false,
    released_in_india BOOLEAN DEFAULT true,
    ai_verified BOOLEAN DEFAULT false,
    official_catalogue_url TEXT,
    image_url TEXT,
    source VARCHAR(100),
    raw_specs JSONB DEFAULT '{}'::jsonb,
    
    -- Aspect-Based Sentiment Analysis (ABSA)
    absa_camera NUMERIC(3,2) DEFAULT 0.0,
    absa_battery NUMERIC(3,2) DEFAULT 0.0,
    absa_performance NUMERIC(3,2) DEFAULT 0.0,
    absa_display NUMERIC(3,2) DEFAULT 0.0,
    absa_build NUMERIC(3,2) DEFAULT 0.0,
    absa_updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Scientific Lab Benchmarks
    dxomark_camera_score NUMERIC(5,1),
    dxomark_selfie_score NUMERIC(5,1),
    dxomark_display_score NUMERIC(5,1),
    vcx_camera_score NUMERIC(5,1),
    geekbench_single INTEGER,
    geekbench_multi INTEGER,
    antutu_v10_score INTEGER,
    gsmarena_battery_hours NUMERIC(4,1),
    
    -- 5D Hardware Vector for Sub-Millisecond Cosine Similarity Search
    hardware_vector vector(5),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indices for performance
CREATE INDEX idx_phones_brand ON phones(brand);
CREATE INDEX idx_phones_price_numeric ON phones(price_numeric);
CREATE INDEX idx_phones_india ON phones(released_in_india, is_current_catalogue);
CREATE INDEX idx_phones_hardware_vec ON phones USING ivfflat (hardware_vector vector_cosine_ops) WITH (lists = 100);

-- ============================================================================
-- Data Migration Inserts
-- ============================================================================
"""


def escape_sql_str(val: Any) -> str:
    """Escapes strings for SQL queries."""
    if val is None:
        return "NULL"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    s = str(val).replace("'", "''")
    return f"'{s}'"


def escape_json_str(val: Any) -> str:
    """Escapes JSON string for PostgreSQL JSONB format."""
    if not val:
        return "'{}'::jsonb"
    if isinstance(val, dict):
        s = json.dumps(val).replace("'", "''")
        return f"'{s}'::jsonb"
    try:
        parsed = json.loads(str(val))
        s = json.dumps(parsed).replace("'", "''")
        return f"'{s}'::jsonb"
    except:
        return "'{}'::jsonb"


def format_vector(val: Any) -> str:
    """Formats hardware vector for pgvector format: '[0.8, 0.9, 0.7, 0.85, 0.9]'::vector."""
    if not val:
        return "NULL"
    if isinstance(val, list):
        return f"'{json.dumps(val)}'::vector"
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list):
                return f"'{json.dumps(parsed)}'::vector"
        except:
            pass
    return "NULL"


def generate_postgres_migration(
    db_path: str = DB_PATH,
    output_sql_path: str = DEFAULT_SQL_DUMP
) -> Dict[str, Any]:
    """
    Reads SQLite database and dumps full PostgreSQL / Supabase migration SQL script.
    """
    print("=" * 70)
    print("🐘 Starting Phonos.ai PostgreSQL / Supabase Migration Exporter")
    print(f"📦 Source SQLite: {db_path}")
    print(f"📄 Output SQL: {output_sql_path}")
    print("=" * 70)

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Source database not found at {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT rowid as id, name, brand, price, price_numeric, os, launch_year,
               launch_status, is_current_catalogue, india_official_catalogue,
               released_in_india, ai_verified, official_catalogue_url, source,
               raw_specs, absa_camera, absa_battery, absa_performance, absa_display,
               absa_build, dxomark_camera_score, dxomark_selfie_score, dxomark_display_score,
               vcx_camera_score, geekbench_single, geekbench_multi, antutu_v10_score,
               gsmarena_battery_hours, hardware_vector, image_url, slug
        FROM phones
    """)
    rows = cursor.fetchall()
    conn.close()

    print(f"📊 Read {len(rows)} phone records from SQLite catalog.")

    sql_statements = [POSTGRES_DDL]
    batch_size = 50

    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        values_list = []
        for r in batch:
            brand = r["brand"] or "Generic"
            name = r["name"] or brand
            slug = r["slug"] or f"{brand.lower()}-{name.lower().replace(' ', '-')}"
            
            val_str = f"""(
                {escape_sql_str(name)},
                {escape_sql_str(brand)},
                {escape_sql_str(name)},
                {escape_sql_str(slug)},
                {escape_sql_str(r['price'])},
                {escape_sql_str(r['price_numeric'])},
                {escape_sql_str(r['os'])},
                {escape_sql_str(r['launch_year'])},
                {escape_sql_str(r['launch_status'])},
                {escape_sql_str(bool(r['is_current_catalogue']))},
                {escape_sql_str(bool(r['india_official_catalogue']))},
                {escape_sql_str(bool(r['released_in_india']))},
                {escape_sql_str(bool(r['ai_verified']))},
                {escape_sql_str(r['official_catalogue_url'])},
                {escape_sql_str(r['image_url'])},
                {escape_sql_str(r['source'])},
                {escape_json_str(r['raw_specs'])},
                {escape_sql_str(r['absa_camera'])},
                {escape_sql_str(r['absa_battery'])},
                {escape_sql_str(r['absa_performance'])},
                {escape_sql_str(r['absa_display'])},
                {escape_sql_str(r['absa_build'])},
                {escape_sql_str(r['dxomark_camera_score'])},
                {escape_sql_str(r['dxomark_selfie_score'])},
                {escape_sql_str(r['dxomark_display_score'])},
                {escape_sql_str(r['vcx_camera_score'])},
                {escape_sql_str(r['geekbench_single'])},
                {escape_sql_str(r['geekbench_multi'])},
                {escape_sql_str(r['antutu_v10_score'])},
                {escape_sql_str(r['gsmarena_battery_hours'])},
                {format_vector(r['hardware_vector'])}
            )"""
            values_list.append(val_str)

        insert_sql = f"""INSERT INTO phones (
            name, brand, model, slug, price, price_numeric, os, launch_year,
            launch_status, is_current_catalogue, india_official_catalogue,
            released_in_india, ai_verified, official_catalogue_url, image_url,
            source, raw_specs, absa_camera, absa_battery, absa_performance,
            absa_display, absa_build, dxomark_camera_score, dxomark_selfie_score,
            dxomark_display_score, vcx_camera_score, geekbench_single,
            geekbench_multi, antutu_v10_score, gsmarena_battery_hours, hardware_vector
        ) VALUES {','.join(values_list)};\n"""
        sql_statements.append(insert_sql)

    os.makedirs(os.path.dirname(output_sql_path), exist_ok=True)
    with open(output_sql_path, "w", encoding="utf-8") as f:
        f.writelines(sql_statements)

    file_size_kb = os.path.getsize(output_sql_path) / 1024.0
    print(f"\n✅ PostgreSQL migration dump successfully generated at:")
    print(f"   {output_sql_path} ({file_size_kb:.1f} KB, {len(rows)} phones)")

    return {
        "status": "success",
        "exported_phones": len(rows),
        "output_file": output_sql_path,
        "file_size_kb": round(file_size_kb, 1),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phonos.ai PostgreSQL / Supabase Migration Exporter")
    parser.add_argument("--output", type=str, default=DEFAULT_SQL_DUMP, help="Path to output SQL file")
    args = parser.parse_args()

    generate_postgres_migration(output_sql_path=args.output)
