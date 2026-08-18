import os
import re
import sqlite3
import pandas as pd
from typing import Dict, Any, Optional
from app.core.config import settings

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/absa_phone_summary.csv'))

# In-memory fast cache
_absa_cache: Dict[str, Dict[str, float]] = {}

def load_cached_absa():
    """Load existing sentiment scores from CSV."""
    global _absa_cache
    if not _absa_cache and os.path.exists(CSV_PATH):
        try:
            df = pd.read_csv(CSV_PATH)
            for _, row in df.iterrows():
                model = str(row.get("model", "")).strip().lower()
                if model:
                    _absa_cache[model] = {
                        "camera": float(row.get("camera", 0.0)),
                        "battery": float(row.get("battery", 0.0)),
                        "performance": float(row.get("performance", 0.0)),
                        "display": float(row.get("display", 0.0)),
                    }
        except Exception as e:
            print(f"[YouTubeABSA] Error loading cached ABSA: {e}")

def get_youtube_client():
    if not settings.YOUTUBE_API_KEY:
        return None
    try:
        from googleapiclient.discovery import build
        return build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
    except Exception as e:
        print(f"[YouTubeABSA] Failed to initialize YouTube client: {e}")
        return None

def analyze_review_sentiment(texts: list) -> Dict[str, float]:
    """Calculate aspect sentiment scores across video titles, descriptions, and comments."""
    aspects = {"camera": 0.0, "battery": 0.0, "performance": 0.0, "display": 0.0}
    counts = {"camera": 0, "battery": 0, "performance": 0, "display": 0}
    
    positives = {'good', 'great', 'awesome', 'excellent', 'amazing', 'best', 'fast', 'smooth', 'flagship', 'crisp', 'bright'}
    negatives = {'bad', 'poor', 'terrible', 'worst', 'slow', 'heating', 'drain', 'lag', 'stutter', 'throttling', 'dim', 'buggy'}
    
    for text in texts:
        t = str(text).lower()
        words = set(re.findall(r'\b\w+\b', t))
        score = len(words.intersection(positives)) - len(words.intersection(negatives))
        
        for aspect in aspects.keys():
            if aspect in t or (aspect == "performance" and ("game" in t or "fps" in t or "chipset" in t)):
                aspects[aspect] += score
                counts[aspect] += 1
                
    final_scores = {}
    for aspect in aspects.keys():
        if counts[aspect] > 0:
            final_scores[aspect] = round(max(-1.0, min(1.0, aspects[aspect] / (counts[aspect] * 2))), 2)
        else:
            final_scores[aspect] = 0.0
            
    return final_scores

_youtube_quota_exceeded = False

def fetch_live_sentiment(phone_name: str) -> Dict[str, float]:
    """
    Fetches live sentiment scores for a phone, checking CSV cache first,
    then falling back to YouTube Data API + sentiment analysis.
    """
    global _youtube_quota_exceeded, _absa_cache
    load_cached_absa()
    key = phone_name.lower().strip()
    if key in _absa_cache:
        return _absa_cache[key]
        
    for cached_k, scores in _absa_cache.items():
        if cached_k in key or key in cached_k:
            return scores
        
    if _youtube_quota_exceeded:
        return {"camera": 0.0, "battery": 0.0, "performance": 0.0, "display": 0.0}
        
    youtube = get_youtube_client()
    if not youtube:
        return {"camera": 0.0, "battery": 0.0, "performance": 0.0, "display": 0.0}
        
    try:
        req = youtube.search().list(
            q=f"{phone_name} review India",
            part='snippet',
            maxResults=3,
            type='video'
        )
        res = req.execute()
        
        snippets = []
        for item in res.get("items", []):
            snippets.append(item.get("snippet", {}).get("title", ""))
            snippets.append(item.get("snippet", {}).get("description", ""))
            
        scores = analyze_review_sentiment(snippets)
        _absa_cache[key] = scores
        
        # Save to CSV
        try:
            row_df = pd.DataFrame([{
                "model": phone_name,
                "camera": scores["camera"],
                "battery": scores["battery"],
                "performance": scores["performance"],
                "display": scores["display"]
            }])
            if os.path.exists(CSV_PATH):
                row_df.to_csv(CSV_PATH, mode='a', header=False, index=False)
            else:
                row_df.to_csv(CSV_PATH, index=False)
        except Exception as e:
            pass
            
        return scores
    except Exception as e:
        if "quota" in str(e).lower() or "429" in str(e):
            _youtube_quota_exceeded = True
        scores = {"camera": 0.0, "battery": 0.0, "performance": 0.0, "display": 0.0}
        _absa_cache[key] = scores
        return scores
