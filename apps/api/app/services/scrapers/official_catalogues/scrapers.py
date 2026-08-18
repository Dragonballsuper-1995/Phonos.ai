import re
import json
from typing import List, Dict, Set, Optional
from bs4 import BeautifulSoup
from .base import BrandCatalogueScraper
from .models import ScrapedPhoneModel

# ---------------------------------------------------------
# 1. SAMSUNG
# ---------------------------------------------------------
class SamsungScraper(BrandCatalogueScraper):
    brand_name = "Samsung"
    parent_company = "Samsung Electronics"
    parent_ecosystem = "Mainstream & Flagship"
    catalogue_url = "https://www.samsung.com/in/smartphones/all-smartphones/"

    def scrape(self) -> List[ScrapedPhoneModel]:
        # Exact official active selling models on Samsung India store
        official_catalog = [
            # S Series
            ("Galaxy S26 Ultra", 124999.0, "Galaxy S Series"),
            ("Galaxy S26+", 114999.0, "Galaxy S Series"),
            ("Galaxy S26", 99999.0, "Galaxy S Series"),
            ("Galaxy S25 Ultra", 90620.0, "Galaxy S Series"),
            ("Galaxy S25", 64000.0, "Galaxy S Series"),
            ("Galaxy S25 FE", 45739.0, "Galaxy S Series"),
            ("Galaxy S24 Ultra", 119999.0, "Galaxy S Series"),
            ("Galaxy S24", 49999.0, "Galaxy S Series"),
            ("Galaxy S25 Edge", 64999.0, "Galaxy S Series"),
            ("Galaxy S24 FE", 39999.0, "Galaxy S Series"),
            # Z Series
            ("Galaxy Z Fold8 Ultra", 199999.0, "Galaxy Z Series"),
            ("Galaxy Z Fold8", 179999.0, "Galaxy Z Series"),
            ("Galaxy Z Flip8", 124999.0, "Galaxy Z Series"),
            ("Galaxy Z Fold7", 174999.0, "Galaxy Z Series"),
            ("Galaxy Z Flip7", 121999.0, "Galaxy Z Series"),
            ("Galaxy Z Flip7 FE", 89999.0, "Galaxy Z Series"),
            ("Galaxy Z Fold6", 149999.0, "Galaxy Z Series"),
            ("Galaxy Z Flip6", 75999.0, "Galaxy Z Series"),
            # A Series
            ("Galaxy A57 5G", 49499.0, "Galaxy A Series"),
            ("Galaxy A56 5G", 52499.0, "Galaxy A Series"),
            ("Galaxy A37 5G", 36999.0, "Galaxy A Series"),
            ("Galaxy A36 5G", 37999.0, "Galaxy A Series"),
            ("Galaxy A27 5G", 31999.0, "Galaxy A Series"),
            ("Galaxy A35 5G", 29990.0, "Galaxy A Series"),
            ("Galaxy A55 5G", 29998.0, "Galaxy A Series"),
            ("Galaxy A26 5G", None, "Galaxy A Series"),
            ("Galaxy A17 5G", 21499.0, "Galaxy A Series"),
            ("Galaxy A16 5G", None, "Galaxy A Series"),
            ("Galaxy A15 5G", None, "Galaxy A Series"),
            ("Galaxy A07 5G", 18499.0, "Galaxy A Series"),
            ("Galaxy A07", 13499.0, "Galaxy A Series"),
            ("Galaxy A06 5G", 15499.0, "Galaxy A Series"),
            ("Galaxy A06", None, "Galaxy A Series"),
            # M Series
            ("Galaxy M47 5G", 36999.0, "Galaxy M Series"),
            ("Galaxy M17 5G", 21999.0, "Galaxy M Series"),
            ("Galaxy M17e 5G", 12499.0, "Galaxy M Series"),
            ("Galaxy M36 5G", None, "Galaxy M Series"),
            ("Galaxy M56 5G", None, "Galaxy M Series"),
            ("Galaxy M35 5G", None, "Galaxy M Series"),
            ("Galaxy M55 5G", None, "Galaxy M Series"),
            ("Galaxy M55s 5G", None, "Galaxy M Series"),
            ("Galaxy M16 5G", None, "Galaxy M Series"),
            ("Galaxy M15 5G Prime", None, "Galaxy M Series"),
            ("Galaxy M06 5G", 12499.0, "Galaxy M Series"),
            ("Galaxy M07", 11399.0, "Galaxy M Series"),
            ("Galaxy M05", None, "Galaxy M Series"),
            # F Series
            ("Galaxy F70 Pro 5G", 36999.0, "Galaxy F Series"),
            ("Galaxy F70e 5G", 16499.0, "Galaxy F Series"),
            ("Galaxy F56 5G", 27999.0, "Galaxy F Series"),
            ("Galaxy F55 5G", None, "Galaxy F Series"),
            ("Galaxy F36 5G", 21999.0, "Galaxy F Series"),
            ("Galaxy F17 5G", 18999.0, "Galaxy F Series"),
            ("Galaxy F16 5G", None, "Galaxy F Series"),
            ("Galaxy F15 5G", None, "Galaxy F Series"),
            ("Galaxy F13", None, "Galaxy F Series"),
            ("Galaxy F07", 11399.0, "Galaxy F Series"),
            ("Galaxy F06 5G", 13999.0, "Galaxy F Series"),
            ("Galaxy F05", None, "Galaxy F Series"),
        ]

        models: List[ScrapedPhoneModel] = []
        for name, price, ser in official_catalog:
            price_raw = f"₹{int(price):,}" if price else ""
            models.append(
                ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=f"Samsung {name}",
                    series=ser,
                    price_inr=price,
                    price_raw=price_raw,
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )
            )

        return models


# ---------------------------------------------------------
# 2. APPLE
# ---------------------------------------------------------
class AppleScraper(BrandCatalogueScraper):
    brand_name = "Apple"
    parent_company = "Apple Inc."
    parent_ecosystem = "Mainstream & Flagship"
    catalogue_url = "https://www.apple.com/in/shop/buy-iphone"

    def scrape(self) -> List[ScrapedPhoneModel]:
        # Official active selling iPhone lineup on Apple India store
        active_lineup = [
            ("iPhone 17 Pro", 134900.0),
            ("iPhone 17 Pro Max", 149900.0),
            ("iPhone Air", 119900.0),
            ("iPhone 17", 82900.0),
            ("iPhone 17e", 64900.0),
            ("iPhone 16", 69900.0),
            ("iPhone 16 Plus", 79900.0),
        ]

        models: List[ScrapedPhoneModel] = []
        for name, price in active_lineup:
            models.append(
                ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=f"Apple {name}",
                    series="iPhone",
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )
            )

        return models


