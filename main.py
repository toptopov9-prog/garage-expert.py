import os
from fastapi import FastAPI, Request
import google.generativeai as genai

app = FastAPI()

# Зашили твой ключ прямо в движок, теперь Версел не отмажется
API_KEY = "AQ.Ab8RN6Lx40dhhzfToMCjGYezNBuze_f2P5CCQHzByvJijy5KWg"

@app.get("/")
async def root():
    return {"message": "Братуха, движок запущен прямо с ключа!"}

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

    try:
        # Инициализируем Гугл напрямую по ключу
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"Ты опытный автомеханик. Общайся как реальный братуха, используй мат и крепкое словцо, если это уместно, но никогда не используй слово 'бро'. Ответь коротко на вопрос: {command}"
        response = model.generate_content(prompt)
        reply = response.text
    except Exception as e:
        # Если ключ не подойдёт, он выведет в Алису саму ошибку, и мы сразу поймём в чём дело
        reply = f"Братуха, косяк с ключом. Гугл выдал ошибку: {str(e)}"

    return {
        "version": "1.0",
        "session": data.get("session", {}),
        "response": {"text": reply, "end_session": False}
    }
