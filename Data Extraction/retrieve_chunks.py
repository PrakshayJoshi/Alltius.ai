import os
import json
import faiss
from sentence_transformers import SentenceTransformer

# Paths (adjust if needed)
SCRIPT_DIR       = os.path.dirname(__file__)
INDEX_PATH       = os.path.join(SCRIPT_DIR, "faiss_index.bin")
METADATA_PATH    = os.path.join(SCRIPT_DIR, "faiss_metadata.json")

# Same model you used when building the index
EMBEDDING_MODEL  = "all-MiniLM-L6-v2"

def load_resources():
    """Load FAISS index, metadata, and embedding model."""
    # 1. Load index
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(f"FAISS index not found at {INDEX_PATH}")
    index = faiss.read_index(INDEX_PATH)

    # 2. Load metadata (list of chunk dicts)
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # 3. Load embedding model
    model = SentenceTransformer(EMBEDDING_MODEL)
    return index, metadata, model

def retrieve(query: str, top_k: int = 5):
    """
    Given an input query, return the top_k most relevant chunks.
    """
    index, metadata, model = load_resources()

    # 1. Embed the query
    q_vector = model.encode([query], convert_to_numpy=True)

    # 2. Search in FAISS
    distances, indices = index.search(q_vector, top_k)

    # 3. Gather results
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        chunk = metadata[idx]
        results.append({
            "source_file": chunk["source_file"],
            "chunk_index": chunk["chunk_index"],
            "distance": float(dist),
            "text": chunk["text"]
        })
    return results

if __name__ == "__main__":
    # Example usage
    question = input("Enter your question: ")
    top_k = 5
    hits = retrieve(question, top_k)
    
    if not hits or hits[0]["distance"] > 1.0:
        # threshold can be tuned; here 1.0 is an example
        print("I don't know")
    else:
        for i, hit in enumerate(hits, start=1):
            print(f"\n[{i}] (dist: {hit['distance']:.4f}) from {hit['source_file']} (chunk {hit['chunk_index']}):\n")
            print(hit["text"][:500] + ("..." if len(hit["text"])>500 else ""))
