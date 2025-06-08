# rag_chatbot_gemini.py
import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "faiss_index.bin")
META_PATH = os.path.join(BASE_DIR, "faiss_metadata.json")


_index = None
_metadata = None
_model = None


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("[ERROR] GEMINI_API_KEY not set in environment variables.")

GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
HEADERS = { "Content-Type": "application/json" }


def load_resources():
    global _index, _metadata, _model

    if _index is None or _metadata is None or _model is None:
        if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
            raise FileNotFoundError("FAISS index or metadata file missing.")

        _index = faiss.read_index(INDEX_PATH)

        with open(META_PATH, "r") as f:
            _metadata = json.load(f)

        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _index, _metadata, _model


def retrieve_chunks(question, top_k=3):
    index, metadata, model = load_resources()
    query_embedding = model.encode([question])
    D, I = index.search(np.array(query_embedding).astype("float32"), top_k)

    chunks = []
    for i in I[0]:
        entry = metadata[i]
        chunks.append({
            "text": entry["text"],
            "source": entry.get("source_file", "unknown_source.json")
        })

    return chunks


def generate_answer(question, retrieved_chunks):
    context = ""
    for chunk in retrieved_chunks:
        context += f"{chunk['text']}\n(Source: {chunk['source']})\n\n"

    prompt_text = (
        f"Answer the question based only on the context below. "
        f"If not in context, say 'I don't know'.\n\n"
        f"Context:\n{context}\nQuestion: {question}\nAnswer:"
    )

    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt_text}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 500,
            "topP": 0.9,
            "topK": 40
        }
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        parts = result.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        return parts[0]["text"].strip() if parts else "[ERROR] Gemini API returned no answer."

    except requests.exceptions.Timeout:
        return "[ERROR] Gemini API request timed out."
    except requests.exceptions.RequestException as e:
        return f"[ERROR] Request failed: {e}"
    except Exception as e:
        return f"[ERROR] Unexpected error: {e}"


def answer_question(question):
    chunks = retrieve_chunks(question)
    return generate_answer(question, chunks)
