import os
import sys

# Add parent directory to path so we can import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.live_pricing import get_live_price, init_db

def test_waterfall():
    print("Initializing pricing cache DB...")
    init_db()
    
    # We use a dummy ID to force a cache miss on first run
    dummy_id = "test_phone_123"
    test_phone = "Samsung Galaxy S23 Ultra"
    
    print(f"Testing Live Price Waterfall for '{test_phone}'...")
    price = get_live_price(dummy_id, test_phone)
    
    if price:
        print(f"SUCCESS! Retrieved price: ₹{price}")
    else:
        print("FAILED to retrieve price via any API or fallback.")
        
if __name__ == "__main__":
    test_waterfall()
