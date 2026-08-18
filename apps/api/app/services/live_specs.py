import os
import re
import json
import sqlite3
import requests
from typing import Optional, Dict, Any, List
from app.core.config import settings

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/fone_master.db'))

def clean_phone_name(brand: str, raw_name: str) -> str:
    """Strip redundant brand prefixes and RAM/ROM brackets."""
    name = raw_name.strip()
    escaped_brand = re.escape(brand.strip())
    name = re.sub(rf'^{escaped_brand}\s*', '', name, flags=re.IGNORECASE).strip()
    name = re.sub(r'\s*\(\d+GB\s+RAM\s*\+\s*\d+GB\)', '', name, flags=re.IGNORECASE).strip()
    name = re.sub(r'\s*\(\d+GB\s*\+\s*\d+GB\)', '', name, flags=re.IGNORECASE).strip()
    name = re.sub(r'\s*\(\d+GB\s+RAM\)', '', name, flags=re.IGNORECASE).strip()
    return f"{brand} {name}".strip()

def fetch_mobileapi_specs(query: str) -> Optional[Dict[str, Any]]:
    """Fetch structured specs from MobileAPI.dev."""
    if not settings.MOBILEAPI_KEY:
        return None
    try:
        headers = {"Authorization": f"Bearer {settings.MOBILEAPI_KEY}"}
        search_url = "https://api.mobileapi.dev/devices/search/"
        resp = requests.get(search_url, params={"name": query}, headers=headers, timeout=8.0)
        if resp.status_code != 200:
            return None
        data = resp.json()
        devices = data.get("devices", [])
        if not devices:
            return None
        
        # Pick best match
        device = devices[0]
        device_id = device.get("id")
        brand = device.get("manufacturer_name", "Unknown")
        name = device.get("name", query)
        
        # Fetch full device details
        detail_resp = requests.get(f"https://api.mobileapi.dev/devices/{device_id}", headers=headers, timeout=8.0)
        detail_data = detail_resp.json() if detail_resp.status_code == 200 else device
        
        full_name = clean_phone_name(brand, name)
        
        # Parse launch year
        announced = str(detail_data.get("announced_date") or "")
        year_match = re.search(r'202[0-6]', announced)
        launch_year = int(year_match.group(0)) if year_match else 2026

        return {
            "brand": brand,
            "name": full_name,
            "price": 0.0,
            "price_numeric": 0.0,
            "os": str(detail_data.get("platform", {}).get("os") or "Android"),
            "source": "mobileapi.dev",
            "released_in_india": 1,
            "launch_year": launch_year,
            "raw_specs": json.dumps(detail_data),
            "ai_verified": 1
        }
    except Exception as e:
        print(f"[LiveSpecs] MobileAPI error for '{query}': {e}")
        return None

def fetch_techspecs_specs(query: str) -> Optional[Dict[str, Any]]:
    """Fetch standardized specs from TechSpecs.io v5."""
    if not settings.TECHSPECS_API_KEY or not settings.TECHSPECS_API_ID:
        return None
    try:
        headers = {
            "Accept": "application/json",
            "X-API-KEY": settings.TECHSPECS_API_KEY,
            "X-API-ID": settings.TECHSPECS_API_ID
        }
        search_url = "https://api.techspecs.io/v5/products/search"
        resp = requests.get(search_url, params={"query": query}, headers=headers, timeout=8.0)
        if resp.status_code != 200:
            return None
        data = resp.json()
        products = data.get("data", [])
        if not products:
            return None
        
        item = products[0]
        prod_meta = item.get("Product", {})
        brand = prod_meta.get("Brand", "Unknown")
        model = prod_meta.get("Model", query)
        full_name = clean_phone_name(brand, model)
        
        release_date = str(item.get("Release Date", ""))
        year_match = re.search(r'202[0-6]', release_date)
        launch_year = int(year_match.group(0)) if year_match else 2026
        
        return {
            "brand": brand,
            "name": full_name,
            "price": 0.0,
            "price_numeric": 0.0,
            "os": "Android" if "apple" not in brand.lower() else "iOS",
            "source": "techspecs.io",
            "released_in_india": 1,
            "launch_year": launch_year,
            "raw_specs": json.dumps(item),
            "ai_verified": 1
        }
    except Exception as e:
        print(f"[LiveSpecs] TechSpecs error for '{query}': {e}")
        return None

