"""
build_absa_scores.py
====================
Scales ABSA sentiment analysis to top phones in fone_master.db.
Writes scores directly into SQLite columns (absa_camera, absa_battery, etc.).

Usage:
  python scripts/build_absa_scores.py [--limit 50] [--overwrite] [--seed-only]
"""
import argparse
import os
import re
import sys
import time
import sqlite3
import requests
import pandas as pd
from typing import Dict, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/fone_master.db'))
YOUTUBE_KEY = os.getenv("YOUTUBE_API_KEY", "")
EXISTING_CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data_engine/youtube_reviews.csv'))
SUMMARY_CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data_engine/absa_phone_summary.csv'))

ASPECTS = {
    "camera": [
        "camera", "photo", "video", "lens", "zoom", "portrait", "selfie", "low light",
        "megapixel", "optic", "telephoto", "ois", "sensor", "dynamic range", "night mode", "hdr"
    ],
    "battery": [
        "battery", "charge", "charging", "mah", "screen on time", "endurance", "power",
        "backup", "drain", "sot", "fast charging", "watt", "adapter"
    ],
    "performance": [
        "performance", "speed", "processor", "chip", "chipset", "lag", "stutter", "gaming",
        "smooth", "snapdragon", "dimensity", "exynos", "heating", "thermal", "throttling", "fps", "bgmi"
    ],
    "display": [
        "display", "screen", "oled", "amoled", "lcd", "brightness", "refresh rate",
        "hz", "nits", "panel", "viewing angles", "bezels", "resolution"
    ],
    "build": [
        "build", "design", "feel", "weight", "grip", "premium", "plastic", "glass",
        "metal", "finish", "ergonomic", "ip68", "titanium", "durability"
    ],
}
ASPECT_COLS = list(ASPECTS.keys())

def migrate_absa_columns(conn: sqlite3.Connection):
    """Ensure ABSA columns exist in SQLite phones table."""
    for col in ASPECT_COLS:
        try:
            conn.execute(f"ALTER TABLE phones ADD COLUMN absa_{col} REAL")
        except Exception:
            pass
    try:
        conn.execute("ALTER TABLE phones ADD COLUMN absa_updated_at INTEGER")
    except Exception:
        pass
    conn.commit()
    print(f"[ABSA Migration] Verified columns: {['absa_' + c for c in ASPECT_COLS]}")

def search_youtube_api(query: str, max_results: int = 2) -> List[Dict[str, str]]:
    """Searches YouTube using YouTube Data API v3 or yt-dlp fallback."""
    videos = []
    if YOUTUBE_KEY:
        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": max_results,
                "key": YOUTUBE_KEY,
                "relevanceLanguage": "en"
            }
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("items", []):
                    vid_id = item.get("id", {}).get("videoId")
                    if vid_id:
                        videos.append({
                            "id": vid_id,
                            "title": item.get("snippet", {}).get("title", ""),
                            "uploader": item.get("snippet", {}).get("channelTitle", "")
                        })
                if videos:
                    return videos
        except Exception as e:
            print(f"  [API Warn] YouTube Data API lookup failed: {e}")

    # Fallback to yt-dlp
    try:
        ydl_opts = {'format': 'best', 'quiet': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            res = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            if 'entries' in res:
                for entry in res['entries']:
                    videos.append({
                        "id": entry['id'],
                        "title": entry.get('title', 'Review'),
                        "uploader": entry.get('uploader', 'Reviewer')
                    })
    except Exception as e:
        print(f"  [yt-dlp Warn] Search failed for '{query}': {e}")

    return videos

def get_transcript(video_id: str) -> Optional[str]:
    """Fetches transcript text for a given YouTube video ID."""
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id, languages=['en', 'en-IN', 'hi', 'hi-Latn'])
        full_text = " ".join([t.text for t in transcript_list])
        return full_text
    except Exception:
        return None

def analyze_transcript_aspects(text: str, analyzer: SentimentIntensityAnalyzer) -> Dict[str, float]:
    """Splits text into sentences and computes mean aspect sentiment using VADER."""
    sentences = re.split(r'[.!?\n]+', text)
    aspect_scores: Dict[str, List[float]] = {aspect: [] for aspect in ASPECTS}

    for sent in sentences:
        sent_clean = sent.strip().lower()
        if len(sent_clean) < 10:
            continue
        vader_res = analyzer.polarity_scores(sent_clean)
        compound = vader_res["compound"]

        for aspect, keywords in ASPECTS.items():
            if any(kw in sent_clean for kw in keywords):
                aspect_scores[aspect].append(compound)

    results = {}
    for aspect, scores in aspect_scores.items():
        if scores:
            results[aspect] = round(float(sum(scores) / len(scores)), 4)
        else:
            results[aspect] = 0.0
    return results

