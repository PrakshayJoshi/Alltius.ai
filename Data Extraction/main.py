from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os

# Add parent directory to sys.path so Python can find rag_chatbot_gemini.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag_chatbot_gemini import answer_question


app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
def ask_endpoint(req: QueryRequest):
    response = answer_question(req.query)
    return {"answer": response}


