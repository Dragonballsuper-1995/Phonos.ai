import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os

# Ensure the punkt tokenizer is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Define Aspects and their associated keywords
ASPECTS = {
    "Camera": ["camera", "photo", "video", "lens", "zoom", "portrait", "selfie", "low light", "megapixel"],
    "Battery": ["battery", "charge", "charging", "mah", "screen on time", "endurance", "power"],
    "Performance": ["performance", "speed", "processor", "chip", "lag", "stutter", "gaming", "smooth", "snapdragon", "exynos"],
    "Display": ["display", "screen", "oled", "amoled", "lcd", "brightness", "refresh rate", "hz", "nits"],
    "Value": ["value", "price", "budget", "cost", "worth", "expensive", "cheap"]
}

def analyze_aspects(text, analyzer):
    """
    Splits text into sentences, identifies aspects, and calculates sentiment score.
    Returns a dictionary of aspects and their average sentiment score (-1 to 1).
    """
    if not isinstance(text, str):
        return {}
        
    sentences = sent_tokenize(text.lower())
    
    aspect_scores = {aspect: [] for aspect in ASPECTS.keys()}
    
    for sentence in sentences:
        # Check which aspects this sentence talks about
        matched_aspects = []
        for aspect, keywords in ASPECTS.items():
            if any(keyword in sentence for keyword in keywords):
                matched_aspects.append(aspect)
                
        # If it talks about any aspects, calculate sentiment
        if matched_aspects:
            sentiment_dict = analyzer.polarity_scores(sentence)
            compound_score = sentiment_dict['compound']
            
            for aspect in matched_aspects:
                aspect_scores[aspect].append(compound_score)
                
    # Average the scores for each aspect
    final_scores = {}
    for aspect, scores in aspect_scores.items():
        if scores:
            final_scores[aspect] = sum(scores) / len(scores)
        else:
            final_scores[aspect] = None # No mention of this aspect
            
    return final_scores

def main():
    if not os.path.exists('youtube_reviews.csv'):
        print("Error: youtube_reviews.csv not found. Please run youtube_fetcher.py first.")
        return
        
    print("Loading YouTube reviews...")
    df = pd.read_csv('youtube_reviews.csv')
    
    if df.empty:
        print("No reviews to process.")
        return
        
    analyzer = SentimentIntensityAnalyzer()
    print("Starting Aspect-Based Sentiment Analysis (ABSA)...")
    
    results = []
    
    for index, row in df.iterrows():
        phone_name = f"{row['Brand']} {row['Model']}"
        safe_phone_name = phone_name.encode('ascii', 'ignore').decode('ascii')
        safe_video_title = str(row['Video_Title']).encode('ascii', 'ignore').decode('ascii')
        print(f"Processing review for: {safe_phone_name} (Video: {safe_video_title})")
        
        scores = analyze_aspects(row['Transcript'], analyzer)
        
        # Combine base info with scores
        result_row = {
            'Brand': row['Brand'],
            'Model': row['Model'],
            'Video_ID': row['Video_ID']
        }
        result_row.update(scores)
        results.append(result_row)
        
    # Aggregate scores per phone model (average across multiple reviews)
    results_df = pd.DataFrame(results)
    
    # We want a summary table: Model -> Avg Camera Score, Avg Battery Score, etc.
    summary_df = results_df.groupby(['Brand', 'Model']).mean(numeric_only=True).reset_index()
    
    # Save the raw detailed scores and the summary
    results_df.to_csv('absa_detailed_scores.csv', index=False)
    summary_df.to_csv('absa_phone_summary.csv', index=False)
    
    print(f"\nSuccessfully analyzed {len(results_df)} reviews.")
    print("Saved detailed scores to absa_detailed_scores.csv")
    print("Saved aggregated phone summary to absa_phone_summary.csv")

if __name__ == "__main__":
    main()
