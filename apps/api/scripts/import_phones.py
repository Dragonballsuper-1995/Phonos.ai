import json
import argparse
import asyncio
from app.db.database import get_db_pool, close_db_pool

async def import_data(file_path: str, format_type: str):
    pool = await get_db_pool()
    with open(file_path, 'r') as f:
        data = json.load(f)
            
    print(f"Loaded {len(data)} records.")
    
    for item in data:
        try:
                from datetime import datetime
                release_date = datetime.strptime(item.get('release_date'), "%Y-%m-%d").date() if item.get('release_date') else None
                
                await pool.execute('''
                    INSERT INTO phones (
                        brand, model, full_name, slug, price_inr, price_tier, 
                        amazon_url, flipkart_url, display_size, display_type, 
                        refresh_rate, resolution, peak_brightness, chipset, 
                        ram_gb, storage_gb, os, main_camera_mp, camera_setup, 
                        front_camera_mp, ultrawide_mp, telephoto_mp, optical_zoom, 
                        video_max, battery_mah, charging_watts, wireless_charging_w, 
                        weight_grams, dimensions, ip_rating, build_material, 
                        has_5g, has_nfc, has_ir_blaster, has_headphone_jack, 
                        usb_type, release_date, image_url, gsmarena_url, source, 
                        performance_score, camera_score, battery_score, display_score, 
                        value_score, overall_score, description_text
                    )
                    VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14,
                        $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26,
                        $27, $28, $29, $30, $31, $32, $33, $34, $35, $36, $37, $38,
                        $39, $40, $41, $42, $43, $44, $45, $46, $47
                    )
                    ON CONFLICT (slug) DO NOTHING
                ''', 
                    item.get('brand'), item.get('model'), item.get('full_name'), item.get('slug'), 
                    item.get('price_inr'), item.get('price_tier'), item.get('amazon_url'), 
                    item.get('flipkart_url'), item.get('display_size'), item.get('display_type'), 
                    item.get('refresh_rate'), item.get('resolution'), item.get('peak_brightness'), 
                    item.get('chipset'), item.get('ram_gb'), item.get('storage_gb'), 
                    item.get('os'), item.get('main_camera_mp'), item.get('camera_setup'), 
                    item.get('front_camera_mp'), item.get('ultrawide_mp'), item.get('telephoto_mp'), 
                    item.get('optical_zoom'), item.get('video_max'), item.get('battery_mah'), 
                    item.get('charging_watts'), item.get('wireless_charging_w'), item.get('weight_grams'), 
                    item.get('dimensions'), item.get('ip_rating'), item.get('build_material'), 
                    bool(item.get('has_5g')), bool(item.get('has_nfc')), bool(item.get('has_ir_blaster')), 
                    bool(item.get('has_headphone_jack')), item.get('usb_type'), 
                    release_date, 
                    item.get('image_url'), item.get('gsmarena_url'), item.get('source'), 
                    item.get('performance_score'), item.get('camera_score'), item.get('battery_score'), 
                    item.get('display_score'), item.get('value_score'), item.get('overall_score'), 
                    item.get('description_text')
                )
        except Exception as e:
            print(f"Error inserting {item.get('full_name')}: {e}")
            
    await close_db_pool()
    print("Import completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--format", default='json')
    args = parser.parse_args()
    asyncio.run(import_data(args.file, args.format))
