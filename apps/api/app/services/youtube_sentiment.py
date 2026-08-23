"""
youtube_sentiment.py — SQLite-Backed Aspect Sentiment Store
===========================================================
Reads ABSA aspect scores directly from phonos_ai.db.
In-process memory cache with lazy loading ensures 0ms latency during recommendation scoring.
"""
import os
import sqlite3
from typing import Dict

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../data/phonos_ai.db')
)

_cache: Dict[str, Dict[str, float]] = {}
_loaded: bool = False

NEUTRAL = {"camera": 0.0, "battery": 0.0, "performance": 0.0, "display": 0.0, "build": 0.0}

def _load():
    global _loaded, _cache
    if _loaded:
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT name, absa_camera, absa_battery, absa_performance, absa_display, absa_build "
            "FROM phones "
            "WHERE absa_camera IS NOT NULL OR absa_battery IS NOT NULL OR absa_performance IS NOT NULL"
        ).fetchall()
        conn.close()
        for name, cam, bat, perf, disp, build in rows:
            if name:
                _cache[name.lower().strip()] = {
                    "camera": float(cam or 0.0),
                    "battery": float(bat or 0.0),
                    "performance": float(perf or 0.0),
                    "display": float(disp or 0.0),
                    "build": float(build or 0.0),
                }
        print(f"[ABSA] Loaded {len(_cache)} phone sentiment profiles from database.")
    except Exception as e:
        print(f"[ABSA] DB load warning: {e}")
    _loaded = True

def fetch_live_sentiment(phone_name: str) -> Dict[str, float]:
    """
    Fetches sentiment scores instantly from in-memory cache backed by phonos_ai.db.
    """
    _load()
    if not phone_name:
        return NEUTRAL
    key = phone_name.lower().strip()
    return _cache.get(key, NEUTRAL)

