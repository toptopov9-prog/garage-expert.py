import os
from fastapi import FastAPI
import google.generativeai as genai

app = FastAPI()

# Добавляем обработку и корня, и нашего пути
"/"
"/api/alice"
async def alice_handler(request: dict = None):
    # Если запрос пустой, просто отвечаем
    if request is None:
        return {"version": "1.0", "response": {"text": "На связи, братуха!", "end_session": False}}
    
    req_data = request.get("request", {})
    command = req_data.get("command", "")
    
    if not command:
        return {
            "version": "1.0",
            "session": request.get("session", {}),
            "response": {"text": "Чего хотел?", "end_session": False}
        }

    try:
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        response = model.generate_content(
            f"Ты автомеханик. Общайся как братуха, используй нецензурную лексику, если уместно, но НЕ используй слово 'бро'. Твой совет: {command}"
        )
        reply = response.text
    except Exception as e:
        reply = "Братуха, какая-то хуйня с ответом сервера."

    return {
        "version": "1.0",
        "session": request.get("session", {}),
        "response": {"text": reply, "end_session": False}
    }
