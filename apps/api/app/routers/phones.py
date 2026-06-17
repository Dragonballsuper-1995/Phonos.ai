from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import httpx

from app.models.phone import PhoneListResponse, PhoneDetails
from app.db.queries import get_all_phones, count_phones, get_phone_by_slug, search_phones, insert_phone

router = APIRouter()

MOBILE_API_KEY = "afc3242e2a6dbc33d270e23d5a6bbc8a9daa2c33"
MOBILE_API_URL = "https://api.mobileapi.dev/devices/search/"

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
    # 1. Search our local Fone Master Dataset first
    local_results = await search_phones(q)
    
    if local_results:
        return local_results
        
    # 2. Fallback to MobileAPI if not found locally
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                MOBILE_API_URL, 
                params={"name": q, "key": MOBILE_API_KEY}
            )
            response.raise_for_status()
            data = response.json()
            
            api_devices = data.get("devices", [])
            new_phones = []
            
            # 3. Cache the new results into our local DB for future use
            for device in api_devices:
                # Transform API data to our DB schema
                phone_data = {
                    "brand": device.get("manufacturer_name", "Unknown"),
                    "name": device.get("name", "Unknown"),
                    "price": None, # Price isn't usually in the search endpoint directly
                    "os": device.get("os", ""),
                    "description": device.get("description", ""),
                    "hardware": device.get("hardware", "")
                }
                
                # We can save it all under raw_specs
                phone_data.update(device)
                
                saved_phone = await insert_phone(phone_data)
                new_phones.append(saved_phone)
                
            return new_phones

        except Exception as e:
            print(f"Error fetching from MobileAPI: {e}")
            return []

@router.get("/{name}", response_model=PhoneDetails)
async def get_phone(name: str):
    phone = await get_phone_by_slug(name)
    if not phone:
        raise HTTPException(status_code=404, detail="Phone not found")
    return phone
