from typing import Dict, Any, List

PERSONA_WEIGHTS: Dict[str, Dict[str, float]] = {
    "Student": {
        "camera": 0.15,
        "performance": 0.15,
        "battery": 0.20,
        "display": 0.10,
        "storage": 0.10,
        "build": 0.05,
        "value": 0.25
    },
    "Gamer": {
        "camera": 0.05,
        "performance": 0.30,
        "battery": 0.20,
        "display": 0.25,
        "storage": 0.05,
        "build": 0.05,
        "value": 0.10
    },
    "Content Creator": {
        "camera": 0.35,
        "performance": 0.15,
        "battery": 0.15,
        "display": 0.15,
        "storage": 0.10,
        "build": 0.05,
        "value": 0.05
    },
    "Professional": {
        "camera": 0.10,
        "performance": 0.15,
        "battery": 0.25,
        "display": 0.15,
        "storage": 0.10,
        "build": 0.15,
        "value": 0.10
    },
    "Senior/Basic": {
        "camera": 0.05,
        "performance": 0.05,
        "battery": 0.30,
        "display": 0.25,
        "storage": 0.05,
        "build": 0.05,
        "value": 0.25
    },
    "Photography": {
        "camera": 0.40,
        "performance": 0.10,
        "battery": 0.15,
        "display": 0.15,
        "storage": 0.10,
        "build": 0.05,
        "value": 0.05
    },
    "General": {
        "camera": 0.20,
        "performance": 0.20,
        "battery": 0.20,
        "display": 0.15,
        "storage": 0.10,
        "build": 0.05,
        "value": 0.10
    }
}

PRICE_TIERS = {
    "Budget": (0, 15000),
    "Mid-Range": (15000, 30000),
    "Premium Mid-Range": (30000, 50000),
    "Flagship": (50000, 100000),
    "Ultra Premium": (100000, float('inf'))
}

# Software UI Quality & Bloatware Taxonomy Matrix (0.0 to 1.0)
SOFTWARE_UI_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "google": {"tier": 1, "name": "Pixel UI (Stock)", "cleanliness": 1.0, "bloatware_free": 1.0, "update_speed": 1.0},
    "motorola": {"tier": 1, "name": "Hello UI (Near-Stock)", "cleanliness": 0.95, "bloatware_free": 0.92, "update_speed": 0.75},
    "nothing": {"tier": 1, "name": "Nothing OS", "cleanliness": 0.95, "bloatware_free": 0.98, "update_speed": 0.88},
    "cmf": {"tier": 1, "name": "Nothing OS", "cleanliness": 0.95, "bloatware_free": 0.98, "update_speed": 0.85},
    "apple": {"tier": 1, "name": "iOS", "cleanliness": 1.0, "bloatware_free": 1.0, "update_speed": 1.0},
    "lava": {"tier": 1, "name": "Clean Stock Android", "cleanliness": 0.90, "bloatware_free": 0.90, "update_speed": 0.70},
    "hmd": {"tier": 1, "name": "Clean Android", "cleanliness": 0.90, "bloatware_free": 0.90, "update_speed": 0.70},
    "samsung": {"tier": 2, "name": "One UI", "cleanliness": 0.88, "bloatware_free": 0.82, "update_speed": 0.95},
    "oneplus": {"tier": 2, "name": "OxygenOS", "cleanliness": 0.85, "bloatware_free": 0.80, "update_speed": 0.85},
    "honor": {"tier": 2, "name": "MagicOS", "cleanliness": 0.78, "bloatware_free": 0.70, "update_speed": 0.75},
    "realme": {"tier": 3, "name": "Realme UI", "cleanliness": 0.68, "bloatware_free": 0.55, "update_speed": 0.75},
    "vivo": {"tier": 3, "name": "Funtouch OS", "cleanliness": 0.68, "bloatware_free": 0.55, "update_speed": 0.75},
    "iqoo": {"tier": 3, "name": "Funtouch OS (iQOO)", "cleanliness": 0.70, "bloatware_free": 0.58, "update_speed": 0.78},
    "oppo": {"tier": 3, "name": "ColorOS", "cleanliness": 0.70, "bloatware_free": 0.58, "update_speed": 0.78},
    "xiaomi": {"tier": 3, "name": "HyperOS", "cleanliness": 0.65, "bloatware_free": 0.50, "update_speed": 0.75},
    "redmi": {"tier": 3, "name": "HyperOS", "cleanliness": 0.65, "bloatware_free": 0.50, "update_speed": 0.70},
    "poco": {"tier": 3, "name": "HyperOS (POCO)", "cleanliness": 0.65, "bloatware_free": 0.50, "update_speed": 0.70},
    "infinix": {"tier": 3, "name": "XOS", "cleanliness": 0.60, "bloatware_free": 0.45, "update_speed": 0.60},
    "tecno": {"tier": 3, "name": "HiOS", "cleanliness": 0.60, "bloatware_free": 0.45, "update_speed": 0.60},
}

# Sub-Brand & Lineup Series DNA Hierarchy
LINEUP_DNA_HIERARCHY: Dict[str, list] = {
    "gaming": [
        "iqoo neo", "iqoo pro", "iqoo 13", "iqoo 12", "iqoo 11", "iqoo 9",
        "poco f", "poco x", "realme gt", "oneplus r", "oneplus 12r", "oneplus 13r",
        "infinix gt", "infinix gt 20 pro"
    ],
    "camera": [
        "vivo x", "vivo v", "pixel", "ultra", "find x", "reno pro", "reno 12 pro",
        "reno 13 pro", "reno 14 pro", "reno 15 pro", "phone (3a) pro", "phone (2a) plus",
        "galaxy s24 ultra", "galaxy s25 ultra", "xiaomi 14 ultra", "xiaomi 15 ultra",
        "xiaomi 16 ultra", "xiaomi 17 ultra", "iphone pro", "iphone pro max"
    ],
    "battery_value": [
        "moto g", "moto g power", "moto g57", "moto g85", "poco m", "galaxy m",
        "galaxy f", "redmi note", "narzo", "realme p", "vivo t", "infinix note"
    ],
    "flagship": [
        "galaxy s25", "galaxy s24", "galaxy z fold", "galaxy z flip", "iphone 16 pro",
        "iphone 17 pro", "iphone 16 pro max", "iphone 17 pro max", "vivo x100 pro",
        "vivo x200 pro", "vivo x300 pro", "find n", "find x8 pro", "mix fold"
    ]
}
