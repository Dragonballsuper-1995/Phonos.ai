import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# GSMArena base URL
BASE_URL = "https://www.gsmarena.com/"

# Headers to mimic a real browser and avoid 403 Forbidden errors
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.gsmarena.com/"
}

# Brands popular in India (GSMArena brand URLs)
TARGET_BRANDS = [
    {"name": "Samsung", "url": "samsung-phones-9.php"},
    {"name": "Apple", "url": "apple-phones-48.php"},
    {"name": "Xiaomi", "url": "xiaomi-phones-80.php"},
    {"name": "vivo", "url": "vivo-phones-98.php"},
    {"name": "Oppo", "url": "oppo-phones-82.php"},
    {"name": "OnePlus", "url": "oneplus-phones-95.php"},
    {"name": "Realme", "url": "realme-phones-118.php"},
    {"name": "Motorola", "url": "motorola-phones-4.php"},
    {"name": "iQOO", "url": "iqoo-phones-123.php"},
    {"name": "Poco", "url": "poco-phones-120.php"}
]

def fetch_html(url):
    """Fetches HTML content with error handling and random delays."""
    try:
        # Random sleep to avoid getting banned
        time.sleep(random.uniform(1.5, 3.5))
        print(f"Fetching: {url}")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_phone_links_from_brand(brand_url, max_phones=30):
    """Gets a list of phone URLs from a brand's page."""
    html = fetch_html(BASE_URL + brand_url)
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    makers_div = soup.find('div', class_='makers')
    
    if not makers_div:
        print("Could not find 'makers' div. GSMArena might be blocking us or the page structure changed.")
        return []
        
    links = makers_div.find_all('a')
    phone_data = []
    
    for link in links[:max_phones]: # Get the top recent phones per brand
        phone_name = link.text.strip()
        phone_url = link.get('href')
        
        # Sometimes names are nested in elements, let's grab the img title if text is empty
        if not phone_name:
            img = link.find('img')
            if img and img.get('title'):
                phone_name = img.get('title')
                
        if phone_url:
            phone_data.append({
                "name": phone_name,
                "url": BASE_URL + phone_url
            })
            
    return phone_data

def scrape_phone_specs(phone_url):
    """Scrapes basic specs from a specific phone page."""
    html = fetch_html(phone_url)
    if not html:
        return {}
        
    soup = BeautifulSoup(html, 'html.parser')
    specs = {}
    
    # Example: Extracting basic info from the spec node
    try:
        # Title
        title_tag = soup.find('h1', class_='specs-phone-name-title')
        specs['Full_Name'] = title_tag.text.strip() if title_tag else "Unknown"
        
        # Price (often in a specific data attribute or quick spec box)
        price_tag = soup.find('td', {'data-spec': 'price'})
        specs['Price_Estimate'] = price_tag.text.strip() if price_tag else "N/A"
        
        # Quick specs (Battery, Camera, RAM) from the top summary boxes
        specs_summary = soup.find_all('span', class_='specs-brief-accent')
        if len(specs_summary) >= 3:
            specs['Screen_Size'] = specs_summary[0].text.strip()
            specs['Camera_Main'] = specs_summary[1].text.strip()
            specs['RAM'] = specs_summary[2].text.strip()
            specs['Battery'] = specs_summary[3].text.strip() if len(specs_summary) > 3 else "Unknown"
            
    except Exception as e:
        print(f"Error parsing specs for {phone_url}: {e}")
        
    return specs

def main():
    print("Starting GSMArena Scraper (Targeting 200-300 phones)...")
    all_phones = []
    
    # We want 200-300 phones total, so about 25-30 phones per brand (10 brands)
    for brand in TARGET_BRANDS:
        print(f"\n--- Scraping Brand: {brand['name']} ---")
        phone_links = get_phone_links_from_brand(brand['url'], max_phones=25)
        
        for phone in phone_links:
            print(f"Parsing specs for: {phone['name']}")
            specs = scrape_phone_specs(phone['url'])
            # Combine basic data with specs
            combined_data = {**{"Brand": brand['name'], "Model": phone['name'], "URL": phone['url']}, **specs}
            all_phones.append(combined_data)
            
    # Save to CSV
    if all_phones:
        df = pd.DataFrame(all_phones)
        df.to_csv('smartphone_specs.csv', index=False)
        print(f"\nSuccessfully saved {len(df)} phones to smartphone_specs.csv")
    else:
        print("\nNo phones scraped. Check anti-bot measures or selectors.")

if __name__ == "__main__":
    main()
