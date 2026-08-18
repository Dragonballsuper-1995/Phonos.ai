"""
Hardware & Benchmark Scoring Matrix for Phonos.ai
===================================================
Granular multi-dimensional hardware evaluation engine:
1. SoC Benchmark Index (Snapdragon 8 Elite, Dimensity 9400, Apple A18/A17, Tensor G4)
2. Camera & Creator Optics Index (4K120, 10-bit Log, Dolby Vision, Periscope Zoom, Zeiss APO/Leica, 1-inch sensor)
3. Display Engineering Index (LTPO, 1.5K/2K, AMOLED vs LCD, Refresh Rate, Peak Nits)
4. Battery Endurance & Flash Charge Index (mAh capacity, Wattage tiers, Wireless)
5. Build Quality & Durability Index (IP68/IP69, Victus 2/Ceramic Shield, Titanium)
"""

import re
from typing import Dict, Any
from app.models.phone import PhoneDetails

# ─── 1. COMPREHENSIVE SOC BENCHMARK INDEX (0 to 100) ─────────────────────────
SOC_BENCHMARK_MAP = {
    # Flagship Extreme (2.0M - 3M+ AnTuTu / Geekbench 6)
    "snapdragon 8 elite": 100.0,
    "dimensity 9400": 98.0,
    "a18 pro": 98.0,
    "a18": 95.0,
    "snapdragon 8 gen 3": 92.0,
    "dimensity 9300+": 92.0,
    "dimensity 9300": 90.0,
    "a17 pro": 90.0,
    "snapdragon 8s gen 3": 85.0,
    "dimensity 8350": 83.0,
    "dimensity 8300 ultra": 83.0,
    "dimensity 8300": 82.0,
    "snapdragon 7+ gen 3": 81.0,
    "snapdragon 8 gen 2": 82.0,
    "a16 bionic": 82.0,
    "a15 bionic": 78.0,
    "tensor g4": 78.0,
    "dimensity 8200 ultimate": 76.0,
    "dimensity 8200": 75.0,
    "dimensity 8100": 73.0,
    
    # Upper Mid-Range (800K - 1.2M AnTuTu)
    "snapdragon 8+ gen 1": 78.0,
    "snapdragon 8 gen 1": 75.0,
    "snapdragon 7 gen 3": 70.0,
    "dimensity 7300 energy": 69.0,
    "dimensity 7300": 68.0,
    "dimensity 7200 pro": 68.0,
    "dimensity 7200 ultra": 68.0,
    "dimensity 7200": 67.0,
    "tensor g3": 72.0,
    "tensor g2": 65.0,
    "snapdragon 778g": 62.0,
    
    # Budget 5G (400K - 750K AnTuTu)
    "snapdragon 7s gen 2": 62.0,
    "dimensity 7050": 58.0,
    "dimensity 7020": 57.0,
    "snapdragon 6 gen 1": 55.0,
    "snapdragon 6s gen 3": 54.0,
    "snapdragon 695": 52.0,
    "dimensity 6080": 50.0,
    "dimensity 6100+": 49.0,
    "dimensity 6300": 50.0,
    "snapdragon 4 gen 2": 46.0,
    "snapdragon 4 gen 1": 44.0,
    
    # Entry-level / 4G
    "helio g99": 38.0,
    "helio g88": 32.0,
    "helio g85": 30.0,
    "unisoc t616": 28.0,
    "unisoc t612": 25.0,
    "unisoc t606": 22.0
}

def evaluate_soc_score(raw_text: str) -> float:
    """Calculates 0-100 processor performance score from raw spec strings."""
    t = raw_text.lower()
    for soc_name, score in SOC_BENCHMARK_MAP.items():
        if soc_name in t:
            return score
            
    # Generic fallbacks
    if "snapdragon 8" in t or "dimensity 9" in t or "a18" in t or "a17" in t: return 90.0
    if "snapdragon 7" in t or "dimensity 8" in t or "a16" in t: return 75.0
    if "snapdragon 6" in t or "dimensity 7" in t: return 60.0
    if "snapdragon 4" in t or "dimensity 6" in t: return 48.0
    if "octa-core" in t or "octa core" in t: return 45.0
    return 35.0

