import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import os
import time

def search_youtube_videos(query, max_results=3):
    """Searches YouTube and returns a list of video IDs."""
    print(f"Searching YouTube for: '{query}'")
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': False,
    }
    video_ids = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ytsearch prefix tells yt-dlp to search youtube
            result = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            if 'entries' in result:
                for entry in result['entries']:
                    video_ids.append({
                        'id': entry['id'],
                        'title': entry.get('title', 'Unknown Title'),
                        'uploader': entry.get('uploader', 'Unknown Uploader')
                    })
    except Exception as e:
        print(f"Error searching YouTube for {query}: {e}")
    return video_ids

def get_transcript(video_id):
    """Fetches transcript for a given video ID."""
    try:
        # Get transcript (prefers English or auto-generated English/Hindi)
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=['en', 'hi', 'en-IN'])
        # Combine text
        full_text = " ".join([t.text for t in transcript])
        return full_text
    except Exception as e:
        print(f"  Could not fetch transcript for {video_id}: {e}")
        return None

def main():
    if not os.path.exists('smartphone_specs.csv'):
        print("smartphone_specs.csv not found. Please run gsmarena_scraper.py first.")
        return

    df = pd.read_csv('smartphone_specs.csv')
    print(f"Loaded {len(df)} phones from database.")
    
    # We don't want to hit YouTube for 300 phones all at once right now (rate limits),
    # so we will process the first 5 for testing. You can remove the limit later.
    test_df = df.head(5)
    
    reviews_data = []

    for index, row in test_df.iterrows():
        phone_name = f"{row['Brand']} {row['Model']}"
        # Targeting Indian reviewers
        query = f"{phone_name} review Geekyranjit OR Tech Burner OR Trakin Tech"
        
        videos = search_youtube_videos(query, max_results=2)
        
        for video in videos:
            safe_title = video['title'].encode('ascii', 'ignore').decode('ascii')
            safe_uploader = video['uploader'].encode('ascii', 'ignore').decode('ascii')
            print(f"  Fetching transcript for video: {safe_title} by {safe_uploader}")
            transcript_text = get_transcript(video['id'])
            
            if transcript_text:
                reviews_data.append({
                    'Brand': row['Brand'],
                    'Model': row['Model'],
                    'Video_ID': video['id'],
                    'Uploader': video['uploader'],
                    'Video_Title': video['title'],
                    'Transcript': transcript_text[:1000] + "..." # Storing first 1000 chars for demo
                })
            time.sleep(2) # Be polite to APIs
            
    if reviews_data:
        reviews_df = pd.DataFrame(reviews_data)
        reviews_df.to_csv('youtube_reviews.csv', index=False)
        print(f"\nSuccessfully saved {len(reviews_df)} reviews to youtube_reviews.csv")
    else:
        print("\nNo reviews fetched.")

if __name__ == "__main__":
    main()
