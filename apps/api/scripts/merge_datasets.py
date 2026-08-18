import pandas as pd
import sqlite3
import json
import os
import re
import ast

# Define paths
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
DB_PATH = os.path.join(DATA_DIR, 'fone_master.db')
CSV_OUT_PATH = os.path.join(DATA_DIR, 'master_dataset.csv')

def safe_eval(val):
    if pd.isna(val):
        return None
    return str(val)

def clean_phone_name(brand, name):
    if not name or pd.isna(name):
        return 'Unknown'
    brand = str(brand).strip()
    name = str(name).strip()
    
    # Normalize spaces
    name = ' '.join(name.split())
    
    # Remove duplicate brand names at the start
    # e.g., "Samsung Samsung Galaxy" -> "Samsung Galaxy"
    brand_lower = brand.lower()
    words = name.split()
    cleaned_words = []
    seen_brand = False
    
    for word in words:
        if word.lower() == brand_lower:
            if not seen_brand:
                cleaned_words.append(word)
                seen_brand = True
        else:
            cleaned_words.append(word)
            cleaned_words.extend(words[len(cleaned_words):])
            break
            
    # Ensure first character is uppercase
    res = ' '.join(cleaned_words)
    return res[0].upper() + res[1:] if res else 'Unknown'

def extract_price_from_prices_column(prices_str):
    if not prices_str or pd.isna(prices_str):
        return None
    try:
        prices_list = ast.literal_eval(prices_str)
        if isinstance(prices_list, list) and len(prices_list) > 0:
            first_item = prices_list[0]
            if isinstance(first_item, dict):
                first_val = list(first_item.values())[0]
                return first_val
    except Exception as e:
        pass
    return None

def clean_and_convert_price(price_str):
    if not price_str or pd.isna(price_str):
        return None, None
    
    price_str = str(price_str).strip()
    
    # Approved Exchange Rates (June 2026 update):
    USD_TO_INR = 93.5
    EUR_TO_INR = 105.0
    GBP_TO_INR = 122.0
    CAD_TO_INR = 65.0
    
    # Clean up common spacing and commas
    cleaned_str = price_str.replace(',', '').replace(r'\xa0', '').replace(r'\u2009', '')
    
    rate = 1.0
    
    if '€' in cleaned_str or 'eur' in cleaned_str.lower():
        rate = EUR_TO_INR
    elif 'c$' in cleaned_str.lower():
        rate = CAD_TO_INR
    elif '$' in cleaned_str or 'usd' in cleaned_str.lower():
        rate = USD_TO_INR
    elif '£' in cleaned_str or 'gbp' in cleaned_str.lower():
        rate = GBP_TO_INR
        
    nums = re.findall(r"[-+]?\d*\.\d+|\d+", cleaned_str)
    if nums:
        val = float(nums[0])
        price_numeric = float(round(val * rate))
        formatted_price = f"₹{int(price_numeric):,}"
        return price_numeric, formatted_price
        
    return None, None

def check_released_in_india(source, price_str, brand, raw_specs):
    # Rule 1: Smartprix is Indian market comparison
    if source == 'Smartprix':
        return True
    
    # Rule 2: If price is in INR (contains ₹, Rs., or INR)
    price_str_lower = str(price_str).lower()
    if '₹' in price_str_lower or 'rs' in price_str_lower or 'inr' in price_str_lower:
        return True
    
    # Rule 3: Brands that do not sell in India
    non_india_brands = {
        'sony', 'sharp', 'leitz', 'meizu', 'blu', 'kyocera', 'archos', 'wiko', 'kazam', 
        'gigabyte', 'plum', 'verykool', 'alcatel', 'acer', 'toshiba', 'panasonic', 'yota'
    }
    if brand.lower() in non_india_brands:
        return False
        
    # Rule 4: Check raw specs for India indicators
    raw_str = str(raw_specs).lower()
    if 'india' in raw_str:
        return True
        
    # Rule 5: If it is from global AllPhones.csv, has only EUR/USD prices, and no 'india' in specs -> False
    if source == 'AllPhones.csv':
        if ('eur' in price_str_lower or 'usd' in price_str_lower or '$' in price_str_lower or '€' in price_str_lower) and 'india' not in raw_str:
            return False
            
    # Default mainstream brands list
    mainstream_brands = {
        'samsung', 'apple', 'oneplus', 'xiaomi', 'redmi', 'poco', 'realme', 'vivo', 'oppo', 
        'motorola', 'iqoo', 'infinix', 'tecno', 'nothing', 'honor', 'asus', 'lenovo', 'nokia'
    }
    if brand.lower() in mainstream_brands:
        return True
        
    return False