def evaluate_camera_score(raw_text: str, name: str) -> float:
    """Calculates 0-100 camera optics, video capabilities, and sensor score."""
    t = (raw_text + " " + name).lower()
    score = 42.0 # baseline
    
    # Dedicated Optical Image Stabilization (OIS)
    if "ois" in t or "optical image stabilization" in t or "sensor-shift" in t:
        score += 15.0
        
    # Periscope / Telephoto Optical Zoom / ZEISS APO
    if "periscope" in t or "telephoto" in t or "apo" in t or "optical zoom" in t or "3.5x" in t or "5x" in t:
        score += 20.0
        
    # High-end sensor & optical co-engineering
    if any(k in t for k in ["zeiss", "hasselblad", "leica", "sony lyt", "imx989", "imx890", "hp2", "photonic"]):
        score += 12.0
        
    # Creator Pro Video: 4K120, 10-bit Log, Dolby Vision
    if any(k in t for k in ["4k@120fps", "4k 120", "120fps", "dolby vision", "log video", "pro video", "cinematic mode"]):
        score += 12.0
    elif "4k@60fps" in t or "8k" in t or "4k 60" in t:
        score += 6.0
        
    # Front camera quality (for creators / social media / reels)
    if any(k in t for k in ["center stage", "32 mp", "32mp", "50 mp front", "50mp front", "4k front", "autofocus selfie"]):
        score += 6.0
        
    # Megapixel primary thresholds
    if "200 mp" in t or "200mp" in t: score += 6.0
    elif "108 mp" in t or "108mp" in t or "50 mp" in t or "50mp" in t: score += 4.0
    
    return min(100.0, score)

def evaluate_display_score(raw_text: str) -> float:
    """Calculates 0-100 display engineering and panel quality score."""
    t = raw_text.lower()
    score = 50.0
    
    # Panel Type
    if "amoled" in t or "oled" in t or "poled" in t or "super retina" in t:
        score += 20.0
        
    # LTPO dynamic refresh
    if "ltpo" in t or "promotion" in t:
        score += 12.0
        
    # Refresh Rate
    if "165hz" in t or "144hz" in t: score += 10.0
    elif "120hz" in t: score += 8.0
    elif "90hz" in t: score += 4.0
    
    # Resolution
    if "2k" in t or "1440 x" in t or "qhd" in t: score += 10.0
    elif "1.5k" in t or "1220 x" in t or "1260 x" in t: score += 6.0
    
    # Brightness
    if any(k in t for k in ["4500 nits", "4000 nits", "3000 nits", "2600 nits", "2000 nits"]):
        score += 6.0
        
    return min(100.0, score)

def evaluate_battery_charge_score(raw_text: str) -> float:
    """Calculates 0-100 battery capacity & fast charging speed score."""
    t = raw_text.lower()
    score = 50.0
    
    # Battery Capacity
    if "8000 mah" in t or "7300 mah" in t or "7000 mah" in t or "7000mah" in t: score += 25.0
    elif "6500 mah" in t or "6000 mah" in t or "6000mah" in t: score += 20.0
    elif "5500 mah" in t or "5500mah" in t: score += 15.0
    elif "5000 mah" in t or "5000mah" in t: score += 10.0
    
    # Charging Wattage
    if any(k in t for k in ["150w", "120w", "100w", "90w", "80w"]): score += 20.0
    elif any(k in t for k in ["67w", "65w", "66w"]): score += 15.0
    elif any(k in t for k in ["45w", "33w"]): score += 10.0
    elif "25w" in t: score += 5.0
    
    # Wireless Charging / MagSafe
    if "wireless charging" in t or "magsafe" in t or "magcharge" in t:
        score += 8.0
        
    return min(100.0, score)

def evaluate_build_score(raw_text: str) -> float:
    """Calculates 0-100 chassis and durability score."""
    t = raw_text.lower()
    score = 50.0
    
    if "ip68" in t or "ip69" in t: score += 25.0
    elif "ip65" in t or "ip64" in t or "ip54" in t: score += 10.0
    
    if "titanium" in t: score += 15.0
    elif "aluminum" in t or "metal frame" in t: score += 10.0
    
    if "victus" in t or "ceramic shield" in t or "kunlun" in t or "panda glass" in t:
        score += 10.0
        
    return min(100.0, score)

def extract_hardware_spec_vector(phone: PhoneDetails) -> Dict[str, float]:
    raw_str = str(phone.raw_specs or "")
    name = str(phone.name or "")
    
    return {
        "soc_score": evaluate_soc_score(raw_str),
        "camera_score": evaluate_camera_score(raw_str, name),
        "display_score": evaluate_display_score(raw_str),
        "battery_charge_score": evaluate_battery_charge_score(raw_str),
        "build_score": evaluate_build_score(raw_str)
    }