# ---------------------------------------------------------
# 3. XIAOMI
# ---------------------------------------------------------
class XiaomiScraper(BrandCatalogueScraper):
    brand_name = "Xiaomi"
    parent_company = "Xiaomi Corporation"
    parent_ecosystem = "Xiaomi Corporation"
    catalogue_url = "https://www.mi.com/in/product-list/xiaomi/"

    def scrape(self) -> List[ScrapedPhoneModel]:
        html = self.fetch_page()
        models: Dict[str, ScrapedPhoneModel] = {}

        if html and "window.__PRELOADED_STATE__" in html:
            try:
                idx = html.find("window.__PRELOADED_STATE__")
                end_idx = html.find("</script>", idx)
                json_str = html[idx + len("window.__PRELOADED_STATE__ = "):end_idx].strip().rstrip(";")
                data = json.loads(json_str)
                dp_data = data.get("pagedata", {}).get("product_list", {}).get("dataProvider", {}).get("data", [])
                for item in dp_data:
                    p = item.get("product", {})
                    name = p.get("name")
                    if name and not any(bad in name.lower() for bad in ["pad", "tablet", "tv", "buds", "watch", "speaker", "vacuum"]):
                        clean_name = self.clean_name(name)
                        models[clean_name] = ScrapedPhoneModel(
                            brand=self.brand_name,
                            parent_ecosystem=self.parent_ecosystem,
                            model_name=clean_name,
                            full_name=f"Xiaomi {clean_name}" if not clean_name.startswith("Xiaomi") else clean_name,
                            series="Xiaomi Flagship",
                            price_inr=self.parse_price(p.get("price")),
                            price_raw=f"₹{p.get('price')}" if p.get("price") else "",
                            launch_status="available",
                            catalogue_url=self.catalogue_url,
                            brand_status=self.brand_status,
                        )
            except Exception as e:
                print(f"[XiaomiScraper] Error parsing preloaded state: {e}")

        # Baseline official Xiaomi catalog in India
        catalog = [
            ("Xiaomi 17 Ultra", 119999.0),
            ("Xiaomi 17 Pro", 89999.0),
            ("Xiaomi 17", 74999.0),
            ("Xiaomi 17T", 54999.0),
            ("Xiaomi 14 Ultra", 99999.0),
            ("Xiaomi 14", 69999.0),
            ("Xiaomi 14 Civi", 39999.0),
            ("Xiaomi 13 Pro", 74999.0),
        ]
        for name, price in catalog:
            clean = name.replace("Xiaomi ", "").strip()
            if name not in models and clean not in models:
                models[name] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=f"Xiaomi {name}" if not name.startswith("Xiaomi") else name,
                    series="Xiaomi Flagship",
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )

        return list(models.values())


# ---------------------------------------------------------
# 4. REDMI
# ---------------------------------------------------------
class RedmiScraper(BrandCatalogueScraper):
    brand_name = "Redmi"
    parent_company = "Xiaomi Corporation"
    parent_ecosystem = "Xiaomi Corporation"
    catalogue_url = "https://www.mi.com/in/product-list/redmi/"

    def scrape(self) -> List[ScrapedPhoneModel]:
        html = self.fetch_page()
        models: Dict[str, ScrapedPhoneModel] = {}

        if html and "window.__PRELOADED_STATE__" in html:
            try:
                idx = html.find("window.__PRELOADED_STATE__")
                end_idx = html.find("</script>", idx)
                json_str = html[idx + len("window.__PRELOADED_STATE__ = "):end_idx].strip().rstrip(";")
                data = json.loads(json_str)
                dp_data = data.get("pagedata", {}).get("product_list", {}).get("dataProvider", {}).get("data", [])
                for item in dp_data:
                    p = item.get("product", {})
                    name = p.get("name")
                    if name and not any(bad in name.lower() for bad in ["pad", "tablet", "tv", "buds", "watch", "power bank"]):
                        clean_name = self.clean_name(name)
                        series = "Redmi Note Series" if "note" in clean_name.lower() else ("Redmi A Series" if " a" in clean_name.lower() else "Redmi Number Series")
                        models[clean_name] = ScrapedPhoneModel(
                            brand=self.brand_name,
                            parent_ecosystem=self.parent_ecosystem,
                            model_name=clean_name,
                            full_name=f"Redmi {clean_name}" if not clean_name.startswith("Redmi") else clean_name,
                            series=series,
                            price_inr=self.parse_price(p.get("price")),
                            price_raw=f"₹{p.get('price')}" if p.get("price") else "",
                            launch_status="available",
                            catalogue_url=self.catalogue_url,
                            brand_status=self.brand_status,
                        )
            except Exception as e:
                print(f"[RedmiScraper] Error parsing preloaded state: {e}")

        # Baseline official active Redmi catalogue
        catalog = [
            ("Redmi Note 15 Pro+ 5G", 31999.0, "Redmi Note Series"),
            ("Redmi Note 15 Pro 5G", 26999.0, "Redmi Note Series"),
            ("Redmi Note 15 5G", 18999.0, "Redmi Note Series"),
            ("Redmi Note 14 Pro+ 5G", 29999.0, "Redmi Note Series"),
            ("Redmi Note 14 Pro 5G", 23999.0, "Redmi Note Series"),
            ("Redmi Note 14 5G", 17999.0, "Redmi Note Series"),
            ("Redmi Note 14 SE 5G", 14999.0, "Redmi Note Series"),
            ("Redmi 15 5G", 13999.0, "Redmi Number Series"),
            ("Redmi 15C 5G", 11999.0, "Redmi Number Series"),
            ("Redmi 14C 5G", 10999.0, "Redmi Number Series"),
            ("Redmi 13 5G", 12999.0, "Redmi Number Series"),
            ("Redmi 13C 5G", 9999.0, "Redmi Number Series"),
            ("Redmi A5", 6999.0, "Redmi A Series"),
            ("Redmi A4 5G", 8499.0, "Redmi A Series"),
            ("Redmi A3", 6499.0, "Redmi A Series"),
            ("REDMI Turbo 5", 27999.0, "Redmi Turbo Series"),
        ]
        for name, price, ser in catalog:
            if name not in models:
                models[name] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=f"Redmi {name}" if not name.startswith("Redmi") else name,
                    series=ser,
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )

        return list(models.values())


# ---------------------------------------------------------
# 5. POCO
# ---------------------------------------------------------
class POCOScraper(BrandCatalogueScraper):
    brand_name = "POCO"
    parent_company = "Xiaomi Corporation"
    parent_ecosystem = "Xiaomi Corporation"
    catalogue_url = "https://www.poco.in/product-details/"

    def scrape(self) -> List[ScrapedPhoneModel]:
        # Models explicitly defined by user & India catalogue
        poco_model_definitions = [
            ("X8 Pro Max", "POCO X Series", 32999.0),
            ("X8 Pro", "POCO X Series", 27999.0),
            ("X7 Pro", "POCO X Series", 25999.0),
            ("X7", "POCO X Series", 21999.0),
            ("F7", "POCO F Series", 34999.0),
            ("F6", "POCO F Series", 29999.0),
            ("M8 Power", "POCO M Series", 17999.0),
            ("M8 5G", "POCO M Series", 13999.0),
            ("M7 Plus", "POCO M Series", 14999.0),
            ("M7 Pro", "POCO M Series", 13499.0),
            ("M7 5G", "POCO M Series", 10999.0),
            ("M6 Pro 5G", "POCO M Series", 9999.0),
            ("C85x", "POCO C Series", 8999.0),
            ("C85", "POCO C Series", 7999.0),
            ("C81x", "POCO C Series", 7499.0),
            ("C81", "POCO C Series", 6999.0),
            ("C75", "POCO C Series", 7999.0),
            ("C71", "POCO C Series", 6499.0),
            ("C61", "POCO C Series", 5999.0),
        ]

        models = []
        for model_slug, series, price in poco_model_definitions:
            url_slug = model_slug.replace(" ", "")
            prod_url = f"https://www.poco.in/product-details/{url_slug}"
            models.append(
                ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=f"POCO {model_slug}",
                    full_name=f"POCO {model_slug}",
                    series=series,
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    product_url=prod_url,
                    brand_status=self.brand_status,
                )
            )

        return models


# ---------------------------------------------------------
# 6. VIVO
# ---------------------------------------------------------
class VivoScraper(BrandCatalogueScraper):
    brand_name = "vivo"
    parent_company = "BBK Electronics"
    parent_ecosystem = "BBK Ecosystem"
    catalogue_url = "https://www.vivo.com/in/products?choose=all"

    def scrape(self) -> List[ScrapedPhoneModel]:
        html = self.fetch_page()
        models: Dict[str, ScrapedPhoneModel] = {}

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["h2", "h3", "h4", "p", "span", "a", "div"]):
                t = tag.get_text(strip=True)
                if any(t.startswith(prefix) for prefix in ["X", "V", "Y", "T", "vivo X", "vivo V", "vivo Y", "vivo T"]) and len(t) < 35:
                    clean = self.clean_name(t)
                    if any(clean.startswith(p) for p in ["X", "V", "Y", "T", "vivo X", "vivo V", "vivo Y", "vivo T"]):
                        if not any(bad in clean.lower() for bad in ["policy", "store", "newsroom", "about", "terms", "service", "care"]):
                            full_name = clean if clean.lower().startswith("vivo") else f"vivo {clean}"
                            model_name = re.sub(r"^vivo\s*", "", full_name, flags=re.IGNORECASE).strip()
                            models[model_name] = ScrapedPhoneModel(
                                brand=self.brand_name,
                                parent_ecosystem=self.parent_ecosystem,
                                model_name=model_name,
                                full_name=full_name,
                                series="vivo X Series" if model_name.startswith("X") else ("vivo V Series" if model_name.startswith("V") else ("vivo T Series" if model_name.startswith("T") else "vivo Y Series")),
                                launch_status="available",
                                catalogue_url=self.catalogue_url,
                                brand_status=self.brand_status,
                            )

        # Baseline official vivo catalog in India
        catalog = [
            ("X300 Pro", 99999.0, "vivo X Series"),
            ("X300", 79999.0, "vivo X Series"),
            ("X200 Pro 5G", 94999.0, "vivo X Series"),
            ("X200 5G", 64999.0, "vivo X Series"),
            ("X Fold 5", 159999.0, "vivo X Series"),
            ("X Fold 3 Pro", 149999.0, "vivo X Series"),
            ("V70 Elite", 46999.0, "vivo V Series"),
            ("V70", 39999.0, "vivo V Series"),
            ("V50 Pro 5G", 42999.0, "vivo V Series"),
            ("V50 5G", 34999.0, "vivo V Series"),
            ("V40 Pro 5G", 49999.0, "vivo V Series"),
            ("V40 5G", 34999.0, "vivo V Series"),
            ("V40e 5G", 28999.0, "vivo V Series"),
            ("T5 Lite 5G", 14999.0, "vivo T Series"),
            ("T5e", 13999.0, "vivo T Series"),
            ("T5x", 12999.0, "vivo T Series"),
            ("T3 Pro 5G", 24999.0, "vivo T Series"),
            ("T3 Ultra 5G", 31999.0, "vivo T Series"),
            ("T3 5G", 19999.0, "vivo T Series"),
            ("T3x 5G", 13499.0, "vivo T Series"),
            ("Y300 5G", 21999.0, "vivo Y Series"),
            ("Y200 Pro 5G", 24999.0, "vivo Y Series"),
            ("Y58 5G", 19499.0, "vivo Y Series"),
            ("Y28 5G", 13999.0, "vivo Y Series"),
        ]
        for name, price, ser in catalog:
            clean = name.replace("vivo ", "").strip()
            if clean not in models:
                models[clean] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=clean,
                    full_name=f"vivo {clean}",
                    series=ser,
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )

        return list(models.values())


# ---------------------------------------------------------
# 7. IQOO
# ---------------------------------------------------------
class IQOOScraper(BrandCatalogueScraper):
    brand_name = "iQOO"
    parent_company = "BBK Electronics"
    parent_ecosystem = "BBK Ecosystem"
    catalogue_url = "https://www.iqoo.com/in/products?choose=all"

    def scrape(self) -> List[ScrapedPhoneModel]:
        html = self.fetch_page()
        models: Dict[str, ScrapedPhoneModel] = {}

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["h2", "h3", "h4", "p", "span", "a"]):
                t = tag.get_text(strip=True)
                if "iqoo" in t.lower() and len(t) < 35:
                    clean = self.clean_name(t)
                    if clean.lower().startswith("iqoo") and not any(bad in clean.lower() for bad in ["live", "about", "care", "service", "store"]):
                        series = "iQOO Number Series" if any(k in clean for k in ["15", "13", "12", "11"]) else ("iQOO Neo Series" if "neo" in clean.lower() else "iQOO Z Series")
                        models[clean] = ScrapedPhoneModel(
                            brand=self.brand_name,
                            parent_ecosystem=self.parent_ecosystem,
                            model_name=clean,
                            full_name=clean,
                            series=series,
                            launch_status="available",
                            catalogue_url=self.catalogue_url,
                            brand_status=self.brand_status,
                        )

        # Baseline official iQOO India catalogue
        catalog = [
            ("iQOO 15", 59999.0, "iQOO Number Series"),
            ("iQOO 15R", 44999.0, "iQOO Number Series"),
            ("iQOO 13", 54999.0, "iQOO Number Series"),
            ("iQOO 12 5G", 52999.0, "iQOO Number Series"),
            ("iQOO Neo 10R", 34999.0, "iQOO Neo Series"),
            ("iQOO Neo 9 Pro 5G", 35999.0, "iQOO Neo Series"),
            ("iQOO Neo 7 Pro 5G", 32999.0, "iQOO Neo Series"),
            ("iQOO Z9 Turbo", 26999.0, "iQOO Z Series"),
            ("iQOO Z9s Pro 5G", 24999.0, "iQOO Z Series"),
            ("iQOO Z9s 5G", 19999.0, "iQOO Z Series"),
            ("iQOO Z9 5G", 19999.0, "iQOO Z Series"),
            ("iQOO Z9x 5G", 12999.0, "iQOO Z Series"),
        ]
        for name, price, ser in catalog:
            if name not in models:
                models[name] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=name,
                    series=ser,
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )

        return list(models.values())


# ---------------------------------------------------------
# 8. OPPO
# ---------------------------------------------------------
class OPPOScraper(BrandCatalogueScraper):
    brand_name = "OPPO"
    parent_company = "BBK Electronics"
    parent_ecosystem = "BBK Ecosystem"
    catalogue_url = "https://www.oppo.com/in/smartphones/"

    def scrape(self) -> List[ScrapedPhoneModel]:
        html = self.fetch_page()
        models: Dict[str, ScrapedPhoneModel] = {}

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["h2", "h3", "h4", "a", "div", "p"]):
                t = tag.get_text(strip=True)
                if "oppo" in t.lower() and len(t) < 40:
                    clean = self.clean_name(t)
                    if clean.startswith("OPPO") and not any(bad in clean.lower() for bad in ["store", "india", "care", "service", "terms"]):
                        series = "Find Series" if "find" in clean.lower() else ("Reno Series" if "reno" in clean.lower() else ("F Series" if " f" in clean.lower() else ("K Series" if " k" in clean.lower() else "A Series")))
                        models[clean] = ScrapedPhoneModel(
                            brand=self.brand_name,
                            parent_ecosystem=self.parent_ecosystem,
                            model_name=clean,
                            full_name=clean,
                            series=series,
                            launch_status="available",
                            catalogue_url=self.catalogue_url,
                            brand_status=self.brand_status,
                        )

        # Baseline official OPPO India catalogue
        catalog = [
            ("OPPO Find X9 Ultra", 109999.0, "Find Series"),
            ("OPPO Find X9s", 74999.0, "Find Series"),
            ("OPPO Find X8 Pro", 99999.0, "Find Series"),
            ("OPPO Find X8", 69999.0, "Find Series"),
            ("OPPO Find N3 Flip", 94999.0, "Find Series"),
            ("OPPO Reno16 5G", 38999.0, "Reno Series"),
            ("OPPO Reno16c 5G", 32999.0, "Reno Series"),
            ("OPPO Reno13 Pro 5G", 49999.0, "Reno Series"),
            ("OPPO Reno13 5G", 39999.0, "Reno Series"),
            ("OPPO Reno12 Pro 5G", 36999.0, "Reno Series"),
            ("OPPO Reno12 5G", 32999.0, "Reno Series"),
            ("OPPO F33 Pro 5G", 29999.0, "F Series"),
            ("OPPO F27 Pro+ 5G", 27999.0, "F Series"),
            ("OPPO F27 5G", 22999.0, "F Series"),
            ("OPPO F25 Pro 5G", 23999.0, "F Series"),
            ("OPPO K14 5G", 18999.0, "K Series"),
            ("OPPO K12x 5G", 12999.0, "K Series"),
            ("OPPO A3 Pro 5G", 17999.0, "A Series"),
            ("OPPO A3 5G", 15999.0, "A Series"),
            ("OPPO A3x 5G", 12499.0, "A Series"),
            ("OPPO A79 5G", 17499.0, "A Series"),
        ]
        for name, price, ser in catalog:
            if name not in models:
                models[name] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=name,
                    series=ser,
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )

        return list(models.values())


# ---------------------------------------------------------
# 9. ONEPLUS
# ---------------------------------------------------------
class OnePlusScraper(BrandCatalogueScraper):
    brand_name = "OnePlus"
    parent_company = "BBK Electronics"
    parent_ecosystem = "BBK Ecosystem"
    catalogue_url = "https://www.oneplus.in/store/phone"

    def scrape(self) -> List[ScrapedPhoneModel]:
        html = self.fetch_page()
        models: Dict[str, ScrapedPhoneModel] = {}

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for s in soup.find_all("script"):
                if s.string and "spuList" in s.string:
                    try:
                        data = json.loads(s.string)
                        spus = data.get("spuList", [])
                        for spu in spus:
                            name = self.clean_name(spu.get("productName", ""))
                            if name and not any(bad in name.lower() for bad in ["buds", "watch", "pad", "case", "power"]):
                                series = "OnePlus Flagship" if any(k in name for k in ["15", "13", "12", "11", "10", "Open"]) else "OnePlus Nord Series"
                                price_val = spu.get("price") or spu.get("originalPrice")
                                models[name] = ScrapedPhoneModel(
                                    brand=self.brand_name,
                                    parent_ecosystem=self.parent_ecosystem,
                                    model_name=name,
                                    full_name=name,
                                    series=series,
                                    price_inr=self.parse_price(str(price_val)) if price_val else None,
                                    launch_status="available",
                                    catalogue_url=self.catalogue_url,
                                    product_url=f"https://www.oneplus.in/{spu.get('urlKey')}" if spu.get("urlKey") else "",
                                    brand_status=self.brand_status,
                                )
                    except Exception as e:
                        print(f"[OnePlusScraper] Error parsing spuList: {e}")

        # Baseline official OnePlus catalogue
        catalog = [
            ("OnePlus 15", 69999.0, "OnePlus Flagship"),
            ("OnePlus 15R", 42999.0, "OnePlus Flagship"),
            ("OnePlus 13", 69999.0, "OnePlus Flagship"),
            ("OnePlus 13R", 42999.0, "OnePlus Flagship"),
            ("OnePlus 13s", 49999.0, "OnePlus Flagship"),
            ("OnePlus 12", 64999.0, "OnePlus Flagship"),
            ("OnePlus 12R", 39999.0, "OnePlus Flagship"),
            ("OnePlus Open", 139999.0, "OnePlus Flagship"),
            ("OnePlus Nord 6", 32999.0, "OnePlus Nord Series"),
            ("OnePlus Nord 4", 29999.0, "OnePlus Nord Series"),
            ("OnePlus Nord CE6", 24999.0, "OnePlus Nord Series"),
            ("OnePlus Nord CE6 Lite", 19999.0, "OnePlus Nord Series"),
            ("OnePlus Nord CE4 5G", 24999.0, "OnePlus Nord Series"),
            ("OnePlus Nord CE4 Lite 5G", 19999.0, "OnePlus Nord Series"),
            ("OnePlus Nord 3 5G", 28999.0, "OnePlus Nord Series"),
            ("OnePlus Nord CE 3 Lite 5G", 17499.0, "OnePlus Nord Series"),
        ]
        for name, price, ser in catalog:
            if name not in models:
                models[name] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=name,
                    series=ser,
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )

        return list(models.values())


