import os
from fastapi import FastAPI
import google.generativeai as genai

app = FastAPI()

# Твой основной обработчик
"/api/alice"
async def alice_handler(request: dict):
    # Получаем текст от Алисы
    req_data = request.get("request", {})
    command = req_data.get("command", "")
    
    # Если команда пустая, кидаем приветствие
    if not command:
        return {
            "version": "1.0",
            "session": request.get("session", {}),
            "response": {"text": "На связи, братуха! Что по тачке будем делать?", "end_session": False}
        }

    try:
        # Настройка ключа (убедись, что в Vercel Environment Variables он прописан как GEMINI_API_KEY)
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Запрос к нейронке
        prompt = f"Ты опытный автомеханик. Отвечай коротко, по делу, как братуха. Не используй слово 'бро'. Твой совет: {command}"
        response = model.generate_content(prompt)
        reply = response.text
    except Exception as e:
        reply = "Братуха, сервер тупит, не могу прогрузиться."

    return {
        "version": "1.0",
        "session": request.get("session", {}),
        "response": {"text": reply, "end_session": False}
    }
