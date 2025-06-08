# main.py
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from rag_chatbot_gemini import answer_question
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# If you're calling this from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend origin for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str

@app.post("/ask")
async def ask_question(q: Query):
    try:
        if not q.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
        answer = answer_question(q.query)
        return {"question": q.query, "answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
