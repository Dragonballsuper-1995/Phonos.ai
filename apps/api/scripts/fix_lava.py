import pandas as pd
import sqlite3

def clean():
    conn = sqlite3.connect('apps/api/data/phonos_ai.db')
    df = pd.read_sql_query('SELECT * FROM phones', conn)
    
    allowed = ['lava smart 4', 'lava virat v1', 'lava virat v1 5g', 'lava smart 4 plus', 'lava bold n2 5g', 'lava shark 2 5g', 'lava bold n2 lite', 'lava yuva smart 3', 'lava bold 2 5g', 'lava bold n2', 'lava star 3', 'lava blaze duo 3', 'lava play max', 'lava agni 4', 'lava bold n1 lite', 'lava shark 2', 'lava agni 3', 'lava yuva smart 2', 'lava bold n1 5g', 'lava play ultra', 'lava blaze dragon', 'lava storm play 5g', 'lava storm lite 5g', 'lava bold n1 pro', 'lava bold n1', 'lava yuva star 2', 'lava bold 5g', 'lava shark', 'lava o3', 'lava yuva smart', 'lava yuva 2 5g', 'lava blaze duo 5g', 'lava yuva 4', 'lava blaze 3 5g', 'lava blaze x', 'lava yuva 5g', 'lava o2', 'lava blaze curve', 'lava yuva 3', 'lava yuva 3 pro', 'lava o1', 'lava blaze pro 5g', 'lava blaze 2 pro', 'lava yuva 2', 'lava yuva', 'lava agni 2', 'lava blaze 2', 'lava blaze 5g 8gb', 'lava agni 5g', 'lava blaze pro', 'lava x2', 'lava yuva 2 pro', 'lava storm 5g', 'lava yuva star', 'lava shark 5g', 'lava blaze amoled 2', 'lava blaze amoled']
    
    def is_allowed(row):
        brand = str(row['brand']).lower()
        if brand != 'lava': return True
        name = str(row['name']).lower()
        model = str(row.get('model', '')).lower()
        
        for a in allowed:
            if a in name or a in model:
                return True
        return False
        
    mask = df.apply(is_allowed, axis=1)
    df_cleaned = df[mask]
    print(f'DB: Keeping {len(df_cleaned)} out of {len(df)} phones (deleted {len(df) - len(df_cleaned)} Lava phones)')
    
    schema = pd.read_sql_query("SELECT sql FROM sqlite_master WHERE type='table' AND name='phones'", conn).iloc[0,0]
    cursor = conn.cursor()
    cursor.execute('DROP TABLE phones')
    cursor.execute(schema)
    conn.commit()
    
    df_cleaned.to_sql('phones', conn, if_exists='append', index=False)
    conn.close()

def clean_csv(path):
    df = pd.read_csv(path)
    allowed = ['lava smart 4', 'lava virat v1', 'lava virat v1 5g', 'lava smart 4 plus', 'lava bold n2 5g', 'lava shark 2 5g', 'lava bold n2 lite', 'lava yuva smart 3', 'lava bold 2 5g', 'lava bold n2', 'lava star 3', 'lava blaze duo 3', 'lava play max', 'lava agni 4', 'lava bold n1 lite', 'lava shark 2', 'lava agni 3', 'lava yuva smart 2', 'lava bold n1 5g', 'lava play ultra', 'lava blaze dragon', 'lava storm play 5g', 'lava storm lite 5g', 'lava bold n1 pro', 'lava bold n1', 'lava yuva star 2', 'lava bold 5g', 'lava shark', 'lava o3', 'lava yuva smart', 'lava yuva 2 5g', 'lava blaze duo 5g', 'lava yuva 4', 'lava blaze 3 5g', 'lava blaze x', 'lava yuva 5g', 'lava o2', 'lava blaze curve', 'lava yuva 3', 'lava yuva 3 pro', 'lava o1', 'lava blaze pro 5g', 'lava blaze 2 pro', 'lava yuva 2', 'lava yuva', 'lava agni 2', 'lava blaze 2', 'lava blaze 5g 8gb', 'lava agni 5g', 'lava blaze pro', 'lava x2', 'lava yuva 2 pro', 'lava storm 5g', 'lava yuva star', 'lava shark 5g', 'lava blaze amoled 2', 'lava blaze amoled']
    def is_allowed(row):
        if 'brand' not in row or pd.isna(row['brand']): return True
        brand = str(row['brand']).lower()
        if brand != 'lava': return True
        name = str(row.get('name', row.get('full_name', ''))).lower()
        model = str(row.get('model', row.get('model_name', ''))).lower()
        
        for a in allowed:
            if a in name or a in model:
                return True
        return False
    mask = df.apply(is_allowed, axis=1)
    df_cleaned = df[mask]
    print(f'{path}: Keeping {len(df_cleaned)} out of {len(df)} phones (deleted {len(df) - len(df_cleaned)} Lava phones)')
    df_cleaned.to_csv(path, index=False)

clean()
clean_csv('apps/api/data/phonos_ai.csv')
clean_csv('scraped_official_catalogues/Combined_Official_India_Smartphones_Catalogue.csv')
