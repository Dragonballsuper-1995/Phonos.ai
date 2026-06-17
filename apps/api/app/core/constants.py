from typing import Dict

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
