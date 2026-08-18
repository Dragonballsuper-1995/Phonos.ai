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
