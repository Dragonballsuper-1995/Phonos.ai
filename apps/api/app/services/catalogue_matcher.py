import re
import sqlite3
from typing import List, Dict, Any, Tuple, Optional
from rapidfuzz import fuzz, process
from .scrapers.official_catalogues.models import ScrapedPhoneModel

def normalize_phone_name(name: str, brand: str = "") -> str:
    """Normalizes phone names for robust fuzzy & exact cross-comparison."""
    if not name:
        return ""
    
    clean = name.strip()
    
    # 1. Strip brand prefix if present
    if brand:
        _escaped = re.escape(brand.strip())
        clean = re.sub(rf"^{_escaped}\s*", "", clean, flags=re.IGNORECASE).strip()
    
    # 2. Strip RAM/ROM brackets
    clean = re.sub(r"\s*\(\d+GB\s+RAM\s*\+\s*\d+GB\)", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s*\(\d+GB\s*\+\s*\d+GB\)", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s*\(\d+GB\s+RAM\)", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s*\(\d+GB\)", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s*\(\d+TB\)", "", clean, flags=re.IGNORECASE)
    
    # 3. Strip standard suffixes & convert plus
    clean = re.sub(r"\b5G\b", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\b4G\b", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\bLTE\b", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\bEdition\b", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\bPro\s*\+", "Pro Plus", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\+", " Plus", clean)
    
    # 4. Remove excessive punctuation / whitespace
    clean = re.sub(r"[^\w\s\(\)]", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip().lower()
    return clean


class MatchResult:
    def __init__(
        self,
        scraped: ScrapedPhoneModel,
        db_id: Optional[int] = None,
        db_name: Optional[str] = None,
        match_type: str = "UNMATCHED",  # EXACT, HIGH_FUZZY, UNMATCHED
        similarity_score: float = 0.0
    ):
        self.scraped = scraped
        self.db_id = db_id
        self.db_name = db_name
        self.match_type = match_type
        self.similarity_score = similarity_score

class CatalogueMatcher:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def load_db_phones_for_brand(self, brand: str) -> List[Dict[str, Any]]:
        """Loads all database records for a particular brand with sibling disambiguation."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        brand_lower = brand.lower()
        if brand_lower == "redmi":
            c.execute(
                """
                SELECT rowid as id, brand, name, price, price_numeric, released_in_india, launch_year 
                FROM phones 
                WHERE (brand COLLATE NOCASE = 'Redmi') 
                   OR (brand COLLATE NOCASE = 'Xiaomi' AND name LIKE '%Redmi%')
                """
            )
        elif brand_lower == "xiaomi":
            c.execute(
                """
                SELECT rowid as id, brand, name, price, price_numeric, released_in_india, launch_year 
                FROM phones 
                WHERE brand COLLATE NOCASE = 'Xiaomi' 
                  AND name NOT LIKE '%Redmi%' 
                  AND name NOT LIKE '%Poco%'
                """
            )
        elif brand_lower == "poco":
            c.execute(
                """
                SELECT rowid as id, brand, name, price, price_numeric, released_in_india, launch_year 
                FROM phones 
                WHERE (brand COLLATE NOCASE IN ('Poco', 'POCO')) 
                   OR (brand COLLATE NOCASE = 'Xiaomi' AND name LIKE '%Poco%')
                """
            )
        elif brand_lower == "cmf":
            c.execute(
                """
                SELECT rowid as id, brand, name, price, price_numeric, released_in_india, launch_year 
                FROM phones 
                WHERE (brand COLLATE NOCASE = 'CMF') 
                   OR (brand COLLATE NOCASE = 'Nothing' AND name LIKE '%CMF%')
                """
            )
        elif brand_lower == "nothing":
            c.execute(
                """
                SELECT rowid as id, brand, name, price, price_numeric, released_in_india, launch_year 
                FROM phones 
                WHERE brand COLLATE NOCASE = 'Nothing' 
                  AND name NOT LIKE '%CMF%'
                """
            )
        elif brand_lower == "iqoo":
            c.execute(
                """
                SELECT rowid as id, brand, name, price, price_numeric, released_in_india, launch_year 
                FROM phones 
                WHERE (brand COLLATE NOCASE = 'iQOO') 
                   OR (brand COLLATE NOCASE = 'Vivo' AND name LIKE '%iQOO%')
                """
            )
        elif brand_lower == "vivo":
            c.execute(
                """
                SELECT rowid as id, brand, name, price, price_numeric, released_in_india, launch_year 
                FROM phones 
                WHERE brand COLLATE NOCASE = 'Vivo' 
                  AND name NOT LIKE '%iQOO%'
                """
            )
        else:
            c.execute(
                "SELECT rowid as id, brand, name, price, price_numeric, released_in_india, launch_year FROM phones WHERE brand COLLATE NOCASE = ?",
                (brand,)
            )
            
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows


    def match_brand_models(
        self,
        brand: str,
        scraped_models: List[ScrapedPhoneModel]
    ) -> Tuple[List[MatchResult], List[ScrapedPhoneModel], List[Dict[str, Any]]]:
        """
        Matches scraped models for a specific brand against database phones.
        Returns:
            - matches: List of MatchResult for matched items
            - unmatched_new: Scraped models with no DB counterpart
            - unmatched_db: DB phones with no scraped catalogue counterpart
        """
        db_phones = self.load_db_phones_for_brand(brand)
        if not db_phones:
            # All scraped items are new to DB
            return [], scraped_models, []

        db_lookup: Dict[str, Dict[str, Any]] = {}
        db_normalized_names = []
        for p in db_phones:
            norm_name = normalize_phone_name(p["name"], brand)
            db_lookup[norm_name] = p
            db_normalized_names.append(norm_name)

        matched_results: List[MatchResult] = []
        unmatched_new: List[ScrapedPhoneModel] = []
        matched_db_ids: Set[int] = set()

        for scraped in scraped_models:
            norm_scraped = normalize_phone_name(scraped.model_name, brand)

            # 1. Exact Normalized Match
            if norm_scraped in db_lookup:
                matched_db = db_lookup[norm_scraped]
                matched_results.append(
                    MatchResult(
                        scraped=scraped,
                        db_id=matched_db["id"],
                        db_name=matched_db["name"],
                        match_type="EXACT",
                        similarity_score=100.0
                    )
                )
                matched_db_ids.add(matched_db["id"])
                continue

            # 2. Fuzzy Match via RapidFuzz
            best_match = process.extractOne(
                norm_scraped,
                db_normalized_names,
                scorer=fuzz.token_sort_ratio
            )

            if best_match and best_match[1] >= 88.0:
                matched_db = db_lookup[best_match[0]]
                matched_results.append(
                    MatchResult(
                        scraped=scraped,
                        db_id=matched_db["id"],
                        db_name=matched_db["name"],
                        match_type="HIGH_FUZZY",
                        similarity_score=float(best_match[1])
                    )
                )
                matched_db_ids.add(matched_db["id"])
            else:
                unmatched_new.append(scraped)

        unmatched_db = [p for p in db_phones if p["id"] not in matched_db_ids]
        return matched_results, unmatched_new, unmatched_db
