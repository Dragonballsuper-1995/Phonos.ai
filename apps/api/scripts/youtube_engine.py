import os
import sqlite3
import pandas as pd
from googleapiclient.discovery import build
import json
import time

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/fone_master.db'))
CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/absa_phone_summary.csv'))

def get_youtube_client():
    return build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def fetch_top_video_comments(phone_name: str, max_comments=50):
    """
    Search YouTube for phone reviews and fetch top comments to analyze sentiment.
    """
    youtube = get_youtube_client()
    try:
        print(f"[YouTubeEngine] Searching for: {phone_name} review")
        search_response = youtube.search().list(
            q=f"{phone_name} review",
            part='id',
            maxResults=1,
            type='video'
        ).execute()

        if not search_response.get('items'):
            return []

        video_id = search_response['items'][0]['id']['videoId']
        print(f"[YouTubeEngine] Found video ID: {video_id}")

        comments_response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=max_comments,
            order='relevance'
        ).execute()

        comments = []
        for item in comments_response.get('items', []):
            text = item['snippet']['topLevelComment']['snippet']['textOriginal']
            comments.append(text)
            
        return comments
    except Exception as e:
        print(f"[YouTubeEngine] Error fetching YouTube data: {e}")
        return []

def run_mock_absa(comments):
    """
    Mock Aspect-Based Sentiment Analysis.
    In a real pipeline, this uses HuggingFace Transformers (e.g., PyABSA).
    For the MVP, we run a simple keyword-based sentiment heuristic.
    """
    aspects = {"camera": 0.0, "battery": 0.0, "performance": 0.0, "display": 0.0}
    counts = {"camera": 0, "battery": 0, "performance": 0, "display": 0}
    
    positive_words = ['good', 'great', 'awesome', 'excellent', 'amazing', 'best', 'fast', 'smooth']
    negative_words = ['bad', 'poor', 'terrible', 'worst', 'slow', 'heating', 'drain', 'lag']
    
    for text in comments:
        t = text.lower()
        score = 0
        if any(w in t for w in positive_words): score += 1
        if any(w in t for w in negative_words): score -= 1
            
        for aspect in aspects.keys():
            if aspect in t:
                aspects[aspect] += score
                counts[aspect] += 1
                
    # Average the scores
    final_scores = {}
    for aspect in aspects.keys():
        if counts[aspect] > 0:
            final_scores[aspect] = max(-1.0, min(1.0, aspects[aspect] / counts[aspect]))
        else:
            final_scores[aspect] = 0.0
            
    return final_scores

def main():
    print("=== Phonos.ai YouTube Data Engine ===")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM phones WHERE released_in_india=1 LIMIT 10")
    phones = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    results = []
    
    for phone in phones:
        comments = fetch_top_video_comments(phone)
        if comments:
            scores = run_mock_absa(comments)
            scores['model'] = phone
            results.append(scores)
            print(f" -> ABSA Scores for {phone}: {scores}")
            
        # Sleep to avoid hitting YouTube API rate limits immediately
        time.sleep(1)
        
    if results:
        df = pd.DataFrame(results)
        # Reorder columns
        cols = ['model', 'camera', 'battery', 'performance', 'display']
        # If the file exists, append, else create
        if os.path.exists(CSV_PATH):
            df.to_csv(CSV_PATH, mode='a', header=False, index=False, columns=cols)
        else:
            df.to_csv(CSV_PATH, index=False, columns=cols)
        print(f"Successfully appended {len(results)} new sentiment records to absa_phone_summary.csv")
    else:
        print("No results processed.")

if __name__ == "__main__":
    main()
