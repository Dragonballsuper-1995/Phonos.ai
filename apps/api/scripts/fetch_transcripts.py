# Placeholder for fetching YouTube transcripts
import argparse

def fetch_transcripts(video_id: str):
    print(f"Fetching transcript for video {video_id}...")
    # Implementation will use youtube-transcript-api
    print("Done. (Placeholder)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_id", required=True)
    args = parser.parse_args()
    fetch_transcripts(args.video_id)
