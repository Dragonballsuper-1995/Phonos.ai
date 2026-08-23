"""
hardware_similarity.py — Hardware-Space Nearest-Neighbour Search
================================================================
Loads pre-normalised hardware_vector BLOBs from SQLite into a NumPy matrix.
Since all vectors are L2-normalised at storage time, dot product == cosine similarity.

The full-catalogue matrix is cached in-process and only rebuilt when phonos_ai.db
changes on disk (file mtime check).
"""
import os
import sqlite3
import numpy as np
from typing import List, Dict, Any, Optional

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../data/phonos_ai.db')
)

# ── In-process cache ─────────────────────────────────────────────────────────
_cache: Dict[str, Any] = {"matrix": None, "names": None, "brands": None, "ids": None, "prices": None, "mtime": 0.0}

def _load_matrix(max_budget: Optional[float] = None):
    current_mtime = os.path.getmtime(DB_PATH) if os.path.exists(DB_PATH) else 0.0

    # Build or refresh full cache if needed
    if _cache["matrix"] is None or current_mtime != _cache["mtime"]:
        sql = (
            "SELECT rowid, name, brand, price_numeric, hardware_vector FROM phones "
            "WHERE hardware_vector IS NOT NULL AND is_current_catalogue = 1 "
            "AND released_in_india = 1"
        )
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        rows = conn.execute(sql).fetchall()
        conn.close()

        if not rows:
            return [], [], [], [], None

        names, brands, ids, prices, vecs = [], [], [], [], []
        for rid, name, brand, price, blob in rows:
            if blob:
                v = np.frombuffer(blob, dtype=np.float32).copy()
                if v.shape[0] == 5:
                    names.append(name)
                    brands.append(brand or "")
                    ids.append(rid)
                    prices.append(price or 0.0)
                    vecs.append(v)

        if not vecs:
            return [], [], [], [], None

        matrix = np.vstack(vecs)
        prices_arr = np.array(prices, dtype=np.float32)
        _cache.update(matrix=matrix, names=names, brands=brands, ids=ids, prices=prices, prices_arr=prices_arr, mtime=current_mtime)

    names, brands, ids, prices, matrix = _cache["names"], _cache["brands"], _cache["ids"], _cache["prices"], _cache["matrix"]

    if max_budget is not None and matrix is not None:
        threshold = max_budget * 1.05
        prices_arr = _cache["prices_arr"]
        valid_mask = prices_arr <= threshold
        if not np.any(valid_mask):
            return [], [], [], [], None
        indices = np.where(valid_mask)[0]
        return [names[i] for i in indices], [brands[i] for i in indices], [ids[i] for i in indices], [prices[i] for i in indices], matrix[indices]

    return names, brands, ids, prices, matrix


def find_similar_phones(
    query_vector: np.ndarray,
    top_k: int = 10,
    max_budget: Optional[float] = None,
    exclude_ids: Optional[List[int]] = None,
) -> List[Dict[str, Any]]:
    """
    Returns top_k phones closest to query_vector in hardware-spec space.
    query_vector must be float32 (5,) — L2-normalised for correct cosine similarity.
    """
    names, brands, ids, prices, matrix = _load_matrix(max_budget)
    if matrix is None or len(names) == 0:
        return []

    norm = np.linalg.norm(query_vector)
    q = query_vector / norm if norm > 0 else query_vector
    sims = np.dot(matrix, q)                  # cosine similarity for each phone

    exclude = set(exclude_ids or [])
    results = []
    for idx in np.argsort(sims)[::-1]:
        if ids[idx] in exclude:
            continue
        results.append({
            "id": int(ids[idx]),
            "name": names[idx],
            "brand": brands[idx],
            "price": float(prices[idx]),
            "similarity_score": round(float(sims[idx]), 4),
        })
        if len(results) == top_k:
            break
    return results


def build_persona_query_vector(persona_weights: Dict[str, float]) -> np.ndarray:
    """
    Maps a persona weight dict to a 5-dim hardware query vector.
    Dimension order matches HW_VECTOR_DIM_ORDER in hardware_scorer.py:
      [soc, camera, display, battery, build]
    Persona weight keys: performance → soc, camera, display, battery, build.
    """
    raw = np.array([
        persona_weights.get("performance", 0.2),  # → soc
        persona_weights.get("camera", 0.2),
        persona_weights.get("display", 0.15),
        persona_weights.get("battery", 0.2),
        persona_weights.get("build", 0.1),
    ], dtype=np.float32)
    norm = np.linalg.norm(raw)
    return raw / norm if norm > 0 else raw
