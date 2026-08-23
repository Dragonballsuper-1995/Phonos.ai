import os
try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    chromadb = None
    embedding_functions = None

CHROMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/chroma_db'))

# Initialize client globally (singleton)
_client = None
_collection = None

def get_chroma_collection():
    global _client, _collection
    if _client is None:
        if not os.path.exists(CHROMA_PATH):
            raise FileNotFoundError(f"ChromaDB not found at {CHROMA_PATH}. Run build_vector_db.py first.")
        
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        _collection = _client.get_collection(name="phones_collection", embedding_function=sentence_transformer_ef)
    return _collection

def semantic_search(query: str, top_k: int = 50) -> list:
    """
    Search for phones semantically matching the user query.
    Returns a list of phone IDs.
    """
    try:
        try:
            collection = get_chroma_collection()
        except FileNotFoundError:
            print("[Retrieval] Warning: ChromaDB not built. Returning empty.")
            return []
            
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        if not results['ids'] or not results['ids'][0]:
            return []
            
        return results['ids'][0]
    except Exception as e:
        print(f"[Retrieval] Error querying ChromaDB: {e}. Returning empty.")
        return []
