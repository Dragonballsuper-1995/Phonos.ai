import asyncio
import uuid
import random
from datetime import datetime
from app.db.database import get_db_pool, close_db_pool

base_models = [
    {"brand": "Apple", "model": "iPhone 15", "display": 6.1, "chip": "A16 Bionic", "battery": 3349, "price_base": 70000},
    {"brand": "Apple", "model": "iPhone 15 Pro", "display": 6.1, "chip": "A17 Pro", "battery": 3274, "price_base": 130000},
    {"brand": "Samsung", "model": "Galaxy S24", "display": 6.2, "chip": "Exynos 2400", "battery": 4000, "price_base": 75000},
    {"brand": "Samsung", "model": "Galaxy S24 Ultra", "display": 6.8, "chip": "Snapdragon 8 Gen 3", "battery": 5000, "price_base": 125000},
    {"brand": "Google", "model": "Pixel 8", "display": 6.2, "chip": "Tensor G3", "battery": 4575, "price_base": 70000},
    {"brand": "Google", "model": "Pixel 8 Pro", "display": 6.7, "chip": "Tensor G3", "battery": 5050, "price_base": 100000},
    {"brand": "OnePlus", "model": "12", "display": 6.82, "chip": "Snapdragon 8 Gen 3", "battery": 5400, "price_base": 65000},
    {"brand": "OnePlus", "model": "12R", "display": 6.78, "chip": "Snapdragon 8 Gen 2", "battery": 5500, "price_base": 40000},
    {"brand": "Xiaomi", "model": "14", "display": 6.36, "chip": "Snapdragon 8 Gen 3", "battery": 4610, "price_base": 70000},
    {"brand": "Xiaomi", "model": "Redmi Note 13 Pro+", "display": 6.67, "chip": "Dimensity 7200 Ultra", "battery": 5000, "price_base": 30000},
    {"brand": "Realme", "model": "12 Pro+", "display": 6.7, "chip": "Snapdragon 7s Gen 2", "battery": 5000, "price_base": 30000},
    {"brand": "Nothing", "model": "Phone (2)", "display": 6.7, "chip": "Snapdragon 8+ Gen 1", "battery": 4700, "price_base": 45000},
    {"brand": "Nothing", "model": "Phone (2a)", "display": 6.7, "chip": "Dimensity 7200 Pro", "battery": 5000, "price_base": 25000},
    {"brand": "iQOO", "model": "12", "display": 6.78, "chip": "Snapdragon 8 Gen 3", "battery": 5000, "price_base": 53000},
    {"brand": "Motorola", "model": "Edge 50 Pro", "display": 6.7, "chip": "Snapdragon 7 Gen 3", "battery": 4500, "price_base": 32000},
    {"brand": "Poco", "model": "X6 Pro", "display": 6.67, "chip": "Dimensity 8300 Ultra", "battery": 5000, "price_base": 27000},
    {"brand": "Vivo", "model": "V30 Pro", "display": 6.78, "chip": "Dimensity 8200", "battery": 5000, "price_base": 42000},
    {"brand": "Oppo", "model": "Reno 11 Pro", "display": 6.7, "chip": "Dimensity 8200", "battery": 4600, "price_base": 40000},
    {"brand": "Samsung", "model": "Galaxy A55", "display": 6.6, "chip": "Exynos 1480", "battery": 5000, "price_base": 40000},
    {"brand": "Realme", "model": "Narzo 70 Pro", "display": 6.67, "chip": "Dimensity 7050", "battery": 5000, "price_base": 20000},
]

storage_variants = [(128, 8, 1.0), (256, 8, 1.1), (256, 12, 1.15), (512, 12, 1.3), (1024, 16, 1.6)]

async def main():
    pool = await get_db_pool()
    count = 0
    
    for base in base_models:
        for storage, ram, price_mult in storage_variants:
            # Skip invalid combos (e.g. 128GB for S24 Ultra or 1TB for budget phones)
            if storage == 128 and base["price_base"] > 100000: continue
            if storage >= 512 and base["price_base"] < 30000: continue
            
            full_name = f"{base['brand']} {base['model']} ({ram}GB RAM, {storage}GB Storage)"
            slug = f"{base['brand']}-{base['model']}-{ram}gb-{storage}gb".lower().replace(" ", "-").replace("(", "").replace(")", "").replace("+", "plus")
            
            price_inr = int(base["price_base"] * price_mult)
            
            price_tier = "Budget"
            if price_inr > 70000: price_tier = "Premium"
            elif price_inr > 40000: price_tier = "Upper Mid-Range"
            elif price_inr > 20000: price_tier = "Mid-Range"
            
            perf = random.uniform(7.0, 9.9)
            cam = random.uniform(6.5, 9.9)
            bat = random.uniform(7.0, 9.8)
            disp = random.uniform(7.5, 9.9)
            val = random.uniform(6.0, 9.5)
            overall = round((perf + cam + bat + disp + val) / 5, 1)
            
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
                ''', base['brand'], base['model'], full_name, slug, price_inr, price_tier,
                   base['display'], base['chip'], base['battery'], datetime(2024, 1, 1).date(),
                   round(perf, 1), round(cam, 1), round(bat, 1), round(disp, 1),
                   round(val, 1), overall
                )
                count += 1
            except Exception as e:
                print(f"Error inserting {slug}: {e}")
                
    await close_db_pool()
    print(f"Successfully generated and inserted {count} phones!")

if __name__ == "__main__":
    asyncio.run(main())
