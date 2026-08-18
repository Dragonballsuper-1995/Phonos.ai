import os
import re
import pandas as pd
from typing import Dict, Any, Optional

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/absa_phone_summary.csv'))

# In-memory fast cache
_absa_cache: Dict[str, Dict[str, float]] = {}

def load_cached_absa():
    """Load existing sentiment scores from CSV."""
    global _absa_cache
    if not _absa_cache and os.path.exists(CSV_PATH):
        try:
            df = pd.read_csv(CSV_PATH)
            for _, row in df.iterrows():
                model = str(row.get("model", "")).strip().lower()
                if model:
                    _absa_cache[model] = {
                        "camera": float(row.get("camera", 0.0)),
                        "battery": float(row.get("battery", 0.0)),
                        "performance": float(row.get("performance", 0.0)),
                        "display": float(row.get("display", 0.0)),
                    }
        except Exception as e:
            print(f"[YouTubeABSA] Error loading cached ABSA: {e}")

def fetch_live_sentiment(phone_name: str) -> Dict[str, float]:
    """
    Fetches sentiment scores instantly from CSV cache without blocking on live API requests.
    """
    global _absa_cache
    load_cached_absa()
    key = phone_name.lower().strip()
    if key in _absa_cache:
        return _absa_cache[key]
        
    for cached_k, scores in _absa_cache.items():
        if cached_k in key or key in cached_k:
            return scores
            
    # Default neutral sentiment with 0ms latency
    return {"camera": 0.0, "battery": 0.0, "performance": 0.0, "display": 0.0}
