import json
import re
import os

# Configure input/output paths relative to this script
SCRIPT_DIR  = os.path.dirname(__file__)
INPUT_JSON  = os.path.join(SCRIPT_DIR, "insurance_pdfs_data.json")
OUTPUT_JSON = os.path.join(SCRIPT_DIR, "insurance_pdfs_chunks.json")

# Chunking parameters
CHUNK_SIZE    = 250  # target words per chunk
CHUNK_OVERLAP = 50   # overlap words between chunks

def clean_text(text: str) -> str:
    """
    Remove page-number artifacts, stray URLs, and normalize whitespace.
    """
    # Remove '1 of 6', '2 of 6', etc.
    text = re.sub(r'\b\d+\s+of\s+\d+\b', ' ', text)
    # Remove footnote URLs like 'www.something.com'
    text = re.sub(r'www\.\S+', ' ', text)
    # Collapse any run of whitespace/newlines into single spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    Split cleaned text into word-based chunks with overlap.
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end == len(words):
            break
        start += chunk_size - overlap

    return chunks

def main():
    # Check input JSON exists
    if not os.path.exists(INPUT_JSON):
        print(f"ERROR: Input file not found: {INPUT_JSON}")
        return

    # Load extracted PDF data
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        pdf_docs = json.load(f)

    all_chunks = []

    # Process each PDF document
    for doc in pdf_docs:
        raw = doc.get('content', '')
        cleaned = clean_text(raw)
        passages = chunk_text(cleaned, CHUNK_SIZE, CHUNK_OVERLAP)

        for idx, passage in enumerate(passages):
            all_chunks.append({
                "source_file": doc.get('filename', ''),
                "chunk_index": idx,
                "text": passage
            })

    # Write out the chunked data
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"Created {len(all_chunks)} chunks in {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
