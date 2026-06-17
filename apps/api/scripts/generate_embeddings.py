import os
import sys
import asyncio
from sentence_transformers import SentenceTransformer

# Ensure we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db.database import get_db_pool, close_db_pool

async def generate_all_embeddings():
    pool = await get_db_pool()
    
    # Fetch all phones that lack embeddings or fetch all if you want to overwrite
    phones = await pool.fetch("SELECT id, brand, model, full_name, price_inr, display_size, chipset, battery_mah FROM phones WHERE embedding IS NULL")
    
    if not phones:
        print("No phones need embeddings updated.")
        await close_db_pool()
        return
        
    print(f"Generating embeddings for {len(phones)} phones...")
    
    # Load model
    print("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    for phone in phones:
        # Create a combined text representation
        text_parts = [
            f"Brand: {phone['brand']}",
            f"Model: {phone['model']}",
            f"Name: {phone['full_name']}",
        ]
        if phone['price_inr']:
            text_parts.append(f"Price: ₹{phone['price_inr']}")
        if phone['display_size']:
            text_parts.append(f"Display: {phone['display_size']} inches")
        if phone['chipset']:
            text_parts.append(f"Chipset: {phone['chipset']}")
        if phone['battery_mah']:
            text_parts.append(f"Battery: {phone['battery_mah']} mAh")
            
        combined_text = ". ".join(text_parts)
        
        # Generate embedding
        embedding = model.encode(combined_text).tolist()
        
        # Update database
        # Convert list of floats to pgvector string format '[v1, v2, ...]'
        vector_str = f"[{','.join(str(x) for x in embedding)}]"
        
        try:
            await pool.execute(
                "UPDATE phones SET embedding = $1 WHERE id = $2",
                vector_str, phone['id']
            )
            print(f"Updated embedding for {phone['full_name']}")
        except Exception as e:
            print(f"Error updating embedding for {phone['full_name']}: {e}")
        
    await close_db_pool()
    print("Finished generating embeddings.")

if __name__ == "__main__":
    asyncio.run(generate_all_embeddings())
