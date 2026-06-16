from fastapi import FastAPI, Request
import httpx
import json

app = FastAPI()

API_KEY = "AQ.Ab8RN6Lx40dhhzfToMCjGYezNBuze_f2P5CCQHzByvJijy5KWg"

@app.post("/api/alice")
async def alice_handler(request: Request):
    data = await request.json()
    command = data.get("request", {}).get("command", "")
    
    if not command:
        return {"version": "1.0", "response": {"text": "На связи, братуха!", "end_session": False}}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": f"Ты автомеханик. Общайся как братуха, мат уместен, НЕ говори 'бро'. Ответ: {command}"}]}]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
    
    res = response.json()
    reply = res['candidates'][0]['content']['parts'][0]['text'] if 'candidates' in res else "Братуха, сервер тупит."
    
    return {"version": "1.0", "response": {"text": reply, "end_session": False}}
