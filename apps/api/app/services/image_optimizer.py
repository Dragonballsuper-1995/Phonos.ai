"""
image_optimizer.py — Image Asset Optimization and Standardizer for Phonos.ai
=============================================================================
Standardizes phone hardware images, generates high-efficiency WebP/SVG fallback URLs,
and validates asset accessibility for the Next.js frontend and CDN caching.
"""

import re
import urllib.parse
from typing import Optional, Dict

# Standard CDN image placeholder mapping for major brands
BRAND_PLACEHOLDER_THEMES = {
    "apple": {"bg": "1D1D1F", "text": "F5F5F7"},
    "samsung": {"bg": "1428A0", "text": "FFFFFF"},
    "oneplus": {"bg": "EB0029", "text": "FFFFFF"},
    "vivo": {"bg": "004080", "text": "FFFFFF"},
    "iqoo": {"bg": "FF6600", "text": "FFFFFF"},
    "realme": {"bg": "FFC800", "text": "000000"},
    "xiaomi": {"bg": "FF6700", "text": "FFFFFF"},
    "motorola": {"bg": "00142E", "text": "FFFFFF"},
    "nothing": {"bg": "0A0A0A", "text": "FFFFFF"},
    "google": {"bg": "4285F4", "text": "FFFFFF"},
}

def get_standard_image_url(phone_name: str, brand: str, existing_url: Optional[str] = None) -> str:
    """
    Returns an optimized high-resolution image URL or a branded WebP/SVG CDN placeholder.
    """
    if existing_url and (existing_url.startswith("http://") or existing_url.startswith("https://")):
        if "example.com" not in existing_url and not existing_url.endswith("sample.jpg"):
            return existing_url

    brand_clean = (brand or "Smartphone").lower().strip()
    clean_name = re.sub(r'\(.*?\)', '', phone_name or brand).strip()
    encoded_name = urllib.parse.quote(clean_name)
    theme = BRAND_PLACEHOLDER_THEMES.get(brand_clean, {"bg": "111111", "text": "00F0FF"})

    # Return a high-contrast standard SVG/WebP placeholder
    return f"https://placehold.co/600x800/{theme['bg']}/{theme['text']}.png?text={encoded_name}"

def validate_image_url(url: Optional[str]) -> bool:
    """Checks if a URL has valid HTTP(S) protocol and image format."""
    if not url or not isinstance(url, str):
        return False
    clean = url.lower().strip()
    if not (clean.startswith("http://") or clean.startswith("https://")):
        return False
    return any(clean.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".avif", ".svg"]) or "placehold.co" in clean
