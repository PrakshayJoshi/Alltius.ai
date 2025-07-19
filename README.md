Alltius. AI assignment 

1. run server
uvicorn main:app --reload --port 8001

2. Check API is working fine? 
curl -X POST http://127.0.0.1:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Where can I see my account balance?"}'

3. run Frontend
npm dev run

# RagChatBot
