from fastapi import FastAPI
from pydantic import BaseModel
from rag_chatbot_gemini import answer_question

app = FastAPI()

class Query(BaseModel):
    query: str

@app.post("/ask")
async def ask_question(q: Query):
    return {"answer": answer_question(q.query)}
