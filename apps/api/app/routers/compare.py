from fastapi import APIRouter, Query, HTTPException
from typing import List
import re
from app.models.response import CompareResponse
from app.db.queries import get_phones_by_ids

router = APIRouter()

def parse_price(price_str):
    if not price_str:
        return 0.0
    numbers = re.findall(r'\d+', str(price_str).replace(',', ''))
    if numbers:
        return float(numbers[0])
    return 0.0

@router.get("", response_model=CompareResponse)
async def compare_phones(ids: str = Query(..., description="Comma separated phone IDs")):
    try:
        id_list = [int(i.strip()) for i in ids.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid IDs provided")
        
    phones = await get_phones_by_ids(id_list)
    
    # Calculate some basic differences
    differences = {}
    if len(phones) > 1:
        p1 = parse_price(phones[0].price)
        p2 = parse_price(phones[1].price)
        differences["price_diff"] = abs(p1 - p2)
        differences["os_diff"] = phones[0].os != phones[1].os
        
    return CompareResponse(
        phones=phones,
        differences=differences
    )
