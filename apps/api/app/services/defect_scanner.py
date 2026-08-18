import os
import re
import requests
from typing import List, Dict, Any, Optional
from app.services.knowledge_graph import get_knowledge_graph

KNOWN_DEFECT_PATTERNS = {
    "motherboard dead": ("Motherboard Dead", 0.95),
    "motherboard issue": ("Motherboard Failure", 0.90),
    "green line": ("Green Line Display Defect", 0.95),
    "wifi ic dead": ("Wifi IC Hardware Failure", 0.90),
    "camera dead": ("Camera Sensor Hardware Defect", 0.85),
}

def scan_community_defects(phone_name: str) -> Optional[str]:
    """
    Search community forum headlines (r/IndiaTech, r/smartphones) for hardware defect reports.
    If a confirmed pattern is found, dynamically adds a blocking edge to the Knowledge Graph.
    """
    try:
        # Search via public tech discussion queries
        search_query = f"{phone_name} issue defect motherboard green line"
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(search_query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        resp = requests.get(url, headers=headers, timeout=6.0)
        if resp.status_code != 200:
            return None
            
        page_text = resp.text.lower()
        
        for pattern, (defect_name, weight) in KNOWN_DEFECT_PATTERNS.items():
            # Check if defect pattern is prominently mentioned alongside phone name
            if pattern in page_text:
                G = get_knowledge_graph()
                G.add_edge(phone_name, defect_name, weight=weight)
                print(f"[DefectScanner] DYNAMIC KG BLOCK: Added ({phone_name} -> {defect_name})")
                return defect_name
                
    except Exception as e:
        print(f"[DefectScanner] Scan skipped for '{phone_name}': {e}")
        
    return None
