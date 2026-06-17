import aiosqlite
from typing import Optional
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/fone_master.db'))

class Database:
    conn: Optional[aiosqlite.Connection] = None

db = Database()

async def get_db_pool() -> aiosqlite.Connection:
    if db.conn is None:
        db.conn = await aiosqlite.connect(DB_PATH)
        db.conn.row_factory = aiosqlite.Row
    return db.conn

async def close_db_pool():
    if db.conn is not None:
        await db.conn.close()
