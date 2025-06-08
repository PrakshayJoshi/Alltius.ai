import json
import re
import os

SCRIPT_DIR  = os.path.dirname(__file__)
INPUT_JSON  = os.path.join(SCRIPT_DIR, "insurance_pdfs_data.json")
QA_JSON     = os.path.join(SCRIPT_DIR, "angelone_qas.json")
OUTPUT_JSON = os.path.join(SCRIPT_DIR, "insurance_pdfs_chunks.json")

CHUNK_SIZE    = 250  # target words per chunk
CHUNK_OVERLAP = 50   # overlap words between chunks

def clean_text(text: str) -> str:
    text = re.sub(r'\b\d+\s+of\s+\d+\b', ' ', text)
    text = re.sub(r'www\.\S+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
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
    all_chunks = []

    if not os.path.exists(INPUT_JSON):
        print(f"ERROR: Input file not found: {INPUT_JSON}")
        return

    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        pdf_docs = json.load(f)

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

    if os.path.exists(QA_JSON):
        with open(QA_JSON, 'r', encoding='utf-8') as f:
            qas = json.load(f)

        start_idx = len(all_chunks)
        for i, qa in enumerate(qas):
            question = qa.get('question', '').strip()
            answer = qa.get('answer', '').strip()
            if question and answer:
                all_chunks.append({
                    "source_file": "angelone_qas.json",
                    "chunk_index": start_idx + i,
                    "text": f"Q: {question}\nA: {answer}"
                })

    # Save combined chunks
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"Created {len(all_chunks)} chunks in {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
