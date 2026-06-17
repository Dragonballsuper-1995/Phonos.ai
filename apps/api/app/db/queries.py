from typing import List, Optional
from app.db.database import get_db_pool
from app.models.phone import PhoneDetails
import json

async def get_all_phones(max_budget: Optional[float] = None, limit: int = 20, offset: int = 0) -> List[PhoneDetails]:
    conn = await get_db_pool()
    # Ignoring max_budget filtering in SQL for now as price is string, handled in python level
    cursor = await conn.execute("SELECT rowid as id, * FROM phones LIMIT ? OFFSET ?", (limit, offset))
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
    cursor = await conn.execute("SELECT COUNT(*) FROM phones")
    row = await cursor.fetchone()
    return row[0] if row else 0

async def search_phones(query_str: str) -> List[PhoneDetails]:
    conn = await get_db_pool()
    cursor = await conn.execute(
        "SELECT rowid as id, * FROM phones WHERE name LIKE ? OR brand LIKE ? LIMIT 20",
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
