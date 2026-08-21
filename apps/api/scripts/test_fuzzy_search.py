import asyncio
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db.queries import search_phones

async def main():
    queries = ['s26', 's25', '12r', 'oneplus 15', 'samsng', '16 pro']
    for q in queries:
        results = await search_phones(q)
        print(f"Query: \"{q}\" -> Found {len(results)} matches:")
        for p in results[:3]:
            print(f"  - [{p.brand}] {p.fullName} (₹{p.price:,.0f}) | SoC: {p.specs.processor}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
