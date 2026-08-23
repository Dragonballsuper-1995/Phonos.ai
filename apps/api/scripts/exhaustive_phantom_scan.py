import sqlite3
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('apps/api/data/phonos_ai.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT rowid, name, brand, source, price_numeric, launch_year, raw_specs FROM phones WHERE released_in_india=1")
active_phones = c.fetchall()

print(f"Total active India phones currently: {len(active_phones)}")

# Patterns of speculative future generations or China-only series
suspicious_patterns = [
    # Future / Speculative Samsung
    r'Galaxy S2[6-9]', r'Galaxy Z Fold [7-9]', r'Galaxy Z Flip [7-9]', r'Galaxy A[6-9]7', r'Galaxy M[6-9]7', r'Galaxy F[6-9]7',
    # Future / Speculative iPhone
    r'iPhone 1[7-9]', r'iPhone 2[0-9]', r'iPhone Air', r'iPhone Ultra',
    # Future / Speculative Pixel
    r'Pixel 1[0-9]', r'Pixel 2[0-9]',
    # Future / Speculative Xiaomi & China-only
    r'Xiaomi 1[6-9]', r'Xiaomi 2[0-9]', r'Mix Fold', r'Mix Flip', r'Redmi Note 1[5-9]', r'Redmi 1[5-9]',
    # Future / Speculative OnePlus
    r'OnePlus 1[4-9]', r'OnePlus 2[0-9]', r'OnePlus Ace', r'OnePlus Open 2', r'OnePlus V Fold',
    # Future / Speculative Vivo & China-only
    r'Vivo S\d+', r'Vivo V[5-9]\d', r'Vivo V[1-9]\d\d', r'Vivo X[3-9]\d\d', r'Vivo Y[6-9]\d\d', r'Vivo X Fold [4-9]',
    # Future / Speculative Oppo & China-only
    r'Oppo Reno 1[3-9]', r'Oppo Reno [2-9]\d', r'Oppo Find X[8-9]', r'Oppo Find X1\d', r'Oppo Find N[4-9]', r'Oppo A[6-9]',
    # Future / Speculative Realme & China-only
    r'Realme 1[4-9]', r'Realme 2[0-9]', r'Realme GT [7-9]', r'Realme GT Neo [7-9]', r'Realme V\d+', r'Realme C[7-9]\d', r'Realme P[3-9]',
    # Future / Speculative Motorola
    r'Moto X\d+', r'Edge 6\d', r'Edge 7\d', r'Razr 6\d', r'Razr 7\d', r'Moto G[6-9]\d', r'Moto S\d+',
    # Future / Speculative Poco
    r'Poco F[7-9]', r'Poco X[7-9]', r'Poco M[7-9]', r'Poco C[7-9]'
]

combined_regex = re.compile('|'.join(f'({p})' for p in suspicious_patterns), re.IGNORECASE)

flagged_phones = []
for r in active_phones:
    name = r['name']
    specs_str = str(r['raw_specs'] or '')
    match = combined_regex.search(name)
    is_expected_in_specs = 'expected' in specs_str.lower() or 'rumor' in specs_str.lower() or 'coming soon' in specs_str.lower()
    
    if match or is_expected_in_specs:
        flagged_phones.append((r['rowid'], r['brand'], name, r['price_numeric'], r['launch_year'], match.group(0) if match else 'Expected in specs'))

print(f"\nTotal suspicious / speculative / China-only phones flagged: {len(flagged_phones)}")
print("Sample 30 flagged phones:")
for p in flagged_phones[:30]:
    print(f"  ID={p[0]} | {p[1]} | {p[2]} | ₹{p[3]} | Reason: {p[5]}")

conn.close()