def seed_existing_reviews(conn: sqlite3.Connection, analyzer: SentimentIntensityAnalyzer):
    """Seed sentiment from existing transcripts in data_engine."""
    if not os.path.exists(EXISTING_CSV_PATH):
        return 0

    print("[ABSA Seed] Processing existing YouTube reviews archive...")
    df = pd.read_csv(EXISTING_CSV_PATH)
    phone_grouped = df.groupby(["Brand", "Model"])
    seeded = 0

    for (brand, model), group in phone_grouped:
        combined_text = " ".join([str(t) for t in group["Transcript"].dropna()])
        if not combined_text:
            continue
        scores = analyze_transcript_aspects(combined_text, analyzer)
        now_ts = int(time.time())

        # Update in DB where name matches brand + model
        phone_name_pattern = f"%{model}%"
        conn.execute(
            "UPDATE phones SET absa_camera = ?, absa_battery = ?, absa_performance = ?, "
            "absa_display = ?, absa_build = ?, absa_updated_at = ? "
            "WHERE name LIKE ? OR (brand LIKE ? AND name LIKE ?)",
            (
                scores["camera"], scores["battery"], scores["performance"],
                scores["display"], scores["build"], now_ts,
                phone_name_pattern, f"%{brand}%", phone_name_pattern
            )
        )
        seeded += 1

    conn.commit()
    print(f"[ABSA Seed] Successfully seeded sentiment for {seeded} phone models from archive.")
    return seeded

def main():
    parser = argparse.ArgumentParser(description="Build ABSA aspect sentiment scores.")
    parser.add_argument("--limit", type=int, default=30, help="Max number of phones to process live.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing recent scores.")
    parser.add_argument("--seed-only", action="store_true", help="Only process existing review files.")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.row_factory = sqlite3.Row
    migrate_absa_columns(conn)

    analyzer = SentimentIntensityAnalyzer()

    # Step 1: Seed from existing CSV archives
    seed_existing_reviews(conn, analyzer)
    if args.seed_only:
        conn.close()
        print("[ABSA] Seed-only run complete.")
        return

    # Step 2: Fetch and score top phones
    print(f"[ABSA] Fetching target phones for live review processing (Limit: {args.limit})...")
    where_clause = "WHERE released_in_india = 1"
    if not args.overwrite:
        where_clause += " AND (absa_updated_at IS NULL OR absa_camera IS NULL)"

    query = (
        f"SELECT rowid AS id, brand, name, launch_year FROM phones "
        f"{where_clause} "
        f"ORDER BY is_current_catalogue DESC, launch_year DESC, price_numeric DESC "
        f"LIMIT {args.limit}"
    )
    target_phones = conn.execute(query).fetchall()
    print(f"[ABSA] Found {len(target_phones)} candidate phones to analyze.")

    processed = 0
    for row in target_phones:
        phone_id = row["id"]
        brand = row["brand"]
        name = row["name"]
        search_query = f"{brand} {name} review India Geekyranjit OR TechWiser OR Trakin Tech"

        print(f"\n[{processed + 1}/{len(target_phones)}] Searching reviews for: {name}...")
        videos = search_youtube_api(search_query, max_results=2)
        transcripts = []

        for v in videos:
            t = get_transcript(v["id"])
            if t:
                transcripts.append(t)
            time.sleep(0.5)

        if transcripts:
            combined_t = " ".join(transcripts)
            scores = analyze_transcript_aspects(combined_t, analyzer)
            now_ts = int(time.time())
            conn.execute(
                "UPDATE phones SET absa_camera = ?, absa_battery = ?, absa_performance = ?, "
                "absa_display = ?, absa_build = ?, absa_updated_at = ? "
                "WHERE rowid = ?",
                (
                    scores["camera"], scores["battery"], scores["performance"],
                    scores["display"], scores["build"], now_ts, phone_id
                )
            )
            conn.commit()
            print(f"  ✅ Updated ABSA for {name}: {scores}")
            processed += 1
        else:
            print(f"  ℹ️ No transcripts found for {name}.")

    conn.close()
    print(f"\n[ABSA] Finished! Processed {processed} phones.")

if __name__ == "__main__":
    main()
