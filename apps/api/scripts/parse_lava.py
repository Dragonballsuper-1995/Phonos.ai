import re
import pandas as pd
import sqlite3
import os
import json

raw_text = """
Smart 4
3GB+3GB* RAM l 32GB ROM | Octa Core Processor | 16.66cm (6.56") qHD d...



VIRAT V1
4GB+4GB* RAM l 64GB ROM | Octa Core Processor | 17.13cm (6.75") HD+ d...



VIRAT V1 5G
4GB+4GB* RAM l 64GB ROM | Unisoc T8200 Octa Core Ultra Fast Processor...



Smart 4 Plus
4GB+4GB* RAM l 64GB ROM | Octa Core Processor | 17.13cm (6.75") HD+ d...



Bold N2 5G
Unisoc T8200 Octa Core Ultra Fast Processor | 17.13cm (6.75") HD+ 120H...



Shark 2 5G
4GB+4GB* RAM l 64GB ROM | Unisoc T8200 Octa Core Ultra Fast Processor...



Bold N2 Lite
3GB+4GB* RAM l 64GB ROM | Octa Core Processor | 17.13cm (6.75") HD+ d...



Yuva Smart 3
3GB+4GB* RAM l 64GB ROM | Octa Core Processor | 17.13cm (6.75") HD+ d...



Bold 2 5G
50MP AI Rear Camera with Sony Sensor | Large 16.94cm (6.67") FHD+ Amol...



Bold N2
4GB+4GB* RAM l 64GB ROM | Octa Core Processor | 17.13cm (6.75") HD+ d...



Star 3
4GB+4GB* RAM l 64GB ROM | Octa Core Processor | 17.13cm (6.75") HD+ d...



Blaze Duo 3
Large 16.94cm (6.67") FHD+ Amoled Punch-Hole Display with 120Hz Refres...

₹ 20,999

MRP (incl. of all taxes): ₹ 21,999 -5%



Play Max
2.5 GHz MediaTek Dimensity 7300 Processor (4nm) - 700,000K+ Antutu Sco...



AGNI 4
Premium flagship design with Aluminum Metal frame & Matte AG Glass Bac...



Bold N1 Lite
3GB+3GB* RAM l 64GB ROM | UNISOC 9863a Octa Core Processor | 17.13cm ...



Shark 2
50MP AI Rear Camera I 8MP Selfie Camera | 4GB+4GB* RAM l 64GB ROM | O...



AGNI 3
Segment-first Dual AMOLED display on front & back | Segment-first Medi...

₹ 20,999

MRP (incl. of all taxes): ₹ 25,499 -18%


Yuva Smart 2
3GB+4GB* RAM l 64GB ROM | UNISOC 9863a Octa Core Processor | 17.13cm ...



Bold N1 5G
4GB+4GB* RAM l 64GB | 128GB ROM | Unisoc T765 Octa Core Ultra Fast Pr...



Play Ultra
64 MP SONY IMX682 Sensor Camera with EIS + 5MP Macro Camera, 13MP Self...



Blaze Amoled 2
50MP AI Rear Camera with Sony Sensor | Large 16.94cm (6.67") FHD+ Amol...



Blaze Dragon
2.2 GHz Snapdragon 4Gen2 Processor | (4GB+4GB*)/(6GB+6GB*) LPDDR4X RAM...



Storm Play 5G
Large 17.13cm (6.75") HD+ Water-Drop Display with 120Hz Refresh Rate |...

₹ 11,499

MRP (incl. of all taxes): ₹ 13,499 -15%



Storm Lite 5G
Lightning Fast Performance with MediaTek Dimensity 6400 Chipset | 4GB+...

₹ 8,999

MRP (incl. of all taxes): ₹ 10,999 -18%



Bold N1 Pro
50MP AI Rear Camera | 8MP Selfie Camera | 4GB+4GB* RAM | 128GB ROM | ...

₹ 6,799

MRP (incl. of all taxes): ₹ 8,399 -19%



Bold N1
4GB+4GB* RAM l 64GB ROM | Octa-core Processor | 17.13cm (6.75") HD+ D...

₹ 5,999

MRP (incl. of all taxes): ₹ 7,499 -20%



Yuva Star 2
4GB+4GB* RAM l 64GB ROM | Octa-core Processor | 17.15cm (6.75") HD+ D...


Blaze Amoled
3D Curved AMOLED Display | 64MP Sony Sensor Camera & 16MP Selfie Camer...


BOLD 5G
Segment First 3D Curved AMOLED Display | IP64 Dust & Water Resistant |...


Shark
50MP AI Rear Camera | 8MP Selfie Camera | 4GB+4GB* RAM | 64GB ROM | O...



O3
3GB+3GB* | 4GB+4GB* RAM l 64GB ROM | Octa-core Processor | 17.15cm (6...


Yuva Smart
3GB+3GB* RAM l 64GB ROM | Octa-core Processor | 17.15cm (6.75") HD+ N...



Yuva 2 5G
700nits HBM 90Hz HD+ Punch Hole Display | Segment-first Notification L...



Blaze Duo 5G
4.02cm (1.58") Secondary AMOLED Display | 3D Curved AMOLED | 64MP Sony...

₹ 16,999

MRP (incl. of all taxes): ₹ 18,999 -11%



Yuva 4
50MP AI Triple Rear Camera I 8MP Selfie Camera | 4GB+4GB* RAM l 64GB/...



Blaze 3 5G
Segment First VIBE Light | Lightning Fast Performance with MediaTek Di...

₹ 11,499

MRP (incl. of all taxes): ₹ 12,999 -12%



Blaze X
Segment First 3D Curved AMOLED Display | 64MP Sony Sensor Camera & 16M...

₹ 14,999

MRP (incl. of all taxes): ₹ 16,999 -12%



Yuva 5G
Lightning-fast Performance UNISOC T750 5G Processor | 16.58cm (6.528")...

₹ 9,499

MRP (incl. of all taxes): ₹ 11,499 -17%



O2
8GB+ 8GB* RAM / 128GB UFS 2.2 ROM | Octa-core UNISOC T616 Processor (A...

₹ 7,999

MRP (incl. of all taxes): ₹ 9,999 -20%



Blaze Curve
16.94 cm (6.67") 120 Hz Punch Hole 3D Curved Amoled Display with Widev...

₹ 17,999

MRP (incl. of all taxes): ₹ 20,999 -14%



Yuva 3
4GB+ 4GB* RAM I 128GB UFS 2.2 ROM | UNISOC T606 Octa-core Processor (A...

₹ 6,999

MRP (incl. of all taxes): ₹ 7,999 -13%



Yuva 3 Pro
8GB+ 8GB* RAM / 128GB UFS 2.2 ROM | UNISOC T616 Octa-core Processor (A...

₹ 7,999

MRP (incl. of all taxes): ₹ 9,999 -20%



Blaze 2 5G
1st in the Segment Ring Light & Premium Glass Back Design | 16.55cm (6...

₹ 10,999

MRP (incl. of all taxes): ₹ 12,499 -12%



O1
16.66cm (6.56") 90Hz Display | (4GB+ 3GB*) RAM + 64GB ROM | 5000mAh ba...

₹ 6,999

MRP (incl. of all taxes): ₹ 8,999 -22%



Blaze Pro 5G
Ultra-fast Processor MediaTek D6020 | 8GB+8GB* RAM l 128GB ROM | 50MP ...

₹ 12,999

MRP (incl. of all taxes): ₹ 14,999 -13%



Blaze 2 Pro
Ultra-fast UNISOC T616 Processor | 8GB+8GB* RAM I 128GB ROM | 50MP AI ...

₹ 10,999

MRP (incl. of all taxes): ₹ 12,499 -12%



Yuva 2
(3GB+ 3GB*) RAM + 64GB ROM | Unisoc T606 Octa-core Processor | 13MP Du...

₹ 6,999

MRP (incl. of all taxes): ₹ 8,499 -18%



Yuva
MediaTek Helio G25 OctaCore Processor | 8MP Dual Camera + 5MP Selfie C...



AGNI 2
MediaTek Dimensity 7050 Processor | 120Hz FHD+ Curved AMOLED Display |...

₹ 19,999

MRP (incl. of all taxes): ₹ 25,999 -23%



Blaze 2
16.55cm (6.5") 90Hz Punch Hole Display | Ultra-fast Unisoc T616 Proces...

₹ 8,999

MRP (incl. of all taxes): ₹ 10,999 -18%



Blaze 5G 8GB
6GB RAM+ 3GB Virtual RAM + UFS 2.2 128GB ROM | MediaTek Dimensity 700 ...

₹ 12,999

MRP (incl. of all taxes): ₹ 16,499 -21%



AGNI 5G
Powered by MediaTek Dimensity 810 - 5G | Powerful 5000mAh battery | 64...

₹ 17,999

MRP (incl. of all taxes): ₹ 23,999 -25%



Blaze 5G
Supports All Indian 5G bands* | 2K Video Recording with EIS Support | ...

₹ 10,999

MRP (incl. of all taxes): ₹ 14,999 -27%



Blaze Pro
Premium Frosted Glass Back Design | 50MP Triple AI Rear Camera | 64GB ...

₹ 10,499

MRP (incl. of all taxes): ₹ 12,999 -19%



X2
Big 16.51cm (6.5”) IPS HD+ notch display | | Loud Audio speaker | FPS+...

₹ 6,999

MRP (incl. of all taxes): ₹ 7,999 -13%



Yuva 2 Pro
4GB RAM + 3GB Virtual RAM + 64GB ROM | MediaTek Helio G37 Octa-core Pr...

₹ 7,999

MRP (incl. of all taxes): ₹ 9,999 -20%



Storm 5G
17.22cm (6.78") 120Hz Punch Hole Display with Widevine L1 support | Ul...

₹ 13,499

MRP (incl. of all taxes): ₹ 14,999 -10%



Yuva Star
4GB+4GB* RAM l 64GB ROM | Octa-core Processor | 17.15cm (6.75") HD+ N...



Shark 5G
4GB+4GB* RAM l 64GB ROM | Unisoc T765 Octa Core Ultra Fast Processor ...
"""

