import os
from fastapi import FastAPI, Request
import google.generativeai as genai

# Вот эта строчка обязательна! Вёрсел ищет именно это имя 'app'
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Братуха, я в сети и готов к работе!"}

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
        # Ключ берётся из настроек Вёрсела
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"Ты опытный автомеханик. Общайся как реальный братуха, используй мат и крепкое словцо, если это уместно, но никогда не используй слово 'бро'. Ответь коротко на вопрос: {command}"
        response = model.generate_content(prompt)
        reply = response.text
    except Exception as e:
        reply = "Братуха, сервер Gemini чё-то тупит, давай ещё раз."

    return {
        "version": "1.0",
        "session": data.get("session", {}),
        "response": {"text": reply, "end_session": False}
    }
