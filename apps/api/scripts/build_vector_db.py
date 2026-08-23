import sqlite3
import json
import os
import chromadb
from chromadb.utils import embedding_functions

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/phonos_ai.db'))
CHROMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/chroma_db'))

def build_rich_text(row):
    """
    Converts a phone DB row into a rich semantic text document for embedding.
    """
    # row: (rowid, name, brand, price, raw_specs)
    phone_id = str(row[0])
    model = row[1]
    brand = row[2]
    price = row[3]
    raw_html = row[4]
    
    import re
    clean_specs = re.sub(r'<[^>]+>', ' ', str(raw_html) if raw_html else '')
    clean_specs = re.sub(r'\s+', ' ', clean_specs).strip()
    
    doc = f"Brand: {brand}. Model: {model}. Price: {price}. Specifications and details: {clean_specs}"
    
    metadata = {
        "id": phone_id,
        "brand": brand,
        "model": model,
        "price": price if price else ""
    }
    
    return phone_id, doc, metadata

def main():
    print("Loading phones from SQLite...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, name, brand, price, raw_specs FROM phones WHERE released_in_india=1")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No phones found in database!")
        return

    print(f"Loaded {len(rows)} phones.")
    
    os.makedirs(CHROMA_PATH, exist_ok=True)
    
    print(f"Initializing ChromaDB at {CHROMA_PATH}...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    collection = client.get_or_create_collection(
        name="phones_collection",
        embedding_function=sentence_transformer_ef
    )
    
    ids = []
    documents = []
    metadatas = []
    
    print("Building semantic documents...")
    for row in rows:
        p_id, doc, meta = build_rich_text(row)
        ids.append(p_id)
        documents.append(doc)
        metadatas.append(meta)
        
    print("Embedding and inserting into Vector DB (this may take a few minutes)...")
    
    batch_size = 500
    for i in range(0, len(ids), batch_size):
        end = min(i + batch_size, len(ids))
        print(f"Inserting batch {i} to {end}...")
        collection.upsert(
            ids=ids[i:end],
            documents=documents[i:end],
            metadatas=metadatas[i:end]
        )
        
    print(f"Successfully embedded {len(ids)} phones into the Vector DB.")
    
if __name__ == "__main__":
    main()
