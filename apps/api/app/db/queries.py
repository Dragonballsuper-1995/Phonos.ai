from typing import List, Optional
from app.db.database import get_db_pool
from app.models.phone import PhoneDetails
import json

async def get_all_phones(max_budget: Optional[float] = None, limit: int = 20, offset: int = 0) -> List[PhoneDetails]:
    conn = await get_db_pool()
    # Clean SQL-level budget filtering and sorting by launch_year and insertion rowid.
    # We filter only for phones officially released in India (released_in_india = 1).
    if max_budget is not None:
        cursor = await conn.execute(
            "SELECT rowid as id, * FROM phones WHERE price_numeric <= ? AND released_in_india = 1 ORDER BY is_current_catalogue DESC, price_numeric DESC, launch_year DESC, rowid DESC LIMIT ? OFFSET ?",
            (max_budget, limit, offset)
        )
    else:
        cursor = await conn.execute(
            "SELECT rowid as id, * FROM phones WHERE released_in_india = 1 ORDER BY is_current_catalogue DESC, launch_year DESC, rowid DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )

    rows = await cursor.fetchall()
    result = []
    for row in rows:
        d = dict(row)
        if 'raw_specs' in d and isinstance(d['raw_specs'], str):
            try:
                d['raw_specs'] = json.loads(d['raw_specs'])
            except:
                d['raw_specs'] = {}
        result.append(PhoneDetails(**d))
    return result

async def count_phones() -> int:
    conn = await get_db_pool()
    cursor = await conn.execute("SELECT COUNT(*) FROM phones WHERE released_in_india = 1")
    row = await cursor.fetchone()
    return row[0] if row else 0

async def search_phones(query_str: str) -> List[PhoneDetails]:
    if not query_str.strip():
        return []
    conn = await get_db_pool()
    
    # Tokenize for FTS5 full-text matching (prefix match on terms)
    import re
    clean_q = re.sub(r'[^\w\s]', '', query_str).strip()
    if not clean_q:
        return []
    
    fts_query = " ".join(f"{w}*" for w in clean_q.split())
    
    try:
        # Perform super-fast join with FTS virtual table
        cursor = await conn.execute(
            """
            SELECT p.rowid as id, p.* 
            FROM phones p 
            JOIN phones_fts f ON p.rowid = f.rowid 
            WHERE phones_fts MATCH ? 
            ORDER BY p.launch_year DESC, p.rowid DESC 
            LIMIT 30
            """,
            (fts_query,)
        )
        rows = await cursor.fetchall()
        
        # Fallback to standard LIKE if FTS yields nothing
        if not rows:
            cursor = await conn.execute(
                "SELECT rowid as id, * FROM phones WHERE name LIKE ? OR brand LIKE ? ORDER BY launch_year DESC, rowid DESC LIMIT 30",
                (f"%{query_str}%", f"%{query_str}%")
            )
            rows = await cursor.fetchall()
    except Exception as e:
        # Standard query fallback
        cursor = await conn.execute(
            "SELECT rowid as id, * FROM phones WHERE name LIKE ? OR brand LIKE ? ORDER BY launch_year DESC, rowid DESC LIMIT 30",
            (f"%{query_str}%", f"%{query_str}%")
        )
        rows = await cursor.fetchall()
        
    result = []
    for row in rows:
        d = dict(row)
        if 'raw_specs' in d and isinstance(d['raw_specs'], str):
            try:
                d['raw_specs'] = json.loads(d['raw_specs'])
            except:
                d['raw_specs'] = {}
        result.append(PhoneDetails(**d))
    return result

async def get_phone_by_slug(slug: str) -> Optional[PhoneDetails]:
    conn = await get_db_pool()
    cursor = await conn.execute("SELECT rowid as id, * FROM phones WHERE name = ?", (slug,))
    row = await cursor.fetchone()
    if row:
        d = dict(row)
        if 'raw_specs' in d and isinstance(d['raw_specs'], str):
            try:
                d['raw_specs'] = json.loads(d['raw_specs'])
            except:
                d['raw_specs'] = {}
        return PhoneDetails(**d)
    return None

async def insert_phone(phone_data: dict) -> PhoneDetails:
    conn = await get_db_pool()
    brand = phone_data.get('brand', 'Unknown')
    name = phone_data.get('name', 'Unknown')
    price = phone_data.get('price', '')
    os_ver = phone_data.get('os', '')
    raw_specs = json.dumps(phone_data)
    
    cursor = await conn.execute(
        "INSERT INTO phones (brand, name, price, os, source, raw_specs) VALUES (?, ?, ?, ?, ?, ?)",
        (brand, name, price, os_ver, 'MobileAPI', raw_specs)
    )
    await conn.commit()
    
    return PhoneDetails(
        id=cursor.lastrowid,
        brand=brand,
        name=name,
        price=str(price) if price else None,
        os=str(os_ver) if os_ver else None,
        raw_specs=phone_data
    )

async def get_phones_by_ids(ids: List[int]) -> List[PhoneDetails]:
    if not ids:
        return []
    conn = await get_db_pool()
    placeholders = ",".join("?" for _ in ids)
    cursor = await conn.execute(
        f"SELECT rowid as id, * FROM phones WHERE rowid IN ({placeholders})", ids
    )
    rows = await cursor.fetchall()
    result = []
    for row in rows:
        d = dict(row)
        if 'raw_specs' in d and isinstance(d['raw_specs'], str):
            try:
                d['raw_specs'] = json.loads(d['raw_specs'])
            except:
                d['raw_specs'] = {}
        result.append(PhoneDetails(**d))
    return result

async def get_brand_catalogues() -> List[dict]:
    conn = await get_db_pool()
    try:
        cursor = await conn.execute("SELECT * FROM brand_catalogues ORDER BY brand ASC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []

