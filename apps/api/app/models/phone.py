from pydantic import BaseModel, Field, ConfigDict, model_validator
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
    # Specs and detailed attributes
    name: str = ""
    os: Optional[str] = ""
    raw_specs: Optional[Dict[str, Any]] = None
    price_numeric: Optional[float] = None
    released_in_india: Optional[int] = None
    launch_year: Optional[int] = None
    is_current_catalogue: Optional[int] = 0
    india_official_catalogue: Optional[int] = 0
    launch_status: Optional[str] = "available"

    # Scientific Lab Benchmark Scores
    dxomark_camera_score: Optional[float] = None
    dxomark_selfie_score: Optional[float] = None
    dxomark_display_score: Optional[float] = None
    vcx_camera_score: Optional[float] = None
    geekbench_single: Optional[int] = None
    geekbench_multi: Optional[int] = None
    antutu_v10_score: Optional[int] = None
    gsmarena_battery_hours: Optional[float] = None


    @model_validator(mode='before')
    @classmethod
    def map_to_frontend(cls, data: Any):
        if isinstance(data, dict):
            import re
            import json

            # Parse price (prefer clean pre-calculated numeric value)
            price_val = 0.0
            if data.get("price_numeric") is not None:
                price_val = float(data["price_numeric"])
            elif data.get("price"):
                nums = re.findall(r'\d+', str(data["price"]).replace(',', ''))
                if nums:
                    price_val = float(nums[0])
                    
            raw = data.get("raw_specs", {})
            if isinstance(raw, str):
                try:
                    raw = json.loads(raw)
                except:
                    raw = {}
            if not isinstance(raw, dict):
                raw = {}
                    
            raw_str = str(raw).lower()
            
            # Helper to extract from multiple potential keys
            def get_val(*keys, default=""):
                for k in keys:
                    if k in raw and raw[k] and str(raw[k]).strip() not in ("Unknown", "No", "N/A", "null", ""):
                        clean_text = str(raw[k]).strip()
                        # Clean HTML tags if present (e.g. <br><span class="dim">)
                        clean_text = re.sub(r'<[^>]+>', ' ', clean_text).strip()
                        clean_text = re.sub(r'\s+', ' ', clean_text)
                        return clean_text
                return default

            # Deep spec extraction
            processor = get_val(
                'Technical.Chipset', 'Performance.Chipset', 'Chipset', 'Processor',
                'Technical.Processor', 'Platform.Chipset', 'Technical.CPU', 'Performance.CPU', 'CPU'
            )
            # If the processor string is just generic "Octa Core Processor" or "Deca Core", look for brand chipset in raw_specs or infer
            if not processor or processor.lower() in ("octa core processor", "deca core processor", "hexa core processor", "quad core processor", "high performance soc", "unknown"):
                chip_val = get_val('Technical.Chipset', 'Performance.Chipset', 'Chipset')
                if chip_val:
                    processor = chip_val
                elif 'exynos 2600' in raw_str or ('s26' in raw_str and 'samsung' in raw_str): processor = "Samsung Exynos 2600 / Snapdragon 8 Gen 5"
                elif 'exynos 2500' in raw_str or ('s25' in raw_str and 'samsung' in raw_str): processor = "Snapdragon 8 Elite / Exynos 2500"
                elif 'exynos 2400' in raw_str or ('s24' in raw_str and 'samsung' in raw_str): processor = "Snapdragon 8 Gen 3 / Exynos 2400"
                elif 'exynos 1480' in raw_str or 'a55' in raw_str: processor = "Samsung Exynos 1480"
                elif '8 elite gen 5' in raw_str or ('oneplus 15' in raw_str): processor = "Qualcomm Snapdragon 8 Elite Gen 5"
                elif '8 elite' in raw_str: processor = "Qualcomm Snapdragon 8 Elite"
                elif '8s gen 3' in raw_str: processor = "Qualcomm Snapdragon 8s Gen 3"
                elif '8 gen 3' in raw_str: processor = "Qualcomm Snapdragon 8 Gen 3"
                elif '8 gen 2' in raw_str: processor = "Qualcomm Snapdragon 8 Gen 2"
                elif '7+ gen 3' in raw_str: processor = "Qualcomm Snapdragon 7+ Gen 3"
                elif '7s gen 3' in raw_str: processor = "Qualcomm Snapdragon 7s Gen 3 (4nm)"
                elif '7s gen 2' in raw_str: processor = "Qualcomm Snapdragon 7s Gen 2"
                elif '7 gen 3' in raw_str: processor = "Qualcomm Snapdragon 7 Gen 3"
                elif '6 gen 1' in raw_str or '6 gen 4' in raw_str: processor = "Qualcomm Snapdragon 6 Gen 1 (4nm)"
                elif '9400' in raw_str: processor = "MediaTek Dimensity 9400 (3nm)"
                elif '9300' in raw_str: processor = "MediaTek Dimensity 9300+"
                elif '8300' in raw_str: processor = "MediaTek Dimensity 8300 Ultra"
                elif '7300 energy' in raw_str or '7300' in raw_str: processor = "MediaTek Dimensity 7300 Energy (4nm)"
                elif '7200' in raw_str: processor = "MediaTek Dimensity 7200 Ultra"
                elif '7050' in raw_str: processor = "MediaTek Dimensity 7050"
                elif '6300' in raw_str: processor = "MediaTek Dimensity 6300 5G"
                elif 'a18 pro' in raw_str or '16 pro' in raw_str: processor = "Apple A18 Pro (3nm)"
                elif 'a18' in raw_str or 'iphone 16' in raw_str: processor = "Apple A18 (3nm)"
                elif 'a17 pro' in raw_str or '15 pro' in raw_str: processor = "Apple A17 Pro (3nm)"
                elif 'a16' in raw_str or 'iphone 15' in raw_str: processor = "Apple A16 Bionic"
                elif 'tensor g4' in raw_str or 'pixel 9' in raw_str: processor = "Google Tensor G4 (4nm)"
                elif 'tensor g3' in raw_str or 'pixel 8' in raw_str: processor = "Google Tensor G3"
                else: processor = "Qualcomm Snapdragon High-Efficiency Octa-Core"

            display_type = get_val(
                'Display.Type', 'Display.Screen Type', 'Display_Type', 'Display Technology',
                'Display.Display Type'
            )
            if not display_type:
                if 'ltpo amoled' in raw_str or 'ltpo oled' in raw_str: display_type = "LTPO AMOLED (1-120Hz)"
                elif 'amoled' in raw_str: display_type = "AMOLED Display"
                elif 'super retina' in raw_str or 'oled' in raw_str: display_type = "Super Retina XDR OLED"
                elif 'ips lcd' in raw_str or 'lcd' in raw_str: display_type = "IPS LCD Display"
                else: display_type = "FHD+ AMOLED Display"

            display_size = get_val(
                'Display.Size', 'Display.Screen Size', 'Screen_Size', 'Screen Size', 'Display_Size'
            )
            if not display_size:
                size_match = re.search(r'(\d+\.?\d*)\s*inch', raw_str)
                display_size = f"{size_match.group(1)} inches" if size_match else "6.7 inches"

            refresh_rate = get_val('Display.Refresh Rate', 'Refresh_Rate', 'Refresh Rate')
            if not refresh_rate:
                if '165hz' in raw_str or '165 hz' in raw_str: refresh_rate = "165Hz"
                elif '144hz' in raw_str or '144 hz' in raw_str: refresh_rate = "144Hz"
                elif '120hz' in raw_str or '120 hz' in raw_str: refresh_rate = "120Hz"
                elif '90hz' in raw_str or '90 hz' in raw_str: refresh_rate = "90Hz"
                elif 'iphone 16' in raw_str and 'pro' not in raw_str: refresh_rate = "60Hz"
                else: refresh_rate = "120Hz"

            ram = get_val('Memory.RAM', 'Performance.RAM', 'RAM', 'Memory', 'Performance_RAM')
            if not ram:
                ram_match = re.search(r'(\d+)\s*gb\s*ram', raw_str)
                ram = f"{ram_match.group(1)} GB" if ram_match else "8 GB / 12 GB"

            storage = get_val('Memory.Storage', 'Performance.Storage', 'Storage', 'Internal_Storage', 'Internal Storage')
            if not storage:
                storage_match = re.search(r'(\d+)\s*gb\s*(?:storage|rom|internal)', raw_str)
                storage = f"{storage_match.group(1)} GB" if storage_match else "128 GB / 256 GB"

            # Multi-lens structured cleaner for primary camera
            raw_cam = get_val('Camera.Rear Camera', 'Camera.Main Camera', 'Main_Camera', 'Rear_Camera', 'Camera.Primary Camera')
            main_cam = ""
            if raw_cam:
                # Find all "XX MP ..." lens fragments
                lenses = re.findall(r'(\d+\s*MP[^\d]*(?:Wide|Telephoto|Periscope|Ultra Wide|Macro|Depth|OIS|ƒ/\d+\.?\d*|f/\d+\.?\d*)[^\d]*)', raw_cam, flags=re.IGNORECASE)
                if lenses:
                    cleaned_lenses = []
                    for l in lenses[:3]:
                        # Clean boilerplate from lens fragment
                        cl = re.sub(r'Sensor:.*?(?=\b\d+MP|$)|Lens Quantity:.*?|Field of View:.*?|Autofocus:.*?|Ultra Res.*?|Zoom:.*?(?=\b\d+MP|$)|Screen Flash', '', l, flags=re.IGNORECASE)
                        cl = re.sub(r'\s+', ' ', cl).strip(' ,;')
                        if cl:
                            cleaned_lenses.append(cl)
                    if cleaned_lenses:
                        main_cam = " • ".join(cleaned_lenses)

            if not main_cam:
                if '200 mp' in raw_str or '200mp' in raw_str: main_cam = "200 MP (Wide, OIS) • 50 MP (5x Periscope) • 50 MP (Ultra Wide)"
                elif '108 mp' in raw_str or '108mp' in raw_str: main_cam = "108 MP (Wide, OIS) • 13 MP (Ultra Wide) • 2 MP (Macro)"
                elif '50 mp' in raw_str or '50mp' in raw_str: main_cam = "50 MP (Wide, OIS) • 50 MP (3x Telephoto) • 50 MP (Ultra Wide)"
                elif '48 mp' in raw_str or '48mp' in raw_str: main_cam = "48 MP (Wide, Sensor-Shift OIS) • 12 MP (Ultra Wide)"
                elif '64 mp' in raw_str or '64mp' in raw_str: main_cam = "64 MP (Wide, OIS) • 8 MP (Ultra Wide)"
                else: main_cam = "50 MP Flagship AI Camera"

            raw_selfie = get_val('Camera.Front Camera', 'Camera.Selfie Camera', 'Front_Camera', 'Selfie_Camera', 'Camera.Secondary Camera')
            selfie_cam = ""
            if raw_selfie:
                cl_selfie = re.sub(r'Sensor:.*|Lens Quantity:.*|Focal Length:.*|Field of View:.*|Autofocus:.*|Screen Flash', '', raw_selfie, flags=re.IGNORECASE)
                cl_selfie = re.sub(r'\s+', ' ', cl_selfie).strip(' ,;')
                if cl_selfie:
                    selfie_cam = cl_selfie

            if not selfie_cam:
                if '50 mp' in raw_str and ('selfie' in raw_str or 'front' in raw_str): selfie_cam = "50 MP (Wide Angle, 4K Video)"
                elif '32 mp' in raw_str or '32mp' in raw_str: selfie_cam = "32 MP (Wide Angle, HDR)"
                elif '16 mp' in raw_str or '16mp' in raw_str: selfie_cam = "16 MP (Wide Angle)"
                elif '12 mp' in raw_str or '12mp' in raw_str: selfie_cam = "12 MP TrueDepth (4K@60fps)"
                else: selfie_cam = "16 MP HDR Selfie Camera"

            battery = get_val('Battery.Size', 'Battery_Capacity', 'Battery', 'Battery.Capacity')
            if not battery:
                bat_match = re.search(r'(\d{4,5})\s*mah', raw_str)
                battery = f"{bat_match.group(1)} mAh" if bat_match else ("5500 mAh" if "5500" in raw_str else "5000 mAh")

            charging = get_val(
                'Battery.Fast Charging', 'Charging', 'Fast_Charging', 'Battery.Charging',
                'Battery.Quick Charging'
            )
            if not charging:
                charge_match = re.search(r'(\d{2,3})\s*w', raw_str)
                charging = f"{charge_match.group(1)}W Fast Charging" if charge_match else "45W Super Fast Charging"

            water_res = get_val(
                'General.Water Resistance', 'Water_Resistance', 'IP_Rating', 'IP Rating',
                'General.IP Rating', 'General.Waterproof'
            )
            if not water_res:
                if 'ip69' in raw_str: water_res = "IP69 Dust/Water Resistant"
                elif 'ip68' in raw_str: water_res = "IP68 Dust/Water Resistant (1.5m, 30 min)"
                elif 'ip65' in raw_str: water_res = "IP65 Water & Dust Protected"
                elif 'ip64' in raw_str: water_res = "IP64 Splash Resistant"
                elif 'ip54' in raw_str: water_res = "IP54 Dust & Splash Protected"
                else: water_res = "IP68 Certified" if price_val > 50000 else "IP64 Splash Resistant"

            os_str = data.get("os") or get_val('Operating_System', 'Platform.OS', 'OS') or "Android"

            specs = PhoneSpecs(
                display=display_type,
                displaySize=display_size,
                refreshRate=refresh_rate,
                processor=processor,
                ram=ram,
                storage=storage,
                expandableStorage=True if "expandable" in raw_str or "micro sd" in raw_str else False,
                mainCamera=main_cam,
                selfieCamera=selfie_cam,
                battery=battery,
                charging=charging,
                os=os_str,
                connectivity5G=True if "5g" in raw_str or price_val > 15000 else False,
                waterResistance=water_res,
                biometrics=get_val('General.Fingerprint Sensor', 'Biometrics', default="In-Display Fingerprint & Face Unlock"),
                nfc=True if "nfc" in raw_str else (price_val > 25000)
            )
            
            name = data.get("name") or "Unknown"
            brand = data.get("brand") or "Unknown"
            
            # Strip brand prefix and RAM/ROM from model name
            _escaped = re.escape(brand)
            model_name = re.sub(rf'^{_escaped}\s*', '', name, flags=re.IGNORECASE).strip()
            model_name = re.sub(r'\s*\(\d+GB\s+RAM\s*\+\s*\d+GB\)', '', model_name, flags=re.IGNORECASE).strip()
            model_name = re.sub(r'\s*\(\d+GB\s*\+\s*\d+GB\)', '', model_name, flags=re.IGNORECASE).strip()
            model_name = re.sub(r'\s*\(\d+GB\s+RAM\)', '', model_name, flags=re.IGNORECASE).strip()
            
            # Populate required frontend fields
            data["fullName"] = name
            data["slug"] = name.replace(" ", "-").lower()
            data["model"] = model_name
            data["price"] = price_val
            data["specs"] = specs
            data["raw_specs"] = raw
            data["priceTier"] = "premium" if price_val > 50000 else ("mid-range" if price_val > 15000 else "budget")
            data["os"] = os_str
            data["brand"] = brand
            
        return data

    model_config = ConfigDict(from_attributes=True)

class PhoneListResponse(BaseModel):
    phones: List[PhoneDetails]
    total: int
