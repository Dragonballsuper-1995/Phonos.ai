from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict, Any

class PhoneSpecs(BaseModel):
    display: str = ""
    displaySize: str = ""
    refreshRate: str = ""
    processor: str = ""
    ram: str = ""
    storage: str = ""
    expandableStorage: bool = False
    mainCamera: str = ""
    selfieCamera: str = ""
    battery: str = ""
    charging: str = ""
    os: str = ""
    connectivity5G: bool = False
    weight: str = ""
    dimensions: str = ""
    waterResistance: str = ""
    nfc: bool = False
    biometrics: str = ""

class PhoneDetails(BaseModel):
    id: Optional[int] = None
    slug: str = ""
    brand: str
    model: str = ""
    fullName: str = ""
    price: float = 0.0
    imageUrl: Optional[str] = None
    specs: PhoneSpecs = Field(default_factory=PhoneSpecs)
    releaseDate: Optional[str] = None
    priceTier: str = "mid-range"
    highlights: List[str] = []
    
    # Internal fields we use but frontend doesn't need directly
    name: str = ""
    os: Optional[str] = Field(exclude=True, default="")
    raw_specs: Optional[Dict[str, Any]] = Field(exclude=True, default=None)

    @model_validator(mode='before')
    @classmethod
    def map_to_frontend(cls, data: Any):
        if isinstance(data, dict):
            # Parse price
            price_val = 0.0
            if data.get("price"):
                import re
                nums = re.findall(r'\d+', str(data["price"]).replace(',', ''))
                if nums:
                    price_val = float(nums[0])
                    
            raw = data.get("raw_specs", {})
            if isinstance(raw, str):
                import json
                try:
                    raw = json.loads(raw)
                except:
                    raw = {}
                    
            raw_str = str(raw).lower()
            
            os_str = data.get("os")
            if os_str is None:
                os_str = "Unknown"
            
            # Map specs heuristically
            specs = PhoneSpecs(
                os=os_str,
                battery="5000 mAh" if "5000" in raw_str else "Unknown",
                mainCamera="108 MP" if "108 mp" in raw_str else ("50 MP" if "50 mp" in raw_str else "Unknown"),
                connectivity5G=True if "5g" in raw_str else False
            )
            
            name = data.get("name") or "Unknown"
            brand = data.get("brand") or "Unknown"
            
            # Populate required frontend fields
            data["fullName"] = name
            data["slug"] = name.replace(" ", "-").lower()
            data["model"] = name.replace(brand, "").strip()
            data["price"] = price_val
            data["specs"] = specs
            data["priceTier"] = "premium" if price_val > 50000 else ("mid-range" if price_val > 15000 else "budget")
            data["os"] = os_str
            data["brand"] = brand
            
        return data

    class Config:
        from_attributes = True

class PhoneListResponse(BaseModel):
    phones: List[PhoneDetails]
    total: int
