from fastapi import FastAPI, Request
import httpx

app = FastAPI()

# Твой рабочий ключ с фото
API_KEY = "AQ.Ab8RN6Jdans4aBfeOVSPuUR5J-HBCoNJN-NQFTiHmyl9M9rgaA"

@app.get("/")
async def root():
    return {"status": "working", "message": "Братуха, движок переведён на прямой впрыск! Всё чётко!"}

@app.post("/api/alice")
async def alice_handler(request: Request):
    try:
        data = await request.json()
    except Exception:
        return {"version": "1.0", "response": {"text": "Братуха, пустой запрос пришёл.", "end_session": False}}
        
    req_data = data.get("request", {})
    command = req_data.get("command", "")
    
    if not command:
        return {
            "version": "1.0",
            "session": data.get("session", {}),
            "response": {"text": "На связи, братуха! Что по тачке подсказать?", "end_session": False}
        }

    # Отправляем ключ прямо в URL — для новых ключей это единственный стопроцентный способ!
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Ты опытный автомеханик. Общайся как реальный братуха, используй мат и крепкое словцо, если это уместно, но никогда не используй слово 'бро'. Ответь коротко на вопрос: {command}"
            }]
        }]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)
            
        if response.status_code == 200:
            res_data = response.json()
            # Достаём ответ из структуры Гугла
            reply = res_data['candidates'][0]['content']['parts'][0]['text']
        else:
            reply = f"Братуха, Гугл выдал код {response.status_code}. Ошибка авторизации обойдена, но что-то не так."
            
    except Exception as e:
        reply = f"Братуха, сеть легла: {str(e)}"

    return {
        "version": "1.0",
        "session": data.get("session", {}),
        "response": {"text": reply, "end_session": False}
    }
