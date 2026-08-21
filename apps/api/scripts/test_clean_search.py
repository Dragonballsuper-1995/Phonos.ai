import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
sys.path.insert(0, os.path.abspath('.'))
from app.db.queries import search_phones

import asyncio

async def main():
    for query in ['realme', 's26', 'oneplus 15', 'p4 power']:
        res = (await search_phones(query))[:5]
        print(f"\n--- Search '{query}' ({len(res)} results) ---")
        for p in res:
            print(f"  [{p.brand}] {p.name} (Price: ₹{p.price})")

asyncio.run(main())
