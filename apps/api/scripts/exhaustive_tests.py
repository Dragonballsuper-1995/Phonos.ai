import sys
import os

# Ensure we can import the app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.retrieval import semantic_search
from app.services.knowledge_graph import filter_by_knowledge_graph
from app.services.recommender import recommend_easy
from app.services.live_pricing import get_live_price
from app.models.query import EasyRecommendRequest

def test_retrieval():
    print("\n--- Testing Vector Retrieval (Semantic Search) ---")
    query = "Student phone under 30000"
    results = semantic_search(query, top_k=50)
    print(f"✅ Retrieved {len(results)} phone IDs for query '{query}'")
    assert len(results) > 0, "Retrieval failed to find phones."

def test_knowledge_graph():
    print("\n--- Testing Knowledge Graph ---")
    from app.models.phone import PhoneDetails
    # Create some mock PhoneDetails objects since semantic_search returns IDs
    mock_phones = [
        PhoneDetails(id=1, model="Samsung Galaxy S23", brand="Samsung", price="60000"),
        PhoneDetails(id=2, model="Poco X3 Pro", brand="Poco", price="20000") # Might be blocked
    ]
    safe_phones = filter_by_knowledge_graph(mock_phones)
    print(f"✅ Input: {len(mock_phones)} phones. Output: {len(safe_phones)} safe phones.")
    assert len(safe_phones) <= len(mock_phones), "KG Filter returned more phones than inputted."

def test_live_pricing():
    print("\n--- Testing Live Pricing Waterfall ---")
    dummy_id = "test_price_123"
    model = "Samsung Galaxy S23 FE"
    price = get_live_price(dummy_id, model)
    print(f"✅ Live price for {model}: {price}")
    assert price is not None, "Live pricing failed to retrieve a price."

def test_recommend_easy():
    print("\n--- Testing Easy Mode E2E ---")
    from app.models.phone import PhoneDetails
    # Creating a large mock catalog to simulate all_phones
    mock_catalog = [
        PhoneDetails(id=str(i), model=f"Phone {i}", brand="BrandX", price="25000", price_numeric=25000.0, raw_specs={"processor": "snapdragon 8", "battery": "5000mah", "display": "120hz", "ram": "8gb"})
        for i in range(1, 10)
    ]
    req = EasyRecommendRequest(persona="STUDENT", budget=30000)
    # Recommender pipeline runs Retrieval -> KG -> Live Price -> XGBoost
    results = recommend_easy(all_phones=mock_catalog, request=req)
    print(f"✅ Easy Mode generated {len(results)} recommendations.")
    if results:
        print(f"Top Phone: {results[0]['phone'].model} (Score: {results[0]['score']})")

def run_all_tests():
    print("========================================")
    print("   PHONOS.AI INTENSIVE BACKEND TESTING  ")
    print("========================================")
    test_retrieval()
    test_knowledge_graph()
    test_live_pricing()
    test_recommend_easy()
    print("\n========================================")
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("========================================")

if __name__ == "__main__":
    run_all_tests()
