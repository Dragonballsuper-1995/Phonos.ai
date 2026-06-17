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

def safe_float(val):
    try:
        if pd.isna(val): return None
        v = str(val).lower().replace(',', '')
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", v)
        if nums:
            return float(nums[0])
        return None
    except:
        return None

def extract_battery_mah(val):
    if pd.isna(val): return None
    match = re.search(r'(\d+)\s*mAh', str(val), re.IGNORECASE)
    if match: return int(match.group(1))
    return safe_float(val)

def extract_display_size(val):
    if pd.isna(val): return None
    match = re.search(r'(\d+\.?\d*)\s*inch', str(val), re.IGNORECASE)
    if match: return float(match.group(1))
    return safe_float(val)

def generate_slug(brand, model):
    b = str(brand) if pd.notna(brand) else "unknown"
    m = str(model) if pd.notna(model) else "device"
    text = f"{b}-{m}".lower()
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')

async def main():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw_gsmarena.csv")
    if not os.path.exists(csv_path):
        print(f"Error: CSV not found at {csv_path}")
        return
        
    print(f"Loading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Filter for real brands we care about or just take top 300
    df = df.head(300)
    
    pool = await get_db_pool()
    count = 0

    for idx, row in df.iterrows():
        col_names = [str(c).lower() for c in df.columns]
        row_dict = {col_names[i]: row.iloc[i] for i in range(len(col_names))}

        brand = str(row_dict.get('oem', 'Unknown')).strip()
        model = str(row_dict.get('model', f'Model {idx}')).strip()
        full_name = f"{brand} {model}"
        slug = generate_slug(brand, model)
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

        # Attempt to get price
        price_val = row_dict.get('misc_price', '')
        price_float = safe_float(price_val)
        if price_float and 'eur' in str(price_val).lower():
            # Approx EUR->INR mapping: *90 + 18% GST = ~106x
            price_inr = int(price_float * 106)
        elif price_float and '$' in str(price_val):
            price_inr = int(price_float * 83 * 1.18)
        else:
            price_inr = random.randint(10000, 150000)

        price_tier = "Budget"
        if price_inr > 80000: price_tier = "Premium"
        elif price_inr > 40000: price_tier = "Mid-Range"

        display_size = extract_display_size(row_dict.get('display_size', row_dict.get('display_type', 6.1)))
        chipset = str(row_dict.get('platform_chipset', 'Unknown'))
        if pd.isna(row_dict.get('platform_chipset')):
            chipset = 'Unknown'
            
        battery_mah = extract_battery_mah(row_dict.get('battery', ''))
        if battery_mah is None: battery_mah = random.choice([4000, 4500, 5000])

        release_date = None
        launch_val = str(row_dict.get('launch_announced', ''))
        match = re.search(r'(20\d{2})', launch_val)
        if match:
            try:
                release_date = datetime(int(match.group(1)), 1, 1).date()
            except ValueError:
                pass

        perf_score = random.uniform(6.0, 9.9)
        cam_score = random.uniform(5.0, 9.9)
        bat_score = random.uniform(6.0, 9.9)
        disp_score = random.uniform(6.0, 9.9)
        val_score = random.uniform(6.0, 9.9)
        overall = round((perf_score + cam_score + bat_score + disp_score + val_score)/5.0, 1)

        try:
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
                ON CONFLICT (slug) DO NOTHING
            ''', brand, model, full_name, slug, price_inr, price_tier,
               display_size, chipset, battery_mah, release_date,
               round(perf_score,1), round(cam_score,1), round(bat_score,1), round(disp_score,1),
               round(val_score,1), overall
            )
            count += 1
        except Exception as e:
            pass

    await close_db_pool()
    print(f"Successfully ingested {count} phones from raw_gsmarena.csv.")

if __name__ == "__main__":
    asyncio.run(main())