# ---------------------------------------------------------
# 10. REALME
# ---------------------------------------------------------
class RealmeScraper(BrandCatalogueScraper):
    brand_name = "realme"
    parent_company = "BBK Electronics"
    parent_ecosystem = "BBK Ecosystem"
    catalogue_url = "https://www.realme.com/in/search?keyword=realme"

    def scrape(self) -> List[ScrapedPhoneModel]:
        html = self.fetch_page()
        models: Dict[str, ScrapedPhoneModel] = {}

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["h2", "h3", "h4", "a", "div", "p", "span"]):
                t = tag.get_text(strip=True)
                if ("realme" in t.lower() or "narzo" in t.lower()) and len(t) < 40:
                    clean = self.clean_name(t)
                    if (clean.lower().startswith("realme") or clean.lower().startswith("narzo")) and not any(bad in clean.lower() for bad in ["buds", "watch", "pad", "tv", "earphones", "techlife"]):
                        series = "GT Series" if "gt" in clean.lower() else ("NARZO Series" if "narzo" in clean.lower() else ("P Series" if " p" in clean.lower() else ("C Series" if " c" in clean.lower() else "Number Series")))
                        models[clean] = ScrapedPhoneModel(
                            brand=self.brand_name,
                            parent_ecosystem=self.parent_ecosystem,
                            model_name=clean,
                            full_name=clean,
                            series=series,
                            launch_status="available",
                            catalogue_url=self.catalogue_url,
                            brand_status=self.brand_status,
                        )

        # Baseline official realme catalogue
        catalog = [
            ("realme GT 7 Pro", 59999.0, "GT Series"),
            ("realme GT 6", 40999.0, "GT Series"),
            ("realme GT 6T", 30999.0, "GT Series"),
            ("realme 16 Pro+ 5G", 32999.0, "Number Series"),
            ("realme 16 Pro 5G", 26999.0, "Number Series"),
            ("realme 16 5G", 19999.0, "Number Series"),
            ("realme 16T 5G", 17999.0, "Number Series"),
            ("realme 15 Pro+ 5G", 31999.0, "Number Series"),
            ("realme 15 Pro 5G", 25999.0, "Number Series"),
            ("realme 15 5G", 18999.0, "Number Series"),
            ("realme 15T", 16999.0, "Number Series"),
            ("realme 14 Pro+ 5G", 29999.0, "Number Series"),
            ("realme 14 Pro 5G", 24999.0, "Number Series"),
            ("realme 14x 5G", 14999.0, "Number Series"),
            ("realme 13 Pro+ 5G", 29999.0, "Number Series"),
            ("realme 13 Pro 5G", 24999.0, "Number Series"),
            ("realme 13+ 5G", 22999.0, "Number Series"),
            ("realme 13 5G", 17999.0, "Number Series"),
            ("realme P2 Pro 5G", 21999.0, "P Series"),
            ("realme P1 Pro 5G", 19999.0, "P Series"),
            ("realme P1 Speed 5G", 17999.0, "P Series"),
            ("realme P1 5G", 14999.0, "P Series"),
            ("realme NARZO 70 Turbo 5G", 16999.0, "NARZO Series"),
            ("realme NARZO 70 Pro 5G", 18999.0, "NARZO Series"),
            ("realme NARZO 70 5G", 14999.0, "NARZO Series"),
            ("realme NARZO 70x 5G", 11999.0, "NARZO Series"),
            ("realme NARZO N65 5G", 11499.0, "NARZO Series"),
            ("realme C67 5G", 11999.0, "C Series"),
            ("realme C65 5G", 10499.0, "C Series"),
            ("realme C63 5G", 8999.0, "C Series"),
            ("realme C61", 7699.0, "C Series"),
        ]
        for name, price, ser in catalog:
            if name not in models:
                models[name] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=name,
                    series=ser,
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )

        return list(models.values())


# ---------------------------------------------------------
# 11. MOTOROLA
# ---------------------------------------------------------
class MotorolaScraper(BrandCatalogueScraper):
    brand_name = "Motorola"
    parent_company = "Lenovo"
    parent_ecosystem = "Mainstream & Flagship"
    catalogue_url = "https://www.motorola.in/smartphones"

    def scrape(self) -> List[ScrapedPhoneModel]:
        urls = [
            "https://www.motorola.in/smartphones",
            "https://www.motorola.in/smartphones-razr-family",
            "https://www.motorola.in/motorola-edge-family",
            "https://www.motorola.in/moto-g-family",
        ]
        models: Dict[str, ScrapedPhoneModel] = {}

        for u in urls:
            html = self.fetch_page(u)
            if html:
                soup = BeautifulSoup(html, "html.parser")
                for tag in soup.find_all(["h2", "h3", "h4", "a", "span", "p"]):
                    t = tag.get_text(strip=True)
                    if any(k in t.lower() for k in ["motorola", "moto g", "razr", "edge"]) and len(t) < 40:
                        clean = self.clean_name(t)
                        if any(clean.lower().startswith(p) for p in ["motorola", "moto", "razr", "edge"]):
                            series = "Razr Family" if "razr" in clean.lower() else ("Edge Family" if "edge" in clean.lower() else "Moto G Family")
                            models[clean] = ScrapedPhoneModel(
                                brand=self.brand_name,
                                parent_ecosystem=self.parent_ecosystem,
                                model_name=clean,
                                full_name=clean if clean.lower().startswith("motorola") else f"Motorola {clean}",
                                series=series,
                                launch_status="available",
                                catalogue_url=self.catalogue_url,
                                brand_status=self.brand_status,
                            )

        # Baseline official Motorola India portfolio
        catalog = [
            ("motorola razr 50 ultra", 89999.0, "Razr Family"),
            ("motorola razr 50", 64999.0, "Razr Family"),
            ("motorola razr 40 ultra", 69999.0, "Razr Family"),
            ("motorola edge 50 ultra", 54999.0, "Edge Family"),
            ("motorola edge 50 pro", 31999.0, "Edge Family"),
            ("motorola edge 50", 27999.0, "Edge Family"),
            ("motorola edge 50 fusion", 22999.0, "Edge Family"),
            ("motoedge 70 fusion", 24999.0, "Edge Family"),
            ("motoedge 70", 29999.0, "Edge Family"),
            ("moto g85 5G", 17999.0, "Moto G Family"),
            ("moto g64 5G", 14999.0, "Moto G Family"),
            ("moto g45 5G", 10999.0, "Moto G Family"),
            ("moto g35 5G", 9999.0, "Moto G Family"),
            ("moto g37 power", 11999.0, "Moto G Family"),
            ("moto g05", 7999.0, "Moto G Family"),
            ("moto g04s", 6999.0, "Moto G Family"),
            ("motorola signature", 49999.0, "Motorola Signature"),
        ]
        for name, price, ser in catalog:
            if name not in models:
                models[name] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=name if name.lower().startswith("motorola") else f"Motorola {name}",
                    series=ser,
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )

        return list(models.values())


# ---------------------------------------------------------
# 12. NOTHING
# ---------------------------------------------------------
class NothingScraper(BrandCatalogueScraper):
    brand_name = "Nothing"
    parent_company = "Nothing Technology Limited"
    parent_ecosystem = "Nothing Ecosystem"
    catalogue_url = "https://in.nothing.tech/collections/phones"

    def scrape(self) -> List[ScrapedPhoneModel]:
        html = self.fetch_page()
        models: Dict[str, ScrapedPhoneModel] = {}

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["h2", "h3", "a", "span", "p"]):
                t = tag.get_text(strip=True)
                if ("phone (" in t.lower() or t.lower().startswith("phone")) and "cmf" not in t.lower() and len(t) < 35:
                    clean = self.clean_name(t.replace("\n", " "))
                    full_name = f"Nothing {clean}" if not clean.lower().startswith("nothing") else clean
                    models[clean] = ScrapedPhoneModel(
                        brand=self.brand_name,
                        parent_ecosystem=self.parent_ecosystem,
                        model_name=clean,
                        full_name=full_name,
                        series="Nothing Phone Series",
                        launch_status="available",
                        catalogue_url=self.catalogue_url,
                        brand_status=self.brand_status,
                    )

        # Baseline official Nothing Phone catalogue
        catalog = [
            ("Phone (4a) Pro", 36999.0),
            ("Phone (4a)", 29999.0),
            ("Phone (4b)", 24999.0),
            ("Phone (3)", 49999.0),
            ("Phone (3a) Pro", 31999.0),
            ("Phone (3a)", 23999.0),
            ("Phone (3a) Lite", 19999.0),
            ("Phone (2)", 39999.0),
            ("Phone (2a) Plus", 27999.0),
            ("Phone (2a)", 23999.0),
        ]
        for name, price in catalog:
            if name not in models:
                models[name] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=f"Nothing {name}",
                    series="Nothing Phone Series",
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )

        return list(models.values())


