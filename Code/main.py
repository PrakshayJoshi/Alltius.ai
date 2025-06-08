# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag_chatbot_gemini import answer_question
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI()

# CORS: Allow your frontend domain explicitly in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace with actual origin 
    allow_methods=["POST"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str

@app.post("/ask")
async def ask_question(q: Query):
    if not q.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        answer = answer_question(q.query)
        return {"question": q.query, "answer": answer}
    except Exception as e:
        logging.exception("Error answering question")
        raise HTTPException(status_code=500, detail="Internal server error")
