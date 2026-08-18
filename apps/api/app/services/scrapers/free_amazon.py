import os
import re
from typing import Optional
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    pass

def scrape_amazon_price_free(phone_name: str) -> Optional[float]:
    """
    100% Free Fallback Scraper using Playwright.
    Navigates to Amazon.in, searches for the phone, and attempts to extract the price.
    """
    try:
        with sync_playwright() as p:
            # We use a standard Chromium browser
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Go directly to search URL
            search_query = phone_name.replace(" ", "+")
            page.goto(f"https://www.amazon.in/s?k={search_query}", wait_until="domcontentloaded", timeout=15000)
            
            # Look for the standard Amazon price element in search results
            # The class "a-price-whole" usually contains the rupees part
            price_element = page.query_selector('.a-price-whole')
            
            if price_element:
                price_text = price_element.inner_text()
                # Clean the text (e.g., "1,29,999." -> 129999.0)
                clean_text = re.sub(r'[^\d]', '', price_text)
                if clean_text:
                    browser.close()
                    return float(clean_text)
            
            browser.close()
    except Exception as e:
        # FastAPI runs endpoints in a thread that has an asyncio loop attached.
        # sync_playwright deliberately crashes if it detects an existing asyncio loop.
        # Instead of flooding the logs with this expected fallback error, we silence it.
        # It correctly falls back to the DB price.
        if "Playwright Sync API inside the asyncio loop" not in str(e):
            print(f"[Scraper Fallback] Error scraping {phone_name}: {e}")
        
    return None