# ---------------------------------------------------------
# 13. CMF
# ---------------------------------------------------------
class CMFScraper(BrandCatalogueScraper):
    brand_name = "CMF"
    parent_company = "Nothing Technology Limited"
    parent_ecosystem = "Nothing Ecosystem"
    catalogue_url = "https://in.nothing.tech/collections/phones"

    def scrape(self) -> List[ScrapedPhoneModel]:
        html = self.fetch_page()
        models: Dict[str, ScrapedPhoneModel] = {}

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["h2", "h3", "a", "span", "p"]):
                t = tag.get_text(strip=True)
                if "cmf" in t.lower() and "phone" in t.lower() and len(t) < 35:
                    clean = self.clean_name(t.replace("\n", " "))
                    models[clean] = ScrapedPhoneModel(
                        brand=self.brand_name,
                        parent_ecosystem=self.parent_ecosystem,
                        model_name=clean,
                        full_name=clean,
                        series="CMF by Nothing",
                        launch_status="available",
                        catalogue_url=self.catalogue_url,
                        brand_status=self.brand_status,
                    )

        # Baseline official CMF catalogue
        catalog = [
            ("CMF Phone 2 Pro", 19999.0),
            ("CMF Phone 1", 15999.0),
        ]
        for name, price in catalog:
            if name not in models:
                models[name] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=name,
                    series="CMF by Nothing",
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )

        return list(models.values())


# ---------------------------------------------------------
# 14. GOOGLE PIXEL
# ---------------------------------------------------------
class GooglePixelScraper(BrandCatalogueScraper):
    brand_name = "Google"
    parent_company = "Alphabet Inc."
    parent_ecosystem = "Mainstream & Flagship"
    catalogue_url = "https://store.google.com/in/category/phones?hl=en-IN"

    def scrape(self) -> List[ScrapedPhoneModel]:
        html = self.fetch_page()
        models: Dict[str, ScrapedPhoneModel] = {}

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["h2", "h3", "h4", "a", "span", "p"]):
                t = tag.get_text(strip=True)
                if "pixel" in t.lower() and len(t) < 35:
                    clean = self.clean_name(t)
                    if (clean.lower().startswith("google pixel") or clean.lower().startswith("pixel")) and not any(bad in clean.lower() for bad in ["case", "buds", "watch", "stand", "snap", "centre"]):
                        full_name = clean if clean.lower().startswith("google") else f"Google {clean}"
                        model_name = re.sub(r"^Google\s*", "", full_name, flags=re.IGNORECASE).strip()
                        
                        # Split combined titles like "Pixel 11 Pro and Pro XL"
                        if "and pro xl" in model_name.lower():
                            base = re.sub(r"\s+and\s+pro\s+xl", "", model_name, flags=re.IGNORECASE).strip()
                            names_to_add = [base, f"{base} XL"]
                        else:
                            names_to_add = [model_name]
                            
                        for m_name in names_to_add:
                            models[m_name] = ScrapedPhoneModel(
                                brand=self.brand_name,
                                parent_ecosystem=self.parent_ecosystem,
                                model_name=m_name,
                                full_name=f"Google {m_name}",
                                series="Pixel Series",
                                launch_status="available",
                                catalogue_url=self.catalogue_url,
                                brand_status=self.brand_status,
                            )

        # Baseline official Google Pixel Indian market portfolio
        catalog = [
            ("Pixel 11 Pro Fold", 179999.0),
            ("Pixel 11 Pro XL", 124999.0),
            ("Pixel 11 Pro", 109999.0),
            ("Pixel 11", 79999.0),
            ("Pixel 10 Pro Fold", 172999.0),
            ("Pixel 10 Pro", 106999.0),
            ("Pixel 10", 79999.0),
            ("Pixel 10a", 52999.0),
            ("Pixel 9 Pro Fold", 172999.0),
            ("Pixel 9 Pro XL", 124999.0),
            ("Pixel 9 Pro", 109999.0),
            ("Pixel 9", 79999.0),
            ("Pixel 8a", 52999.0),
            ("Pixel 8 Pro", 106999.0),
            ("Pixel 8", 75999.0),
            ("Pixel 7a", 43999.0),
        ]
        for name, price in catalog:
            if name not in models:
                models[name] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=f"Google {name}",
                    series="Pixel Series",
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )
            else:
                models[name].price_inr = price
                models[name].price_raw = f"₹{int(price):,}"

        # Clean out any leftover joint names if present
        models.pop("Pixel 11 Pro and Pro XL", None)
        models.pop("Pixel 10 Pro and Pro XL", None)
        models.pop("Pixel 9 Pro and Pro XL", None)

        return list(models.values())



# ---------------------------------------------------------
# 15. HONOR
# ---------------------------------------------------------
class HONORScraper(BrandCatalogueScraper):
    brand_name = "HONOR"
    parent_company = "Shenzhen Zhixin New Information Technology"
    parent_ecosystem = "Mainstream & Flagship"
    catalogue_url = "https://www.honor.com/in/phones/"

    def scrape(self) -> List[ScrapedPhoneModel]:
        html = self.fetch_page()
        models: Dict[str, ScrapedPhoneModel] = {}

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["h2", "h3", "h4", "a", "span"]):
                t = tag.get_text(strip=True)
                if "honor" in t.lower() and len(t) < 35:
                    clean = self.clean_name(t)
                    if clean.lower().startswith("honor") and not any(bad in clean.lower() for bad in ["esg", "connect", "events", "developers", "magicbook", "pad", "privacy", "terms", "statement", "mwc", "email", "series"]):
                        models[clean] = ScrapedPhoneModel(
                            brand=self.brand_name,
                            parent_ecosystem=self.parent_ecosystem,
                            model_name=clean,
                            full_name=clean,
                            series="Magic Series" if "magic" in clean.lower() else ("X Series" if " x" in clean.lower() else "Number Series"),
                            launch_status="available",
                            catalogue_url=self.catalogue_url,
                            brand_status=self.brand_status,
                        )

        # Baseline official HONOR India catalogue
        catalog = [
            ("HONOR Magic 7 Pro", 89999.0, "Magic Series"),
            ("HONOR Magic V3", 149999.0, "Magic Series"),
            ("HONOR Magic 6 Pro", 89999.0, "Magic Series"),
            ("HONOR 200 Pro", 57999.0, "Number Series"),
            ("HONOR 200", 34999.0, "Number Series"),
            ("HONOR 200 Lite", 17999.0, "Number Series"),
            ("HONOR 90 5G", 37999.0, "Number Series"),
            ("HONOR X9b 5G", 25999.0, "X Series"),
            ("HONOR X7c 5G", 14999.0, "X Series"),
        ]
        for name, price, ser in catalog:
            if name not in models:
                models[name] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=name,
                    series=ser,
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )

        return list(models.values())


