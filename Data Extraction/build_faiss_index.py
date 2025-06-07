import json
import os
import faiss
from sentence_transformers import SentenceTransformer

# Paths
SCRIPT_DIR        = os.path.dirname(__file__)
CHUNKS_JSON       = os.path.join(SCRIPT_DIR, "insurance_pdfs_chunks.json")
FAISS_INDEX_PATH  = os.path.join(SCRIPT_DIR, "faiss_index.bin")
METADATA_PATH     = os.path.join(SCRIPT_DIR, "faiss_metadata.json")

# Model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # small & performant

def main():
    # 1. Load your chunks
    with open(CHUNKS_JSON, 'r', encoding='utf-8') as f:
        chunks = json.load(f)

    texts = [chunk["text"] for chunk in chunks]

    # 2. Generate embeddings
    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    # 3. Build FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)       # L2 (Euclidean) distance
    index.add(embeddings)                # add all vectors

    # 4. Save index & metadata
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(METADATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"Built FAISS index with {index.ntotal} vectors")
    print(f"Index saved to {FAISS_INDEX_PATH}")
    print(f"Metadata saved to {METADATA_PATH}")

if __name__ == "__main__":
    main()
