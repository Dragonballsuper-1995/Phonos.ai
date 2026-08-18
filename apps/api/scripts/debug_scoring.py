import sqlite3
import json
import sys
import os
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.recommender import extract_features, get_ranker_model, ml_score_phones
from app.models.phone import PhoneDetails

conn = sqlite3.connect('apps/api/data/fone_master.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Test phones for 20000 budget
c.execute("SELECT rowid as id, * FROM phones WHERE released_in_india=1 AND price_numeric BETWEEN 14000 AND 21000 ORDER BY price_numeric DESC LIMIT 20")
rows = c.fetchall()
phones_20k = []
for r in rows:
    d = dict(r)
    d['raw_specs'] = json.loads(d['raw_specs']) if d['raw_specs'] else {}
    phones_20k.append(PhoneDetails(**d))

print("=== Scoring 20k Budget Phones ===")
scored_20k = ml_score_phones(phones_20k, "Student", 20000)
for item in scored_20k[:10]:
    p = item['phone']
    print(f"{p.name} | ₹{p.price_numeric} | Score: {item['score']:.2f} | Reasons: {item['match_reasons']}")

# Test phones for 120000 budget
c.execute("SELECT rowid as id, * FROM phones WHERE released_in_india=1 AND price_numeric BETWEEN 80000 AND 125000 ORDER BY price_numeric DESC LIMIT 20")
rows = c.fetchall()
phones_120k = []
for r in rows:
    d = dict(r)
    d['raw_specs'] = json.loads(d['raw_specs']) if d['raw_specs'] else {}
    phones_120k.append(PhoneDetails(**d))

print("\n=== Scoring 120k Budget Phones ===")
scored_120k = ml_score_phones(phones_120k, "Executive", 120000)
for item in scored_120k[:10]:
    p = item['phone']
    print(f"{p.name} | ₹{p.price_numeric} | Score: {item['score']:.2f} | Reasons: {item['match_reasons']}")

conn.close()
