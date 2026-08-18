import abc
import re
import time
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
import primp
from .models import ScrapedPhoneModel, BrandMetadata

class BrandCatalogueScraper(abc.ABC):
    brand_name: str
    parent_company: str
    parent_ecosystem: str
    brand_status: str = "ACTIVE"
    catalogue_url: str

    def __init__(self, timeout: int = 20, retries: int = 3):
        self.timeout = timeout
        self.retries = retries
        self.client = primp.Client(impersonate="chrome_130", verify=False)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
        }

    def fetch_page(self, url: Optional[str] = None, headers: Optional[Dict[str, str]] = None) -> str:
        target_url = url or self.catalogue_url
        req_headers = {**self.headers, **(headers or {})}
        
        last_error = None
        for attempt in range(self.retries):
            try:
                response = self.client.get(target_url, headers=req_headers, timeout=self.timeout)
                if response.status_code == 200:
                    return response.text
                elif response.status_code in (403, 429):
                    time.sleep(1.5 * (attempt + 1))
                else:
                    last_error = f"Status code {response.status_code}"
            except Exception as e:
                last_error = str(e)
                time.sleep(1.0 * (attempt + 1))
        
        print(f"[{self.brand_name}] Warning: Failed to fetch {target_url} after {self.retries} attempts: {last_error}")
        return ""

    @abc.abstractmethod
    def scrape(self) -> List[ScrapedPhoneModel]:
        """Scrapes and returns a list of official phone models."""
        pass

    def get_brand_metadata(self, total_models: int) -> BrandMetadata:
        return BrandMetadata(
            brand=self.brand_name,
            parent_company=self.parent_company,
            market="India",
            official_india_presence=True,
            brand_status=self.brand_status,
            smartphone_catalogue_url=self.catalogue_url,
            catalogue_source="official",
            verification_status="verified",
            total_active_models=total_models
        )

    def clean_name(self, text: str) -> str:
        if not text:
            return ""
        # Remove extra whitespace and newlines
        clean = re.sub(r'[\r\n\t]+', ' ', text).strip()
        clean = re.sub(r'\s{2,}', ' ', clean)
        # Remove marketing buzzwords
        clean = re.sub(r'\s*\b(NEW|New|new|BUY NOW|Buy now|Buy Now|Learn More|Explore|Pre-order|Coming Soon)\b\s*', '', clean, flags=re.IGNORECASE).strip()
        # Remove price attachments in title like "from ₹49,999"
        clean = re.sub(r'\s*(?:from\s*)?₹\s*[\d,]+.*$', '', clean, flags=re.IGNORECASE).strip()
        return clean

    def parse_price(self, price_str: Optional[str]) -> Optional[float]:
        if not price_str:
            return None
        nums = re.findall(r'[\d,]+', str(price_str))
        if nums:
            raw_num = nums[0].replace(',', '')
            try:
                val = float(raw_num)
                return val if val > 1000 else None
            except:
                return None
        return None
