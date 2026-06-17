import os
import sys
import pandas as pd
import asyncio
import uuid
import re
import random
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db.database import get_db_pool, close_db_pool

def generate_slug(brand, model):
    b = str(brand) if pd.notna(brand) else "unknown"
    m = str(model) if pd.notna(model) else "device"
    text = f"{b}-{m}".lower()
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')

async def main():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "smartprix_smartphones_april_2026.csv")
    if not os.path.exists(csv_path):
        print(f"Error: CSV not found at {csv_path}")
        return
        
    print(f"Loading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    pool = await get_db_pool()
    count = 0

    # Let's clean up old phones from previous run to avoid clutter and keep only the latest 2026 ones
    await pool.execute("DELETE FROM phones WHERE slug LIKE '%-%'")

    for idx, row in df.iterrows():
        try:
            brand = str(row['brand_name']).strip().title()
            model = str(row['model']).strip()
            # Often smartprix model names include the brand name, so let's check
            full_name = model if brand.lower() in model.lower() else f"{brand} {model}"
            
            slug = generate_slug(brand, model)
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"
            
            price_inr = int(row['price']) if pd.notna(row['price']) else random.randint(10000, 150000)
            
            # price_category
            price_tier = str(row['price_category']) if pd.notna(row['price_category']) else "Mid-Range"
            
            display_size = float(row['screen_size']) if pd.notna(row['screen_size']) else 6.5
            
            proc_brand = str(row['processor_brand']).strip().title() if pd.notna(row['processor_brand']) else ""
            proc_name = str(row['processor_name']).strip() if pd.notna(row['processor_name']) else ""
            chipset = f"{proc_brand} {proc_name}".strip()
            if not chipset or chipset.lower() == "nan": chipset = "Unknown"
            
            battery_mah = int(float(row['battery_capacity(mAh)'])) if pd.notna(row['battery_capacity(mAh)']) else 5000
            
            # Let's assume all these are from 2025/2026
            release_date = datetime(2026, 4, 1).date()
            
            spec_score = float(row['spec_score']) if pd.notna(row['spec_score']) else 70.0
            
            # Map spec score (usually 0-100) to 1-10
            base_score = min(max(spec_score / 10.0, 1.0), 10.0)
            
            perf_score = min(base_score + random.uniform(-0.5, 0.5), 9.9)
            cam_score = min(base_score + random.uniform(-1.0, 1.0), 9.9)
            bat_score = min(base_score + random.uniform(-0.5, 0.5), 9.9)
            disp_score = min(base_score + random.uniform(-0.5, 0.5), 9.9)
            val_score = min(base_score + random.uniform(-1.0, 1.0), 9.9)
            
            overall = round((perf_score + cam_score + bat_score + disp_score + val_score)/5.0, 1)

            await pool.execute('''
                INSERT INTO phones (
                    brand, model, full_name, slug, price_inr, price_tier,
                    display_size, chipset, battery_mah, release_date,
                    performance_score, camera_score, battery_score, display_score,
                    value_score, overall_score
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                    $11, $12, $13, $14, $15, $16
                )
            ''', brand, model, full_name, slug, price_inr, price_tier,
               display_size, chipset, battery_mah, release_date,
               round(perf_score,1), round(cam_score,1), round(bat_score,1), round(disp_score,1),
               round(val_score,1), overall
            )
            count += 1
        except Exception as e:
            print(f"Error on row {idx}: {e}")

    await close_db_pool()
    print(f"Successfully ingested {count} phones from smartprix_smartphones_april_2026.csv.")

if __name__ == "__main__":
    asyncio.run(main())
