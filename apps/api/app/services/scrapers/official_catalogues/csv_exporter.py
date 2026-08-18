import os
import csv
from typing import List, Dict
from .models import ScrapedPhoneModel

CSV_COLUMNS = [
    "brand",
    "parent_ecosystem",
    "model_name",
    "full_name",
    "series",
    "price_inr",
    "price_raw",
    "launch_status",
    "sale_start_date",
    "market",
    "official_india_presence",
    "brand_status",
    "catalogue_url",
    "product_url",
    "specs_summary",
    "scraped_at",
]

def export_catalogues_to_csv(
    phones: List[ScrapedPhoneModel],
    output_dir: str
) -> Dict[str, str]:
    """
    Exports scraped phones to grouped ecosystem CSV files and a combined master CSV.
    Adds a clean blank separator line between different brands for visual readability.
    Returns a dict mapping group names to absolute file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Group phones by ecosystem
    groups: Dict[str, List[ScrapedPhoneModel]] = {
        "Xiaomi_Corporation_Phones.csv": [],
        "BBK_Ecosystem_Phones.csv": [],
        "Nothing_Ecosystem_Phones.csv": [],
        "HMD_Global_Phones.csv": [],
        "Mainstream_and_Flagship_Phones.csv": [],
        "Combined_Official_India_Smartphones_Catalogue.csv": list(phones),
    }

    for phone in phones:
        eco = phone.parent_ecosystem
        brand_lower = phone.brand.lower()

        if brand_lower in ("xiaomi", "redmi", "poco") or eco == "Xiaomi Corporation":
            groups["Xiaomi_Corporation_Phones.csv"].append(phone)
        elif brand_lower in ("vivo", "iqoo", "oppo", "oneplus", "realme") or eco == "BBK Ecosystem":
            groups["BBK_Ecosystem_Phones.csv"].append(phone)
        elif brand_lower in ("nothing", "cmf") or eco == "Nothing Ecosystem":
            groups["Nothing_Ecosystem_Phones.csv"].append(phone)
        elif brand_lower in ("hmd",) or eco == "HMD Global":
            groups["HMD_Global_Phones.csv"].append(phone)
        else:
            groups["Mainstream_and_Flagship_Phones.csv"].append(phone)

    exported_files = {}
    for filename, phone_list in groups.items():
        file_path = os.path.join(output_dir, filename)
        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            
            last_brand = None
            for p in phone_list:
                current_brand = p.brand.strip().lower()
                # Insert blank separator line when switching to a new brand
                if last_brand is not None and current_brand != last_brand:
                    # Write blank row for clear visual brand separation
                    writer.writerow({col: "" for col in CSV_COLUMNS})
                writer.writerow(p.model_dump())
                last_brand = current_brand
                
        exported_files[filename] = file_path

    return exported_files
