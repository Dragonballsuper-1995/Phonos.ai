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
    import re
    import json
    from rapidfuzz import fuzz, process

    clean_q = re.sub(r'[^\w\s]', ' ', query_str).strip()
    if not clean_q:
        return []
    
    tokens = clean_q.split()
    fts_query = " ".join(f"{w}*" for w in tokens)
    
    seen_ids = set()
    rows = []

    # 1. Fast FTS5 prefix match
    try:
        cursor = await conn.execute(
            """
            SELECT p.rowid as id, p.* 
            FROM phones p 
            JOIN phones_fts f ON p.rowid = f.rowid 
            WHERE phones_fts MATCH ? 
            ORDER BY p.is_current_catalogue DESC, p.launch_year DESC, p.rowid DESC 
            LIMIT 25
            """,
            (fts_query,)
        )
        fts_rows = await cursor.fetchall()
        for r in fts_rows:
            if r['id'] not in seen_ids:
                seen_ids.add(r['id'])
                rows.append(r)
    except Exception:
        pass

    # 2. Multi-token substring match fallback
    if len(rows) < 10:
        like_clauses = " AND ".join(["(name LIKE ? OR brand LIKE ?)" for _ in tokens])
        params = []
        for t in tokens:
            params.extend([f"%{t}%", f"%{t}%"])
        params.append(25 - len(rows))

        try:
            cursor = await conn.execute(
                f"SELECT rowid as id, * FROM phones WHERE {like_clauses} ORDER BY is_current_catalogue DESC, launch_year DESC, rowid DESC LIMIT ?",
                params
            )
            like_rows = await cursor.fetchall()
            for r in like_rows:
                if r['id'] not in seen_ids:
                    seen_ids.add(r['id'])
                    rows.append(r)
        except Exception:
            pass

    # 3. RapidFuzz fallback for typos (e.g. 'samsng', 'iphne', 'oneplus15')
    if len(rows) < 5:
        try:
            cursor = await conn.execute(
                "SELECT rowid as id, * FROM phones WHERE is_current_catalogue = 1 OR released_in_india = 1 LIMIT 600"
            )
            all_candidates = await cursor.fetchall()
            candidate_names = [f"{c['brand']} {c['name']}".lower() for c in all_candidates]
            
            matches = process.extract(
                query_str.lower(),
                candidate_names,
                scorer=fuzz.partial_ratio,
                limit=15,
                score_cutoff=65
            )
            
            for match in matches:
                matched_idx = match[2]
                r = all_candidates[matched_idx]
                if r['id'] not in seen_ids:
                    seen_ids.add(r['id'])
                    rows.append(r)
                    if len(rows) >= 20:
                        break
        except Exception:
            pass

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

