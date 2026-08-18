import sqlite3
import os
import time
import re
import requests
from typing import Optional, Dict, Any
from app.core.config import settings

CACHE_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/pricing_cache.db'))

def init_db():
    os.makedirs(os.path.dirname(CACHE_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(CACHE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_cache (
            phone_id TEXT PRIMARY KEY,
            phone_name TEXT,
            price REAL,
            store TEXT,
            store_url TEXT,
            last_updated INTEGER
        )
    ''')
    # Safe migration for existing DB
    try:
        cursor.execute("ALTER TABLE price_cache ADD COLUMN phone_name TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE price_cache ADD COLUMN store TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE price_cache ADD COLUMN store_url TEXT")
    except Exception:
        pass
    conn.commit()
    conn.close()

def get_cached_price(phone_id: str) -> Optional[Dict[str, Any]]:
    try:
        init_db()
        conn = sqlite3.connect(CACHE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT price, store, store_url, last_updated FROM price_cache WHERE phone_id = ?", (str(phone_id),))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            price, store, store_url, last_updated = row["price"], row["store"], row["store_url"], row["last_updated"]
            ttl_seconds = settings.PRICE_CACHE_TTL_HOURS * 3600
            if time.time() - last_updated < ttl_seconds and price and price > 0:
                return {
                    "price": price,
                    "store": store or "Amazon India",
                    "store_url": store_url or f"https://www.amazon.in/s?k={phone_id}",
                    "last_updated": last_updated
                }
    except Exception as e:
        print(f"[LivePricing] Cache read error: {e}")
    return None

def set_cached_price(phone_id: str, phone_name: str, price: float, store: str = "Amazon India", store_url: str = ""):
    try:
        init_db()
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO price_cache (phone_id, phone_name, price, store, store_url, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (str(phone_id), phone_name, float(price), store, store_url, int(time.time())))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[LivePricing] Cache write error: {e}")

def _fetch_serpapi(phone_name: str) -> Optional[Dict[str, Any]]:
    serp_key = os.getenv("SERPAPI_KEY", "")
    if not serp_key:
        return None
    try:
        from serpapi import GoogleSearch
        params = {
            "engine": "google_shopping",
            "q": f"{phone_name} price India",
            "google_domain": "google.co.in",
            "gl": "in",
            "hl": "en",
            "api_key": serp_key,
        }
        search = GoogleSearch(params)
        # Fast query
        results = search.get_dict()
        shopping_results = results.get("shopping_results", [])
        if shopping_results:
            first = shopping_results[0]
            raw_price = str(first.get("extracted_price") or first.get("price") or "")
            clean_num = re.findall(r'\d+', raw_price.replace(',', ''))
            if clean_num:
                price_val = float(''.join(clean_num)) if '.' not in raw_price else float(re.search(r'\d+\.?\d*', raw_price.replace(',', '')).group(0))
                return {
                    "price": price_val,
                    "store": first.get("merchant", "Online Store"),
                    "store_url": first.get("link", f"https://www.amazon.in/s?k={phone_name}")
                }
    except Exception as e:
        print(f"[LivePricing] SerpAPI failed: {e}")
    return None

def _fetch_apify_amazon(phone_name: str) -> Optional[Dict[str, Any]]:
    """Use Apify actor with user's token if available."""
    if not settings.APIFY_TOKEN:
        return None
    try:
        url = f"https://api.apify.com/v2/acts/apify~amazon-scraper/run-sync-get-dataset-items?token={settings.APIFY_TOKEN}"
        payload = {
            "search": phone_name,
            "domain": "in",
            "maxItems": 1
        }
        resp = requests.post(url, json=payload, timeout=2.0)
        if resp.status_code == 200:
            items = resp.json()
            if items and isinstance(items, list):
                item = items[0]
                price = item.get("price", {}).get("value")
                if price:
                    return {
                        "price": float(price),
                        "store": "Amazon India",
                        "store_url": item.get("url", f"https://www.amazon.in/s?k={phone_name}")
                    }
    except Exception as e:
        print(f"[LivePricing] Apify Amazon scraper skipped: {e}")
    return None

def get_live_price(phone_id: str, phone_name: str) -> Optional[float]:
    cached = get_cached_price(phone_id)
    if cached:
        return cached["price"]

    # 1. Try SerpAPI (only if configured)
    res = _fetch_serpapi(phone_name)
    if res and res.get("price", 0) > 0:
        set_cached_price(phone_id, phone_name, res["price"], res.get("store", "Amazon India"), res.get("store_url", ""))
        return res["price"]

    # 2. Try Apify Amazon (only if configured)
    res = _fetch_apify_amazon(phone_name)
    if res and res.get("price", 0) > 0:
        set_cached_price(phone_id, phone_name, res["price"], res.get("store", "Amazon India"), res.get("store_url", ""))
        return res["price"]

    return None

def get_live_pricing_details(phone_id: str, phone_name: str, default_price: float = 0.0) -> Dict[str, Any]:
    """
    Returns live pricing details instantly. If cached, uses cache.
    Otherwise uses verified database default_price immediately to prevent query hangs.
    """
    cached = get_cached_price(phone_id)
    if cached and cached.get("price", 0) > 0:
        return cached

    # Use default_price from database immediately without stalling pipeline
    final_price = default_price if default_price > 0 else 0.0
    safe_name = requests.utils.quote(phone_name)

    return {
        "price": final_price,
        "store": "Amazon India",
        "store_url": f"https://www.amazon.in/s?k={safe_name}",
        "last_updated": int(time.time())
    }