lines = [l.strip() for l in raw_text.split('\n')]
lines = [l for l in lines if l]

spec_keywords = ['RAM', 'ROM', 'Processor', 'Display', 'MediaTek', 'Unisoc', 'Camera', 'Snapdragon', 'AMOLED', 'Chipset', 'OctaCore']

lava_phones = {}

for i, line in enumerate(lines):
    is_spec = any(k.lower() in line.lower() for k in spec_keywords)
    if is_spec and i > 0:
        prev_line = lines[i-1]
        if not any(k.lower() in prev_line.lower() for k in spec_keywords):
            # Probably a phone name
            name = prev_line
            # Look exactly 1 line ahead of the spec line for a price
            price = None
            if i + 1 < len(lines):
                if lines[i+1].startswith('₹'):
                    p_str = lines[i+1].replace('₹', '').replace(',', '').strip()
                    if p_str.isdigit():
                        price = int(p_str)
            
            if not name.lower().startswith('lava'):
                name = 'Lava ' + name
            
            lava_phones[name] = price

print("Parsed Lava Phones:")
print(json.dumps(lava_phones, indent=2))

def standardize_name(n):
    n = str(n).strip().lower()
    if n.startswith('lava '):
        n = n[5:]
    return n

allowed_lava = {standardize_name(k): v for k, v in lava_phones.items()}