def extract_launch_year(name, source, raw_specs):
    name_lower = str(name).lower()
    
    # Regex 4-digit year check in name first (e.g. "Galaxy S25 (2025)")
    year_match = re.search(r'\b(202\d|201\d|200\d)\b', name_lower)
    if year_match:
        return int(year_match.group(1))

    # Look inside raw_specs values
    if isinstance(raw_specs, dict):
        raw_dict = raw_specs
    else:
        try:
            raw_dict = json.loads(raw_specs) if raw_specs else {}
        except:
            raw_dict = {}

    years_found = []
    for k, v in raw_dict.items():
        v_str = str(v).lower()
        matches = re.findall(r'\b(199\d|200\d|201\d|202\d)\b', v_str)
        for m in matches:
            if not any(x in k.lower() for x in ['resolution', 'pixel', 'mah', 'charging', 'battery', 'usb', 'speed', 'camera', 'weight']):
                years_found.append(int(m))

    if years_found:
        valid_years = [y for y in years_found if y <= 2027]
        if valid_years:
            return max(valid_years)
            
    # Specific model mappers
    if 's26' in name_lower: return 2026
    if 's25' in name_lower: return 2025
    if 's24' in name_lower: return 2024
    if 's23' in name_lower: return 2023
    if 's22' in name_lower: return 2022
    if 'iphone 18' in name_lower: return 2026
    if 'iphone 17' in name_lower: return 2025
    if 'iphone 16' in name_lower: return 2024
    if 'iphone 15' in name_lower: return 2023
    
    return None

def is_phone_released(launch_year, raw_dict):
    if launch_year and launch_year > 2026:
        return False
        
    raw_str = str(raw_dict).lower()
    if '2027' in raw_str or '2028' in raw_str:
        return False
        
    if 'expected' in raw_str or 'upcoming' in raw_str or 'rumored' in raw_str:
        future_months = [
            'july 2026', 'august 2026', 'september 2026', 'october 2026', 'november 2026', 'december 2026',
            'july 17 2026', 'july 25 2026', 'aug 2026', 'sept 2026', 'oct 2026', 'nov 2026', 'dec 2026'
        ]
        if any(m in raw_str for m in future_months):
            return False
            
    return True

