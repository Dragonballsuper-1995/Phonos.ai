import requests
import json
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HF_BASE_URL = "https://sujalchhajed925-phonos-api.hf.space"

def run_test(name, fn):
    print(f"\n==================================================")
    print(f"▶ RUNNING TEST: {name}")
    print(f"==================================================")
    try:
        t0 = time.time()
        res = fn()
        elapsed = time.time() - t0
        print(f"✓ PASS ({elapsed:.2f}s): {res}")
        return True
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False

# 1. Health / Root
def test_root():
    url = f"{HF_BASE_URL}/"
    r = requests.get(url, timeout=30)
    return f"HTTP {r.status_code} -> {r.json()}"

# 2. Search 'realme' (Check no 'ow' or 'realmeow')
def test_search_realme():
    url = f"{HF_BASE_URL}/api/v1/phones/search?q=realme"
    r = requests.get(url, timeout=30)
    data = r.json()
    names = [p.get('name') or p.get('fullName') for p in data]
    assert len(data) > 0, "No results returned for realme"
    assert "realmeow" not in [n.lower() for n in names], "Found realmeow in search results!"
    assert "ow" not in [n.lower() for n in names], "Found ow in search results!"
    return f"Returned {len(data)} phones. Top 3: {names[:3]}"

# 3. Search 'p4 power' (Check storage variants)
def test_search_p4_power():
    url = f"{HF_BASE_URL}/api/v1/phones/search?q=p4%20power"
    r = requests.get(url, timeout=30)
    data = r.json()
    assert len(data) >= 3, "Expected at least 3 variants for P4 Power"
    details = [f"ID {p.get('id')}: {p.get('name')} (Price: ₹{p.get('price')}, RAM: {p.get('specs', {}).get('ram')}, Storage: {p.get('specs', {}).get('storage')})" for p in data[:3]]
    return f"Found {len(data)} variants:\n  " + "\n  ".join(details)

# 4. Compare Suite (S26, Realme P4 Power, OnePlus 15)
def test_compare():
    url = f"{HF_BASE_URL}/api/v1/compare?ids=1370,459,407"
    r = requests.get(url, timeout=30)
    data = r.json()
    phones = data.get('phones', [])
    assert len(phones) == 3, f"Expected 3 phones, got {len(phones)}"
    summary = []
    for p in phones:
        summary.append(
            f"[{p.get('brand')}] {p.get('name')} | SoC: {p.get('specs', {}).get('processor')} | Battery: {p.get('specs', {}).get('battery')} | Camera: {p.get('specs', {}).get('mainCamera')}"
        )
    return "Compared 3 phones successfully:\n  " + "\n  ".join(summary)

# 5. Recommendation Engine (Student, 35000 budget)
def test_recommend():
    url = f"{HF_BASE_URL}/api/v1/recommend"
    payload = {
        "budget": 35000,
        "persona": "student",
        "preferences": {}
    }
    r = requests.post(url, json=payload, timeout=45)
    data = r.json()
    recs = data.get('recommendations', [])
    assert len(recs) > 0, "No recommendations returned"
    top = recs[0]
    return f"Recommended {len(recs)} phones. #1: [{top.get('brand')}] {top.get('name')} (Score: {top.get('matchScore')}%, Price: ₹{top.get('price')})"

if __name__ == "__main__":
    print(f"Testing HuggingFace Deployed Backend at: {HF_BASE_URL}")
    results = [
        run_test("Root / Health Endpoint", test_root),
        run_test("Search 'realme' (Hygiene Verification)", test_search_realme),
        run_test("Search 'p4 power' (RAM & Storage Variants)", test_search_p4_power),
        run_test("Compare Suite Multi-Device Differential", test_compare),
        run_test("ML Recommender Pipeline (Student Persona, ₹35,000)", test_recommend),
    ]

    total = len(results)
    passed = sum(results)
    print(f"\n==================================================")
    print(f"SUMMARY: {passed}/{total} Tests Passed ({passed/total*100:.0f}%)")
    print(f"==================================================")
