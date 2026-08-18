import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.llm import generate_json

prompt = """
Evaluate these 2 candidate phones for user query: "gaming phone under 35000":
1. Realme GT 6 (Price: ₹28,999) - Snapdragon 8s Gen 3, 120W charge, 120Hz LTPO
2. Poco F6 (Price: ₹27,490) - Snapdragon 8s Gen 3, 90W charge, 120Hz AMOLED

Return JSON matching:
{
  "rankings": [
    {"candidate_id": 1, "score": 95.0, "match_reason": "Top cooling and 120W charge", "trade_off": "Realme UI bloat"},
    {"candidate_id": 2, "score": 92.0, "match_reason": "Flagship 8s Gen 3 value", "trade_off": "Plastic frame"}
  ]
}
"""

print("Testing generate_json...")
try:
    res = generate_json(prompt)
    print("SUCCESS! Output:")
    print(json.dumps(res, indent=2))
except Exception as e:
    print("FAILED:", e)