def main():
    print("Loading datasets...")
    mobiles_path = os.path.join(DATA_DIR, 'mobiles.csv')
    allphones_path = os.path.join(DATA_DIR, 'AllPhones.csv')
    smartprix_path = os.path.join(DATA_DIR, 'Analysed and Cleaned Mobiles Dataset from Smartprix.csv')
    
    mobiles_df = pd.read_csv(mobiles_path, low_memory=False)
    allphones_df = pd.read_csv(allphones_path, low_memory=False)
    smartprix_df = pd.read_csv(smartprix_path, low_memory=False)

    standardized_records = []

    print("Processing mobiles.csv...")
    for _, row in mobiles_df.iterrows():
        brand = safe_eval(row.get('Brand', ''))
        name = safe_eval(row.get('Name', ''))
        price = safe_eval(row.get('Price', ''))
        os_ver = safe_eval(row.get('Technical.OS', ''))
        
        raw_dict = {k: v for k, v in row.items() if pd.notna(v)}
        
        # Deduplication clean name
        brand_clean = brand.strip() if brand else 'Unknown'
        name_clean = clean_phone_name(brand_clean, name)
        
        price_num, formatted_price = clean_and_convert_price(price)
        released_india = check_released_in_india('mobiles.csv', price, brand_clean, raw_dict)
        launch_year = extract_launch_year(name_clean, 'mobiles.csv', raw_dict)

        # Filter out unreleased/future models
        if released_india:
            released_india = is_phone_released(launch_year, raw_dict)

        standardized_records.append({
            'brand': brand_clean,
            'name': name_clean,
            'price': formatted_price,
            'price_numeric': price_num,
            'os': os_ver,
            'source': 'mobiles.csv',
            'released_in_india': 1 if released_india else 0,
            'launch_year': launch_year,
            'raw_specs': json.dumps(raw_dict)
        })

    print("Processing AllPhones.csv...")
    for _, row in allphones_df.iterrows():
        name = safe_eval(row.get('Name', ''))
        if name:
            parts = name.split(' ', 1)
            brand = parts[0] if len(parts) > 0 else 'Unknown'
        else:
            brand = 'Unknown'
            
        price = safe_eval(row.get('Price', ''))
        if not price:
            prices_col = safe_eval(row.get('Prices', ''))
            price = extract_price_from_prices_column(prices_col)
            
        os_ver = safe_eval(row.get('Platform_OS', ''))
        
        raw_dict = {k: v for k, v in row.items() if pd.notna(v)}
        
        brand_clean = brand.strip()
        name_clean = clean_phone_name(brand_clean, name)
        
        price_num, formatted_price = clean_and_convert_price(price)
        released_india = check_released_in_india('AllPhones.csv', price, brand_clean, raw_dict)
        launch_year = extract_launch_year(name_clean, 'AllPhones.csv', raw_dict)

        # Filter out unreleased/future models
        if released_india:
            released_india = is_phone_released(launch_year, raw_dict)

        standardized_records.append({
            'brand': brand_clean,
            'name': name_clean,
            'price': formatted_price,
            'price_numeric': price_num,
            'os': os_ver,
            'source': 'AllPhones.csv',
            'released_in_india': 1 if released_india else 0,
            'launch_year': launch_year,
            'raw_specs': json.dumps(raw_dict)
        })

    print("Processing Smartprix...")
    for _, row in smartprix_df.iterrows():
        brand = safe_eval(row.get('Brand', ''))
        name = safe_eval(row.get('Product_Name', ''))
        price = safe_eval(row.get('Current_Price', ''))
        os_ver = safe_eval(row.get('Operating_System', ''))
        
        raw_dict = {k: v for k, v in row.items() if pd.notna(v)}
        
        brand_clean = brand.strip() if brand else 'Unknown'
        name_clean = clean_phone_name(brand_clean, name)
        
        price_num, formatted_price = clean_and_convert_price(price)
        released_india = check_released_in_india('Smartprix', price, brand_clean, raw_dict)
        launch_year = extract_launch_year(name_clean, 'Smartprix', raw_dict)

        # Filter out unreleased/future models
        if released_india:
            released_india = is_phone_released(launch_year, raw_dict)

        standardized_records.append({
            'brand': brand_clean,
            'name': name_clean,
            'price': formatted_price,
            'price_numeric': price_num,
            'os': os_ver,
            'source': 'Smartprix',
            'released_in_india': 1 if released_india else 0,
            'launch_year': launch_year,
            'raw_specs': json.dumps(raw_dict)
        })

    # Create Master DataFrame
    print("Merging and deduplicating...")
    master_df = pd.DataFrame(standardized_records)

    # Clean up Brand/Name mapping
    master_df['brand'] = master_df['brand'].str.title()
    master_df['name'] = master_df['name'].str.strip()

    # Deduplicate based on cleaned name
    # Priority: Smartprix (cleanest/recent) > mobiles.csv > AllPhones.csv
    source_priority = {'Smartprix': 1, 'mobiles.csv': 2, 'AllPhones.csv': 3}
    master_df['priority'] = master_df['source'].map(source_priority)
    master_df = master_df.sort_values('priority').drop_duplicates(subset=['name'], keep='first').drop('priority', axis=1)

    # Sort by Launch Year (descending), putting None at the end
    # We create a temporary sorting key where None becomes -1
    master_df['sort_year'] = master_df['launch_year'].fillna(-1)
    master_df = master_df.sort_values(by='sort_year', ascending=False).drop('sort_year', axis=1)

    print(f"Final dataset size: {len(master_df)} phones.")

    # Save to CSV
    print(f"Saving to CSV at {CSV_OUT_PATH}...")
    master_df.to_csv(CSV_OUT_PATH, index=False)

    # Save to SQLite Database
    print(f"Saving to SQLite Database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    
    # Overwrite the 'phones' table with our upgraded dataset
    master_df.to_sql('phones', conn, if_exists='replace', index=False)
    
    # Create indexes and FTS5 Virtual Table
    cursor = conn.cursor()
    
    print("Creating indexes on name, brand, and composite recommender index...")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_phones_name ON phones(name);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_phones_brand ON phones(brand);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_phones_recommender ON phones(released_in_india, price_numeric, launch_year);')
    
    print("Creating FTS5 Virtual Search Table...")
    cursor.execute('DROP TABLE IF EXISTS phones_fts;')
    cursor.execute('CREATE VIRTUAL TABLE phones_fts USING fts5(name, brand, content=phones, content_rowid=rowid);')
    cursor.execute('INSERT INTO phones_fts(rowid, name, brand) SELECT rowid, name, brand FROM phones;')
    
    # SQLite search triggers
    cursor.execute('DROP TRIGGER IF EXISTS phones_ai;')
    cursor.execute('''
    CREATE TRIGGER phones_ai AFTER INSERT ON phones BEGIN
        INSERT INTO phones_fts(rowid, name, brand) VALUES (new.rowid, new.name, new.brand);
    END;
    ''')
    
    cursor.execute('DROP TRIGGER IF EXISTS phones_ad;')
    cursor.execute('''
    CREATE TRIGGER phones_ad AFTER DELETE ON phones BEGIN
        INSERT INTO phones_fts(phones_fts, rowid, name, brand) VALUES('delete', old.rowid, old.name, old.brand);
    END;
    ''')
    
    cursor.execute('DROP TRIGGER IF EXISTS phones_au;')
    cursor.execute('''
    CREATE TRIGGER phones_au AFTER UPDATE ON phones BEGIN
        INSERT INTO phones_fts(phones_fts, rowid, name, brand) VALUES('delete', old.rowid, old.name, old.brand);
        INSERT INTO phones_fts(rowid, name, brand) VALUES(new.rowid, new.name, new.brand);
    END;
    ''')
    
    conn.commit()
    conn.close()

    print("Done! Upgraded master dataset created and FTS5 search indexing completed successfully.")

if __name__ == "__main__":
    main()
