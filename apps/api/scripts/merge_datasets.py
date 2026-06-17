import pandas as pd
import sqlite3
import json
import os

# Define paths
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
DB_PATH = os.path.join(DATA_DIR, 'fone_master.db')
CSV_OUT_PATH = os.path.join(DATA_DIR, 'master_dataset.csv')

def safe_eval(val):
    if pd.isna(val):
        return None
    return str(val)

def main():
    print("Loading datasets...")
    # Load datasets
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
        
        # Dump entire row to dict, dropping NaNs
        raw_dict = {k: v for k, v in row.items() if pd.notna(v)}
        
        standardized_records.append({
            'brand': brand.strip() if brand else 'Unknown',
            'name': name.strip() if name else 'Unknown',
            'price': price,
            'os': os_ver,
            'source': 'mobiles.csv',
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
        os_ver = safe_eval(row.get('Platform_OS', ''))
        
        raw_dict = {k: v for k, v in row.items() if pd.notna(v)}
        
        standardized_records.append({
            'brand': brand.strip(),
            'name': name.strip() if name else 'Unknown',
            'price': price,
            'os': os_ver,
            'source': 'AllPhones.csv',
            'raw_specs': json.dumps(raw_dict)
        })

    print("Processing Smartprix...")
    for _, row in smartprix_df.iterrows():
        brand = safe_eval(row.get('Brand', ''))
        name = safe_eval(row.get('Product_Name', ''))
        price = safe_eval(row.get('Current_Price', ''))
        os_ver = safe_eval(row.get('Operating_System', ''))
        
        raw_dict = {k: v for k, v in row.items() if pd.notna(v)}
        
        standardized_records.append({
            'brand': brand.strip() if brand else 'Unknown',
            'name': name.strip() if name else 'Unknown',
            'price': price,
            'os': os_ver,
            'source': 'Smartprix',
            'raw_specs': json.dumps(raw_dict)
        })

    # Create Master DataFrame
    print("Merging and deduplicating...")
    master_df = pd.DataFrame(standardized_records)

    # Clean up Brand/Name for better deduplication
    master_df['brand'] = master_df['brand'].str.title()
    master_df['name'] = master_df['name'].str.title()

    # Deduplicate based on name.
    # Priority: Smartprix (cleanest/recent) > mobiles.csv > AllPhones.csv
    source_priority = {'Smartprix': 1, 'mobiles.csv': 2, 'AllPhones.csv': 3}
    master_df['priority'] = master_df['source'].map(source_priority)
    master_df = master_df.sort_values('priority').drop_duplicates(subset=['name'], keep='first').drop('priority', axis=1)

    print(f"Final dataset size: {len(master_df)} phones.")

    # Save to CSV
    print(f"Saving to CSV at {CSV_OUT_PATH}...")
    master_df.to_csv(CSV_OUT_PATH, index=False)

    # Save to SQLite Database
    print(f"Saving to SQLite Database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    master_df.to_sql('phones', conn, if_exists='replace', index=False)
    
    # Create an index on the name and brand for faster queries later
    cursor = conn.cursor()
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_phones_name ON phones(name);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_phones_brand ON phones(brand);')
    conn.commit()
    conn.close()

    print("Done! Master dataset created and database initialized.")

if __name__ == "__main__":
    main()
