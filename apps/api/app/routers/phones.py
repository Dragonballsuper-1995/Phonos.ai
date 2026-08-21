from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import httpx

from app.models.phone import PhoneListResponse, PhoneDetails
from app.db.queries import get_all_phones, count_phones, get_phone_by_slug, search_phones, insert_phone
from app.services.live_specs import get_or_fetch_live_phone
from app.core.config import settings

router = APIRouter()

@router.get("", response_model=PhoneListResponse)
async def list_phones(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    brand: Optional[str] = None
):
    phones = await get_all_phones(limit=limit, offset=offset)
    if brand:
        phones = [p for p in phones if p.brand.lower() == brand.lower()]
        
    total = await count_phones()
    return {"phones": phones, "total": total}

@router.get("/search", response_model=List[PhoneDetails])
async def search(q: str = Query(..., min_length=2)):
    # 1. Search local Fone Master Dataset first
    local_results = await search_phones(q)
    if local_results:
        return local_results
        
    # 2. Fallback to Multi-Source Live Specs Engine (MobileAPI / TechSpecs / GSMArena)
    live_phone = get_or_fetch_live_phone(q, auto_save=True)
    if live_phone:
        saved_results = await search_phones(live_phone["name"])
        if saved_results:
            return saved_results
        return [PhoneDetails.model_validate(live_phone)]
        
    return []

@router.get("/{name}", response_model=PhoneDetails)
async def get_phone(name: str):
    phone = await get_phone_by_slug(name)
    if not phone:
        # Try live lookup
        live_phone = get_or_fetch_live_phone(name, auto_save=True)
        if live_phone:
            return PhoneDetails.model_validate(live_phone)
        raise HTTPException(status_code=404, detail="Phone not found")
    return phone

from app.services.hardware_similarity import find_similar_phones
from app.services.hardware_scorer import normalize_hardware_vector

@router.get("/{name}/similar")
async def get_similar_phones(
    name: str,
    budget: Optional[float] = Query(None, description="Max price filter in INR"),
    top_k: int = Query(5, ge=1, le=20),
):
    """
    Returns phones with the most similar hardware profile to the given phone.
    Uses pre-computed L2-normalised hardware vectors and dot-product cosine similarity.
    """
    source_phone = await get_phone_by_slug(name)
    if not source_phone:
        live_phone = get_or_fetch_live_phone(name, auto_save=True)
        if live_phone:
            source_phone = PhoneDetails.model_validate(live_phone)
        else:
            raise HTTPException(status_code=404, detail=f"Phone '{name}' not found")

    query_vec = normalize_hardware_vector(source_phone)
    similar = find_similar_phones(
        query_vector=query_vec,
        top_k=top_k,
        max_budget=budget,
        exclude_ids=[source_phone.id] if source_phone.id else None,
    )
    return {
        "source": source_phone.name or name,
        "similar_phones": similar
    }


from scripts.daily_sync_worker import run_daily_sync
import asyncio

@router.post("/sync/daily")
async def trigger_daily_sync(dry_run: bool = False):
    """
    Triggers the continuous ingestion & catalog sync worker.
    """
    loop = asyncio.get_event_loop()
    stats = await loop.run_in_executor(None, run_daily_sync, dry_run)
    return {"status": "success", "stats": stats}