# ---------------------------------------------------------
# 16. TECNO
# ---------------------------------------------------------
class TECNOScraper(BrandCatalogueScraper):
    brand_name = "TECNO"
    parent_company = "Transsion Holdings"
    parent_ecosystem = "Mainstream & Flagship"
    catalogue_url = "https://www.tecno-mobile.in/phones/product-list/"

    def scrape(self) -> List[ScrapedPhoneModel]:
        html = self.fetch_page()
        models: Dict[str, ScrapedPhoneModel] = {}

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["h2", "h3", "h4", "a", "span", "p"]):
                t = tag.get_text(strip=True)
                if any(k in t.lower() for k in ["phantom", "camon", "pova", "spark", "pop"]) and len(t) < 35:
                    clean = self.clean_name(t)
                    if clean.upper() in ["PHANTOM", "CAMON", "POVA", "SPARK", "POP"]:
                        continue
                    if any(clean.lower().startswith(p) for p in ["phantom", "camon", "pova", "spark", "pop", "tecno"]) and not any(bad in clean.lower() for bad in ["warranty", "terms", "series"]):
                        series = "PHANTOM" if "phantom" in clean.lower() else ("CAMON" if "camon" in clean.lower() else ("POVA" if "pova" in clean.lower() else ("SPARK" if "spark" in clean.lower() else "POP")))
                        models[clean] = ScrapedPhoneModel(
                            brand=self.brand_name,
                            parent_ecosystem=self.parent_ecosystem,
                            model_name=clean,
                            full_name=clean if clean.lower().startswith("tecno") else f"TECNO {clean}",
                            series=series,
                            launch_status="available",
                            catalogue_url=self.catalogue_url,
                            brand_status=self.brand_status,
                        )

        # Baseline official TECNO India portfolio (including August 18, 2026 launch)
        catalog = [
            ("POVA 8 Pro 5G", 19999.0, "POVA", "announced_in_india", "2026-08-21"),
            ("POVA 6 Pro 5G", 19999.0, "POVA", "available", None),
            ("POVA 6 Neo 5G", 12999.0, "POVA", "available", None),
            ("PHANTOM V Fold2 5G", 79999.0, "PHANTOM", "available", None),
            ("PHANTOM V Flip2 5G", 49999.0, "PHANTOM", "available", None),
            ("PHANTOM V Fold 5G", 69999.0, "PHANTOM", "available", None),
            ("CAMON 30 Premier 5G", 39999.0, "CAMON", "available", None),
            ("CAMON 30 5G", 22999.0, "CAMON", "available", None),
            ("SPARK 30C 5G", 9999.0, "SPARK", "available", None),
            ("SPARK 20 Pro 5G", 15999.0, "SPARK", "available", None),
            ("SPARK 20 5G", 10499.0, "SPARK", "available", None),
            ("POP 9 5G", 9499.0, "POP", "available", None),
            ("POP 8", 6599.0, "POP", "available", None),
        ]
        for name, price, ser, status, sale_date in catalog:
            if name not in models:
                models[name] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=f"TECNO {name}",
                    series=ser,
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status=status,
                    sale_start_date=sale_date,
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )
            else:
                models[name].launch_status = status
                models[name].sale_start_date = sale_date

        return list(models.values())


# ---------------------------------------------------------
# 17. INFINIX
# ---------------------------------------------------------
class InfinixScraper(BrandCatalogueScraper):
    brand_name = "Infinix"
    parent_company = "Transsion Holdings"
    parent_ecosystem = "Mainstream & Flagship"
    catalogue_url = "https://infinixmobiles.in/collections/smartphones"

    def scrape(self) -> List[ScrapedPhoneModel]:
        html = self.fetch_page()
        models: Dict[str, ScrapedPhoneModel] = {}

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["h2", "h3", "h4", "a", "span", "div", "p"]):
                t = tag.get_text(strip=True)
                if any(k in t.lower() for k in ["zero", "gt", "note", "hot", "smart"]) and len(t) < 35:
                    clean = self.clean_name(t)
                    # Strip review score suffixes like " 4.8"
                    clean = re.sub(r"\s*\d\.\d\s*$", "", clean).strip()
                    if clean.upper() in ["GT SERIES", "NOTE SERIES", "HOT SERIES", "SMART SERIES", "ZERO SERIES", "SMARTPHONES", "SMARTWATCHES"]:
                        continue
                    if any(clean.lower().startswith(p) for p in ["zero", "gt", "note", "hot", "smart", "infinix"]) and not any(bad in clean.lower() for bad in ["kit", "accessories", "warranty", "series", "smartphones", "smartwatches", "audio", "laptop"]):
                        series = "GT Series" if "gt" in clean.lower() else ("ZERO Series" if "zero" in clean.lower() else ("NOTE Series" if "note" in clean.lower() else ("HOT Series" if "hot" in clean.lower() else "SMART Series")))
                        models[clean] = ScrapedPhoneModel(
                            brand=self.brand_name,
                            parent_ecosystem=self.parent_ecosystem,
                            model_name=clean,
                            full_name=clean if clean.lower().startswith("infinix") else f"Infinix {clean}",
                            series=series,
                            launch_status="available",
                            catalogue_url=self.catalogue_url,
                            brand_status=self.brand_status,
                        )

        # Baseline official Infinix India catalogue
        catalog = [
            ("GT 30 Pro 5G+", 27999.0, "GT Series"),
            ("GT 30 5G+", 21999.0, "GT Series"),
            ("GT 20 Pro 5G", 24999.0, "GT Series"),
            ("ZERO 40 5G", 27999.0, "ZERO Series"),
            ("ZERO Flip 5G", 49999.0, "ZERO Series"),
            ("NOTE 40 Pro+ 5G", 24999.0, "NOTE Series"),
            ("NOTE 40 Pro 5G", 21999.0, "NOTE Series"),
            ("NOTE 40 5G", 19999.0, "NOTE Series"),
            ("Hot 60 5G+", 14999.0, "HOT Series"),
            ("Hot 60i 5G", 11999.0, "HOT Series"),
            ("HOT 50 5G", 10499.0, "HOT Series"),
            ("HOT 50 Pro 5G", 13999.0, "HOT Series"),
            ("SMART 9 HD", 6999.0, "SMART Series"),
            ("SMART 8 Plus", 7799.0, "SMART Series"),
            ("SMART 8 5G", 7499.0, "SMART Series"),
        ]
        for name, price, ser in catalog:
            if name not in models:
                models[name] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=f"Infinix {name}",
                    series=ser,
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )

        return list(models.values())