def fetch_gsmarena_specs(query: str) -> Optional[Dict[str, Any]]:
    """Zero-key fallback: fetches specs from open-source GSMArena API proxy."""
    try:
        url = f"https://phone-specs-api.vercel.app/search?query={query}"
        resp = requests.get(url, timeout=8.0)
        if resp.status_code != 200:
            return None
        data = resp.json()
        phones = data.get("data", {}).get("phones", [])
        if not phones:
            return None
        
        phone = phones[0]
        detail_url = phone.get("detail")
        if not detail_url:
            return None
        
        detail_resp = requests.get(detail_url, timeout=8.0)
        if detail_resp.status_code != 200:
            return None
        detail_data = detail_resp.json().get("data", {})
        
        brand = detail_data.get("brand", "Unknown")
        phone_name = detail_data.get("phone_name", query)
        full_name = clean_phone_name(brand, phone_name)
        
        return {
            "brand": brand,
            "name": full_name,
            "price": 0.0,
            "price_numeric": 0.0,
            "os": "Android" if "apple" not in brand.lower() else "iOS",
            "source": "gsmarena",
            "released_in_india": 1,
            "launch_year": 2026,
            "raw_specs": json.dumps(detail_data),
            "ai_verified": 1
        }
    except Exception as e:
        print(f"[LiveSpecs] GSMArena error for '{query}': {e}")
        return None

def save_phone_to_db(phone: Dict[str, Any]) -> bool:
    """Persist a live fetched phone into fone_master.db."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Check if already exists
        cur.execute("SELECT id FROM phones WHERE name = ? COLLATE NOCASE", (phone["name"],))
        row = cur.fetchone()
        
        if row:
            # Update existing
            cur.execute("""
                UPDATE phones 
                SET brand = ?, price_numeric = COALESCE(NULLIF(?, 0), price_numeric),
                    raw_specs = ?, os = ?, source = ?, ai_verified = 1
                WHERE id = ?
            """, (phone["brand"], phone.get("price_numeric", 0), phone["raw_specs"], phone["os"], phone["source"], row[0]))
        else:
            # Insert new phone
            cur.execute("""
                INSERT INTO phones (brand, name, price, price_numeric, os, source, released_in_india, launch_year, raw_specs, ai_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                phone["brand"],
                phone["name"],
                f"Rs. {int(phone.get('price_numeric', 0))}" if phone.get("price_numeric") else "Price on Request",
                phone.get("price_numeric", 0.0),
                phone["os"],
                phone["source"],
                phone.get("released_in_india", 1),
                phone.get("launch_year", 2026),
                phone["raw_specs"],
                1
            ))
            
            # Rebuild FTS
            try:
                cur.execute("INSERT INTO phones_fts(phones_fts, rank) VALUES('rebuild', 0);")
            except Exception:
                pass
                
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[LiveSpecs] DB save failed for '{phone.get('name')}': {e}")
        return False

def get_or_fetch_live_phone(query: str, auto_save: bool = True) -> Optional[Dict[str, Any]]:
    """
    Search SQLite first; if missing, query Tier 1 (MobileAPI) -> Tier 2 (TechSpecs) -> Tier 3 (GSMArena).
    """
    # 1. Check local SQLite DB
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT brand, name, price, price_numeric, os, source, released_in_india, launch_year, raw_specs, ai_verified
            FROM phones 
            WHERE name LIKE ? AND released_in_india = 1
            LIMIT 1
        """, (f"%{query}%",))
        row = cur.fetchone()
        conn.close()
        if row:
            return dict(row)
    except Exception as e:
        print(f"[LiveSpecs] SQLite lookup error: {e}")

    # 2. Tier 1: MobileAPI.dev
    specs = fetch_mobileapi_specs(query)
    
    # 3. Tier 2: TechSpecs.io
    if not specs:
        specs = fetch_techspecs_specs(query)
        
    # 4. Tier 3: GSMArena proxy
    if not specs:
        specs = fetch_gsmarena_specs(query)
        
    if specs and auto_save:
        save_phone_to_db(specs)
        
    return specs
