from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ScrapedPhoneModel(BaseModel):
    brand: str
    parent_ecosystem: str
    model_name: str
    full_name: str
    series: Optional[str] = ""
    price_inr: Optional[float] = None
    price_raw: Optional[str] = ""
    launch_status: str = "available"  # 'available', 'announced_in_india', 'active_limited', 'discontinued'
    sale_start_date: Optional[str] = None  # e.g., '2026-08-21'
    market: str = "India"
    official_india_presence: bool = True
    brand_status: str = "ACTIVE"  # 'ACTIVE', 'ACTIVE_LIMITED'
    catalogue_url: str = ""
    product_url: Optional[str] = ""
    specs_summary: Optional[str] = ""
    scraped_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class BrandMetadata(BaseModel):
    brand: str
    parent_company: str
    parent_ecosystem: str = ""
    market: str = "India"
    official_india_presence: bool = True
    brand_status: str = "ACTIVE"
    smartphone_catalogue_url: str
    catalogue_source: str = "official"
    last_verified: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    verification_status: str = "verified"
    total_active_models: int = 0

