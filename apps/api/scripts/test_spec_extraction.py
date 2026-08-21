import asyncio
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db.queries import get_phones_by_ids

async def test():
    phones = await get_phones_by_ids([189, 1370, 407, 1119])
    for p in phones:
        print(f"[{p.brand}] {p.fullName} (₹{p.price:,.0f})")
        print(f"  Processor: {p.specs.processor}")
        print(f"  Display:   {p.specs.display} ({p.specs.displaySize}, {p.specs.refreshRate})")
        print(f"  Cameras:   Main: {p.specs.mainCamera} | Selfie: {p.specs.selfieCamera}")
        print(f"  Battery:   {p.specs.battery} ({p.specs.charging})")
        print(f"  Build:     {p.specs.waterResistance} | {p.specs.biometrics}")
        print("-" * 70)

if __name__ == "__main__":
    asyncio.run(test())
