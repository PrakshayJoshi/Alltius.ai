# rag_chatbot_gemini.py
import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INDEX_PATH = os.path.join(BASE_DIR, "faiss_index.bin")
META_PATH = os.path.join(BASE_DIR, "faiss_metadata.json")

if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
    print(f"Error: FAISS index '{INDEX_PATH}' or metadata '{META_PATH}' not found.")
    print("Please ensure these files are in the same directory as this script.")
    exit()

try:
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "r") as f:
        metadata = json.load(f)
    print("FAISS index and metadata loaded successfully.")
except Exception as e:
    print(f"Error loading FAISS index or metadata: {e}")
    exit()

model = SentenceTransformer("all-MiniLM-L6-v2")
print("Sentence Transformer model 'all-MiniLM-L6-v2' loaded.")

# Load API key from env variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("[ERROR] GEMINI_API_KEY not set in environment variables.")
    exit()

GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

HEADERS = {
    "Content-Type": "application/json"
}
print(f"Gemini API URL set to: {GEMINI_API_URL}")

def retrieve_chunks(question, top_k=3):
    print(f"Retrieving {top_k} chunks for question: '{question}'...")
    query_embedding = model.encode([question])
    print("Query embedded successfully.")
    
    D, I = index.search(np.array(query_embedding).astype("float32"), top_k)
    
    chunks = [metadata[i]['text'] for i in I[0]]
    print("Chunks retrieved.")
    return chunks

def generate_answer(question, contexts):
    context = "\n".join(contexts)
    
    prompt_text = f"Answer the question based only on the context below. If not in context, say 'I don't know'.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt_text}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 500,
            "topP": 0.9,
            "topK": 40
        }
    }

    print(f"Generating answer using Gemini API for question: '{question[:50]}...'")

    try:
        response = requests.post(GEMINI_API_URL, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        if result.get("candidates") and len(result["candidates"]) > 0 and \
           result["candidates"][0].get("content") and \
           result["candidates"][0]["content"].get("parts") and \
           len(result["candidates"][0]["content"]["parts"]) > 0 and \
           result["candidates"][0]["content"]["parts"][0].get("text"):
            
            generated_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            print("Answer generated successfully by Gemini.")
            return generated_text
        else:
            error_details = json.dumps(result, indent=2)
            print(f"Error: Gemini API returned unexpected response format. Details:\n{error_details}")
            return f"[ERROR] Gemini API returned unexpected response. Please check logs for details."

    except requests.exceptions.Timeout:
        return "[ERROR] Gemini API request timed out. Please check your internet connection or try again later."
    except requests.exceptions.RequestException as e:
        error_message = f"Error during Gemini API request: {e}"
        if response and hasattr(response, 'text'):
            error_message += f"\nAPI Response: {response.text}"
        print(error_message)
        return f"[ERROR] Failed to connect to Gemini API. Details: {e}"
    except json.JSONDecodeError:
        return "[ERROR] Could not parse JSON response from Gemini API."
    except Exception as e:
        print(f"An unexpected error occurred in generate_answer: {e}")
        return f"[ERROR] An unexpected error occurred: {e}"

def answer_question(question):
    chunks = retrieve_chunks(question)
    answer = generate_answer(question, chunks)
    return answer

if __name__ == "__main__":
    print("--- RAG Chatbot with Gemini 2.0 Flash ---")
    
    # --- Test API Connectivity ---
    print("\nTesting Gemini API connectivity with a simple prompt...")
    test_prompt_text = "Hello, what is your purpose?"
    test_payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": test_prompt_text}]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 50,
            "temperature": 0.7
        }
    }
    
    try:
        test_response = requests.post(GEMINI_API_URL, headers=HEADERS, json=test_payload, timeout=15)
        test_response.raise_for_status()
        
        test_result = test_response.json()
        if test_result.get("candidates") and len(test_result["candidates"]) > 0 and \
           test_result["candidates"][0].get("content") and \
           test_result["candidates"][0]["content"].get("parts") and \
           len(test_result["candidates"][0]["content"]["parts"]) > 0 and \
           test_result["candidates"][0]["content"]["parts"][0].get("text"):
            print(f"API Test Status Code: {test_response.status_code}")
            print(f"API Test Response (partial): {test_result['candidates'][0]['content']['parts'][0]['text'][:100]}...")
            print("\nGemini API Test successful! The model is accessible.")
        else:
            print(f"API Test successful, but unexpected response format: {json.dumps(test_result, indent=2)}")
            print("This might indicate an issue with the model or API output.")

    except requests.exceptions.Timeout:
        print("\nAPI Test failed: Request timed out. Check your internet connection or API availability.")
    except requests.exceptions.RequestException as e:
        print(f"\nAPI Test failed: {e}")
        if 'test_response' in locals() and hasattr(test_response, 'text'):
            print(f"API Error Details: {test_response.text}")
        print("This indicates an issue with the Gemini API key, network, or service availability.")
    except Exception as e:
        print(f"\nAn unexpected error occurred during API test: {e}")

    # --- Start interactive chatbot ---
    print("\n--- Starting RAG Chatbot ---")
    print("Type 'exit' or 'quit' to end.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        response = answer_question(user_input)
        print(f"\nBot: {response}\n")
