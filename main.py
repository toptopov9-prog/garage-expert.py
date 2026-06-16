import os
from fastapi import FastAPI, Request
import google.generativeai as genai

# Вот она, та самая переменная app, которую Вёрсел потерял и обыскался
app = FastAPI()

# Твой новый, чёткий ключ Gemini прямо с картинки
API_KEY = "AQ.Ab8RN6Jdans4aBfeOVSPuUR5J-HBCoNJN-NQFTiHmyl9M9rgaA"

@app.get("/")
async def root():
    return {"status": "working", "message": "Братуха, всё починили! Движок запущен как изначально!"}

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
        # Настраиваем Гугл по твоему новому официальному ключу
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"Ты опытный автомеханик. Общайся как реальный братуха, используй мат и крепкое словцо, если это уместно, но никогда не используй слово 'бро'. Ответь коротко на вопрос: {command}"
        response = model.generate_content(prompt)
        reply = response.text
    except Exception as e:
        reply = f"Братуха, сервер Gemini тупит. Ошибка: {str(e)}"

    return {
        "version": "1.0",
        "session": data.get("session", {}),
        "response": {"text": reply, "end_session": False}
    }
