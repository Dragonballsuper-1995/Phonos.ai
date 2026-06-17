from fastapi import APIRouter
from app.db.database import get_db_pool

router = APIRouter()

@router.get("/health")
async def health_check():
    try:
        pool = await get_db_pool()
        await pool.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
        
    return {
        "status": "healthy",
        "database": db_status
    }
