import os
import sys
import argparse
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Ensure project and apps/api are in sys.path
API_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if API_ROOT not in sys.path:
    sys.path.insert(0, API_ROOT)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.services.scrapers.official_catalogues import (
    SCRAPERS_REGISTRY,
    ScrapedPhoneModel,
    BrandMetadata,
)
from app.services.scrapers.official_catalogues.csv_exporter import export_catalogues_to_csv
from app.services.catalogue_matcher import CatalogueMatcher

DB_PATH = os.path.join(API_ROOT, "data", "fone_master.db")
DEFAULT_CSV_DIR = os.path.join(PROJECT_ROOT, "scraped_official_catalogues")

def ensure_db_schema(conn: sqlite3.Connection):
    """Ensures necessary columns and brand_catalogues table exist."""
    c = conn.cursor()
    
    # 1. Create brand_catalogues table
    c.execute("""
        CREATE TABLE IF NOT EXISTS brand_catalogues (
            brand TEXT PRIMARY KEY,
            parent_company TEXT,
            parent_ecosystem TEXT,
            market TEXT DEFAULT 'India',
            official_india_presence INTEGER DEFAULT 1,
            brand_status TEXT DEFAULT 'ACTIVE',
            smartphone_catalogue_url TEXT,
            catalogue_source TEXT DEFAULT 'official',
            last_verified TEXT,
            verification_status TEXT DEFAULT 'verified',
            total_active_models INTEGER DEFAULT 0
        )
    """)
    
    # 2. Add columns to phones table if missing
    c.execute("PRAGMA table_info(phones)")
    existing_cols = {row[1] for row in c.fetchall()}
    
    new_cols = [
        ("is_current_catalogue", "INTEGER DEFAULT 0"),
        ("india_official_catalogue", "INTEGER DEFAULT 0"),
        ("launch_status", "TEXT DEFAULT 'available'"),
        ("sale_start", "TEXT"),
        ("official_catalogue_url", "TEXT"),
        ("last_verified", "TEXT")
    ]
    for col_name, col_type in new_cols:
        if col_name not in existing_cols:
            try:
                c.execute(f"ALTER TABLE phones ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"[Schema] Note: {e}")
    conn.commit()

def sync_brand_to_db(
    conn: sqlite3.Connection,
    brand_name: str,
    metadata: BrandMetadata,
    matched_results: list,
    unmatched_new: list
) -> Dict[str, int]:
    """Updates existing records and inserts newly discovered models."""
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Update brand_catalogues entry
    c.execute("""
        INSERT INTO brand_catalogues (
            brand, parent_company, parent_ecosystem, market, official_india_presence,
            brand_status, smartphone_catalogue_url, catalogue_source, last_verified,
            verification_status, total_active_models
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(brand) DO UPDATE SET
            parent_company = excluded.parent_company,
            parent_ecosystem = excluded.parent_ecosystem,
            brand_status = excluded.brand_status,
            smartphone_catalogue_url = excluded.smartphone_catalogue_url,
            last_verified = excluded.last_verified,
            total_active_models = excluded.total_active_models
    """, (
        metadata.brand,
        metadata.parent_company,
        getattr(metadata, "parent_ecosystem", "Mainstream & Flagship"),
        metadata.market,
        1 if metadata.official_india_presence else 0,
        metadata.brand_status,
        metadata.smartphone_catalogue_url,
        metadata.catalogue_source,
        metadata.last_verified,
        metadata.verification_status,
        metadata.total_active_models
    ))

    updated_count = 0
    inserted_count = 0

    # Reset is_current_catalogue for this brand to ensure only current models are active
    c.execute("UPDATE phones SET is_current_catalogue = 0 WHERE brand COLLATE NOCASE = ?", (brand_name,))

    # 2. Update matched phones in DB

    for match in matched_results:
        scraped: ScrapedPhoneModel = match.scraped
        db_id = match.db_id
        
        # Prepare updates
        updates = [
            "is_current_catalogue = 1",
            "released_in_india = 1",
            "ai_verified = 1",
            "india_official_catalogue = 1",
            "launch_status = ?",
            "official_catalogue_url = ?",
            "last_verified = ?"
        ]
        params = [
            scraped.launch_status,
            scraped.product_url or scraped.catalogue_url,
            now_str
        ]
        
        if scraped.sale_start_date:
            updates.append("sale_start = ?")
            params.append(scraped.sale_start_date)
            
        if scraped.price_inr and scraped.price_inr > 0:
            updates.append("price_numeric = ?")
            params.append(scraped.price_inr)
            updates.append("price = ?")
            params.append(scraped.price_raw or f"₹{int(scraped.price_inr):,}")

        params.append(db_id)
        sql = f"UPDATE phones SET {', '.join(updates)} WHERE rowid = ?"
        c.execute(sql, params)
        updated_count += 1

    # 3. Insert newly discovered models into DB
    for new_model in unmatched_new:
        raw_specs = json.dumps({
            "brand": new_model.brand,
            "name": new_model.full_name,
            "series": new_model.series,
            "catalogue_url": new_model.catalogue_url,
            "product_url": new_model.product_url,
            "source": "official_catalogue",
            "specs_summary": new_model.specs_summary or "Official Indian launch",
        })
        price_str = new_model.price_raw or (f"₹{int(new_model.price_inr):,}" if new_model.price_inr else "TBA")
        launch_year = 2026
        
        c.execute("""
            INSERT INTO phones (
                brand, name, price, price_numeric, os, source,
                released_in_india, launch_year, raw_specs, ai_verified,
                is_current_catalogue, india_official_catalogue, launch_status, sale_start,
                official_catalogue_url, last_verified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_model.brand,
            new_model.model_name,
            price_str,
            new_model.price_inr,
            "Android" if new_model.brand != "Apple" else "iOS",
            "official_catalogue",
            1,
            launch_year,
            raw_specs,
            1,
            1,
            1,
            new_model.launch_status,
            new_model.sale_start_date,
            new_model.product_url or new_model.catalogue_url,
            now_str
        ))
        inserted_count += 1

    conn.commit()
    return {"updated": updated_count, "inserted": inserted_count}


def main():
    parser = argparse.ArgumentParser(description="Official India Smartphone Catalogue Scraper & DB Sync")
    parser.add_argument("--brand", type=str, help="Scrape a single brand (e.g. Samsung, Nothing, POCO)")
    parser.add_argument("--all", action="store_true", help="Scrape all 20 canonical Indian smartphone brands")
    parser.add_argument("--export-csv", action="store_true", default=True, help="Export partitioned and master CSV datasets")
    parser.add_argument("--output-dir", type=str, default=DEFAULT_CSV_DIR, help="Output directory for generated CSVs")
    parser.add_argument("--export-json", type=str, help="Path to export full JSON snapshot")
    parser.add_argument("--dry-run", action="store_true", help="Perform scraping and comparison without database writes")
    parser.add_argument("--update-db", action="store_true", help="Update fone_master.db with official verification data")
    args = parser.parse_args()

    if not args.brand and not args.all:
        print("Please specify --all to scrape all 20 brands, or --brand <BrandName>.")
        sys.exit(1)

    brands_to_scrape = list(SCRAPERS_REGISTRY.keys()) if args.all else [args.brand]
    valid_brands = [b for b in brands_to_scrape if b in SCRAPERS_REGISTRY]

    if not valid_brands:
        print(f"Error: Brand '{args.brand}' not found in canonical 20 brands registry.")
        print(f"Available brands: {', '.join(SCRAPERS_REGISTRY.keys())}")
        sys.exit(1)

    print("=" * 80)
    print("🚀 PHONOS.AI — OFFICIAL INDIA SMARTPHONE CATALOGUE SCRAPER & VERIFIER")
    print("=" * 80)
    print(f"• Brands to scrape: {len(valid_brands)} ({', '.join(valid_brands)})")
    print(f"• Database Path: {DB_PATH}")
    print(f"• CSV Export Directory: {args.output_dir}")
    print(f"• Mode: {'DRY RUN (No DB Writes)' if args.dry_run else ('UPDATE DATABASE' if args.update_db else 'CATALOGUE EXTRACT')}")
    print("=" * 80)

    all_scraped_phones: List[ScrapedPhoneModel] = []
    brand_summaries = []

    conn = sqlite3.connect(DB_PATH)
    if not args.dry_run and args.update_db:
        ensure_db_schema(conn)

    matcher = CatalogueMatcher(DB_PATH)

    for idx, brand_name in enumerate(valid_brands, 1):
        print(f"\n[{idx}/{len(valid_brands)}] 🌐 Scraping official catalogue: {brand_name}...")
        scraper_cls = SCRAPERS_REGISTRY[brand_name]
        scraper = scraper_cls()
        
        try:
            phones = scraper.scrape()
            all_scraped_phones.extend(phones)
            
            # Run comparison with database
            matched, unmatched_new, unmatched_db = matcher.match_brand_models(brand_name, phones)
            
            exact_matches = sum(1 for m in matched if m.match_type == "EXACT")
            fuzzy_matches = sum(1 for m in matched if m.match_type == "HIGH_FUZZY")
            
            print(f"    ✓ Found {len(phones)} active models on official portal")
            print(f"    ✓ Matched with DB: {len(matched)} ({exact_matches} exact, {fuzzy_matches} fuzzy)")
            print(f"    ✓ New official launches discovered: {len(unmatched_new)}")
            print(f"    ✓ Legacy / Non-catalogue DB phones: {len(unmatched_db)}")

            db_stats = {"updated": 0, "inserted": 0}
            if args.update_db and not args.dry_run:
                metadata = scraper.get_brand_metadata(len(phones))
                metadata.parent_ecosystem = scraper.parent_ecosystem
                db_stats = sync_brand_to_db(conn, brand_name, metadata, matched, unmatched_new)
                print(f"    💾 DB Updated: {db_stats['updated']} models verified, {db_stats['inserted']} new models added")

            brand_summaries.append({
                "brand": brand_name,
                "ecosystem": scraper.parent_ecosystem,
                "scraped_count": len(phones),
                "matched_count": len(matched),
                "new_count": len(unmatched_new),
                "status": scraper.brand_status,
                "db_updated": db_stats["updated"],
                "db_inserted": db_stats["inserted"]
            })

        except Exception as e:
            print(f"    ❌ Error scraping {brand_name}: {e}")

    conn.close()


    # Sync to API root copy if updating DB
    if args.update_db and not args.dry_run:
        import shutil
        alt_db_path = os.path.join(API_ROOT, "fone_master.db")
        try:
            shutil.copy2(DB_PATH, alt_db_path)
            print(f"💾 Synced master database copy to: {alt_db_path}")
        except Exception as e:
            print(f"[Warning] Failed to sync secondary DB path: {e}")

    # 4. Export CSV datasets
    if args.export_csv and all_scraped_phones:

        print(f"\n📂 Exporting structured CSV datasets to: {args.output_dir}")
        exported_files = export_catalogues_to_csv(all_scraped_phones, args.output_dir)
        for filename, path in exported_files.items():
            file_size = os.path.getsize(path) if os.path.exists(path) else 0
            print(f"  • {filename} ({file_size} bytes)")

    # 5. Export JSON snapshot if requested
    if args.export_json:
        os.makedirs(os.path.dirname(os.path.abspath(args.export_json)), exist_ok=True)
        with open(args.export_json, "w", encoding="utf-8") as f:
            json.dump([p.model_dump() for p in all_scraped_phones], f, indent=2, ensure_ascii=False)
        print(f"\n📄 Saved JSON snapshot to: {args.export_json}")

    # Summary Report Table
    print("\n" + "=" * 80)
    print("📊 OFFICIAL INDIA SMARTPHONE CATALOGUE AUDIT & SYNC REPORT")
    print("=" * 80)
    print(f"{'Brand':<15} | {'Ecosystem':<24} | {'Scraped':<8} | {'Matched':<8} | {'New':<6} | {'Status':<14}")
    print("-" * 80)
    for s in brand_summaries:
        print(f"{s['brand']:<15} | {s['ecosystem']:<24} | {s['scraped_count']:<8} | {s['matched_count']:<8} | {s['new_count']:<6} | {s['status']:<14}")
    print("=" * 80)
    print(f"Total Phones Scraped: {len(all_scraped_phones)}")
    print("Verification completed successfully!")

if __name__ == "__main__":
    main()