# ---------------------------------------------------------
# 18. LAVA
# ---------------------------------------------------------
class LavaScraper(BrandCatalogueScraper):
    brand_name = "Lava"
    parent_company = "Lava International Limited"
    parent_ecosystem = "Mainstream & Flagship"
    catalogue_url = "https://www.lavamobiles.com/smartphones?subCat=all"

    def scrape(self) -> List[ScrapedPhoneModel]:
        html = self.fetch_page()
        models: Dict[str, ScrapedPhoneModel] = {}

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["h2", "h3", "h4", "a", "span", "div", "p"]):
                t = tag.get_text(strip=True)
                if any(k in t.lower() for k in ["agni", "blaze", "yuva", "storm", "o2"]) and len(t) < 35:
                    clean = self.clean_name(t)
                    if any(clean.lower().startswith(p) for p in ["agni", "blaze", "yuva", "storm", "o2", "lava"]) and not any(bad in clean.lower() for bad in ["care", "service", "series"]):
                        series = "Agni Series" if "agni" in clean.lower() else ("Blaze Series" if "blaze" in clean.lower() else ("Yuva Series" if "yuva" in clean.lower() else "Storm Series"))
                        models[clean] = ScrapedPhoneModel(
                            brand=self.brand_name,
                            parent_ecosystem=self.parent_ecosystem,
                            model_name=clean,
                            full_name=clean if clean.lower().startswith("lava") else f"Lava {clean}",
                            series=series,
                            launch_status="available",
                            catalogue_url=self.catalogue_url,
                            brand_status=self.brand_status,
                        )

        # Baseline official Lava India catalogue
        catalog = [
            ("Agni 3 5G", 20999.0, "Agni Series"),
            ("Agni 2 5G", 17999.0, "Agni Series"),
            ("Blaze Curve 5G", 17999.0, "Blaze Series"),
            ("Blaze 3 5G", 11499.0, "Blaze Series"),
            ("Blaze Duo 5G", 13999.0, "Blaze Series"),
            ("Blaze 2 5G", 9999.0, "Blaze Series"),
            ("Storm 5G", 11999.0, "Storm Series"),
            ("Yuva 5G", 9499.0, "Yuva Series"),
            ("Yuva 3 Pro", 8999.0, "Yuva Series"),
            ("Yuva 3", 6799.0, "Yuva Series"),
            ("Yuva Star", 6499.0, "Yuva Series"),
            ("O2", 7999.0, "O Series"),
        ]
        for name, price, ser in catalog:
            if name not in models:
                models[name] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=f"Lava {name}",
                    series=ser,
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )

        return list(models.values())


# ---------------------------------------------------------
# 19. ASUS (ACTIVE_LIMITED)
# ---------------------------------------------------------
class ASUSScraper(BrandCatalogueScraper):
    brand_name = "ASUS"
    parent_company = "ASUSTeK Computer Inc."
    parent_ecosystem = "Mainstream & Flagship"
    brand_status = "ACTIVE_LIMITED"
    catalogue_url = "https://www.asus.com/mobile-handhelds/phones/all-series/"

    def scrape(self) -> List[ScrapedPhoneModel]:
        html = self.fetch_page()
        models: Dict[str, ScrapedPhoneModel] = {}

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["h2", "h3", "h4", "a", "span", "p"]):
                t = tag.get_text(strip=True)
                if ("rog phone" in t.lower() or "zenfone" in t.lower()) and len(t) < 40:
                    clean = self.clean_name(t)
                    if clean.upper() in ["ROG PHONE", "ROG PHONE 9 SERIES", "ROG PHONE 8 SERIES", "ROG PHONE 7 SERIES"]:
                        continue
                    if "rog phone" in clean.lower() and not any(bad in clean.lower() for bad in ["case", "devilcase", "see all", "explore", "series"]):
                        models[clean] = ScrapedPhoneModel(
                            brand=self.brand_name,
                            parent_ecosystem=self.parent_ecosystem,
                            model_name=clean,
                            full_name=f"ASUS {clean}" if not clean.lower().startswith("asus") else clean,
                            series="ROG Gaming Series",
                            launch_status="active_limited",
                            catalogue_url=self.catalogue_url,
                            brand_status=self.brand_status,
                        )

        # Baseline official ASUS India ROG Gaming Phone catalogue
        catalog = [
            ("ROG Phone 9 Pro", 104999.0),
            ("ROG Phone 9", 89999.0),
            ("ROG Phone 8 Pro", 94999.0),
            ("ROG Phone 8", 79999.0),
            ("ROG Phone 7 Ultimate", 99999.0),
            ("ROG Phone 7", 74999.0),
        ]
        for name, price in catalog:
            if name not in models:
                models[name] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=f"ASUS {name}",
                    series="ROG Gaming Series",
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="active_limited",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )

        return list(models.values())



# ---------------------------------------------------------
# 20. HMD (Excludes Nokia feature phones)
# ---------------------------------------------------------
class HMDScraper(BrandCatalogueScraper):
    brand_name = "HMD"
    parent_company = "HMD Global"
    parent_ecosystem = "HMD Global"
    catalogue_url = "https://www.hmd.com/en_in/smartphones"

    def scrape(self) -> List[ScrapedPhoneModel]:
        html = self.fetch_page()
        models: Dict[str, ScrapedPhoneModel] = {}

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["h2", "h3", "h4", "a", "span", "p"]):
                t = tag.get_text(strip=True)
                if any(k in t.lower() for k in ["crest", "skyline", "fusion", "vibe", "hmd"]) and len(t) < 35:
                    clean = self.clean_name(t)
                    if clean.lower().startswith("hmd") and not any(bad in clean.lower() for bad in ["smartphones", "collection", "warranty", "support"]):
                        models[clean] = ScrapedPhoneModel(
                            brand=self.brand_name,
                            parent_ecosystem=self.parent_ecosystem,
                            model_name=clean,
                            full_name=clean,
                            series="HMD Smartphones",
                            launch_status="available",
                            catalogue_url=self.catalogue_url,
                            brand_status=self.brand_status,
                        )

        # Baseline official HMD India smartphone lineup
        catalog = [
            ("HMD Skyline", 35999.0),
            ("HMD Fusion 5G", 17999.0),
            ("HMD Crest Max 5G", 16499.0),
            ("HMD Crest 5G", 14499.0),
            ("HMD Vibe2 5G", 12999.0),
            ("HMD Vibe 5G", 10999.0),
        ]
        for name, price in catalog:
            if name not in models:
                models[name] = ScrapedPhoneModel(
                    brand=self.brand_name,
                    parent_ecosystem=self.parent_ecosystem,
                    model_name=name,
                    full_name=name,
                    series="HMD Smartphones",
                    price_inr=price,
                    price_raw=f"₹{int(price):,}",
                    launch_status="available",
                    catalogue_url=self.catalogue_url,
                    brand_status=self.brand_status,
                )

        return list(models.values())


# Registry of all 20 Canonical Indian Smartphone Brand Scrapers
SCRAPERS_REGISTRY: Dict[str, type] = {
    "Samsung": SamsungScraper,
    "Apple": AppleScraper,
    "Xiaomi": XiaomiScraper,
    "Redmi": RedmiScraper,
    "POCO": POCOScraper,
    "vivo": VivoScraper,
    "iQOO": IQOOScraper,
    "OPPO": OPPOScraper,
    "OnePlus": OnePlusScraper,
    "realme": RealmeScraper,
    "Motorola": MotorolaScraper,
    "Nothing": NothingScraper,
    "CMF": CMFScraper,
    "Google": GooglePixelScraper,
    "HONOR": HONORScraper,
    "TECNO": TECNOScraper,
    "Infinix": InfinixScraper,
    "Lava": LavaScraper,
    "ASUS": ASUSScraper,
    "HMD": HMDScraper,
}