def clean_database(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM phones", conn)
    
    def update_price(row):
        brand = str(row['brand']).lower()
        if brand == 'lava':
            name = standardize_name(row['name'])
            model = standardize_name(row['model']) if 'model' in row else ''
            
            for allowed_name in sorted(allowed_lava.keys(), key=len, reverse=True):
                price = allowed_lava[allowed_name]
                if (allowed_name in name or allowed_name in model):
                    # We will enforce the new price (which can be null)
                    # wait, only set it if not None?
                    # The user said "keep only these phones along with their prices".
                    # If it has no price in the list, maybe it should be None.
                    # Or keep existing? We'll overwrite with what's parsed.
                    if price is not None:
                        row['price_numeric'] = price
                        row['price'] = f"₹{price:,}"
                    else:
                        row['price_numeric'] = None
                        row['price'] = None
                    break
        return row
        
    df_cleaned = df.apply(update_price, axis=1)
    
    schema = pd.read_sql_query("SELECT sql FROM sqlite_master WHERE type='table' AND name='phones'", conn).iloc[0,0]
    cursor = conn.cursor()
    cursor.execute("DROP TABLE phones")
    cursor.execute(schema)
    conn.commit()
    
    df_cleaned.to_sql('phones', conn, if_exists='append', index=False)
    conn.close()
    print("DB prices updated.")
    
def clean_csv(csv_path):
    if not os.path.exists(csv_path): return
    df = pd.read_csv(csv_path)
    
    def update_price(row):
        if 'brand' not in row: return row
        brand = str(row['brand']).lower()
        if brand == 'lava':
            name_val = row['name'] if 'name' in row else row.get('full_name', '')
            if pd.isna(name_val): name_val = ''
            name = standardize_name(name_val)
            
            model_val = row.get('model_name', '')
            if pd.isna(model_val): model_val = ''
            model = standardize_name(model_val)
            
            for allowed_name in sorted(allowed_lava.keys(), key=len, reverse=True):
                price = allowed_lava[allowed_name]
                if (allowed_name in name or allowed_name in model):
                    if price is not None:
                        if 'price_numeric' in row: row['price_numeric'] = price
                        if 'price_inr' in row: row['price_inr'] = price
                        if 'price' in row: row['price'] = f"₹{price:,}"
                        if 'price_raw' in row: row['price_raw'] = f"₹{price:,}"
                    else:
                        if 'price_numeric' in row: row['price_numeric'] = None
                        if 'price_inr' in row: row['price_inr'] = None
                        if 'price' in row: row['price'] = None
                        if 'price_raw' in row: row['price_raw'] = None
                    break
        return row
        
    df_cleaned = df.apply(update_price, axis=1)
    df_cleaned.to_csv(csv_path, index=False)
    print(f"CSV {csv_path} updated.")

clean_database('apps/api/data/phonos_ai.db')
clean_csv('apps/api/data/phonos_ai.csv')
clean_csv('scraped_official_catalogues/Combined_Official_India_Smartphones_Catalogue.csv')
