import os
import sys
import pandas as pd
import json
import re

sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))

files = [
    'smartprix_smartphones_april_2026.csv',
    'Analysed and Cleaned Mobiles Dataset from Smartprix.csv',
    'device_specs_structured_dataset.csv',
    'mobiles.csv',
    'cleaned_3.csv',
    'raw_gsmarena.csv'
]

for f in files:
    p = os.path.join(DATA_DIR, f)
    if os.path.exists(p):
        df = pd.read_csv(p, low_memory=False)
        print(f"File: {f} | Rows: {len(df)} | Columns: {len(df.columns)}")
        # Check date/price columns
        date_cols = [c for c in df.columns if any(k in c.lower() for k in ['date', 'year', 'launch', 'announced', 'status'])]
        price_cols = [c for c in df.columns if 'price' in c.lower()]
        print(f"   Date cols: {date_cols}")
        print(f"   Price cols: {price_cols}")
