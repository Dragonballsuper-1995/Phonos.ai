"""
End-to-end recommendation test:
Simulates what happens when a user asks for Gamer phones with 150000rs budget.
Should NOT show Xiaomi 18 Ultra, Samsung S27 Ultra, etc.
"""
import sys, asyncio
sys.path.insert(0, '.')

# Secrets are loaded from environment or .env file

from app.services.verifier import verify_recommendations, KNOWN_NOT_IN_INDIA
from app.models.phone import PhoneDetails

# Simulate the problematic phones from the bug report
problematic = [
    {"name": "Xiaomi 18 Ultra",         "brand": "Xiaomi",  "price_numeric": 119990, "launch_year": 2027},
    {"name": "Xiaomi 18 5G",            "brand": "Xiaomi",  "price_numeric": 94990,  "launch_year": 2027},
    {"name": "Samsung Galaxy S27 Ultra 5G", "brand": "Samsung","price_numeric": 149990,"launch_year": 2027},
    {"name": "Samsung Galaxy S26 Ultra", "brand": "Samsung", "price_numeric": 131700, "launch_year": 2026},
    {"name": "Oppo Find X10 Pro 5G",    "brand": "Oppo",    "price_numeric": 119990, "launch_year": 2026},
]

# And also the EASY mode Student phones
student_phones = [
    {"name": "IQOO Z11 Turbo",      "brand": "iQOO",    "price_numeric": 29990, "launch_year": 2026},
    {"name": "IQOO Z11 Turbo Pro",  "brand": "iQOO",    "price_numeric": 29990, "launch_year": 2026},
    {"name": "Vivo V70e",           "brand": "Vivo",    "price_numeric": 29990, "launch_year": 2026},
    {"name": "Realme Neo 7 Turbo",  "brand": "realme",  "price_numeric": 26990, "launch_year": 2026},
    {"name": "Infinix Note 60 Pro 5G","brand": "Infinix","price_numeric": 25990, "launch_year": 2026},
]

def make_candidate(d: dict, score: float = 90.0):
    phone = PhoneDetails(
        brand=d["brand"],
        name=d["name"],
        fullName=f"{d['brand']} {d['name']}",
        price_numeric=float(d["price_numeric"]),
        launch_year=float(d["launch_year"]),
        raw_specs=None,
    )
    return {"phone": phone, "score": score, "match_reasons": ["Test"], "trade_offs": []}

print("=" * 60)
print("TEST 1: Gamer, Rs 1,50,000 -- Should block S27 Ultra, Xiaomi 18")
print("=" * 60)
candidates = [make_candidate(p, 100 - i * 5) for i, p in enumerate(problematic)]
result = verify_recommendations(candidates)
print(f"Input: {len(candidates)} phones -> Output: {len(result)} verified")
for r in result:
    print(f"  PASS: {r['phone'].name} ({r['phone'].brand}) - {r['phone'].price_numeric}")
blocked = [p for p in problematic if not any(p['name'] in r['phone'].name for r in result)]
for b in blocked:
    print(f"  BLOCKED: {b['name']}")

print()
print("=" * 60)
print("TEST 2: Student, Rs 30,000 -- Should block IQOO Z11 Turbo, V70e")
print("=" * 60)
candidates2 = [make_candidate(p, 100 - i * 2) for i, p in enumerate(student_phones)]
result2 = verify_recommendations(candidates2)
print(f"Input: {len(candidates2)} phones -> Output: {len(result2)} verified")
for r in result2:
    print(f"  PASS: {r['phone'].name} ({r['phone'].brand})")
blocked2 = [p for p in student_phones if not any(p['name'] in r['phone'].name for r in result2)]
for b in blocked2:
    print(f"  BLOCKED: {b['name']}")
