from fastapi import FastAPI, Request
import os
import google.generativeai as genai

app = FastAPI()

"/api/alice"
async def alice_handler(request: Request):
    data = await request.json()
    req_data = data.get("request", {})
    command = req_data.get("command", "")
    
    if not command:
        return {
            "version": "1.0",
            "session": data.get("session", {}),
            "response": {"text": "На связи, братуха. Что по тачке?", "end_session": False}
        }

    try:
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        response = model.generate_content(
            f"Ты автомеханик. Общайся как братуха, используй мат, но НЕ говори 'бро'. Вопрос: {command}"
        )
        reply = response.text
    except Exception as e:
        reply = "Братуха, сервер прилёг отдохнуть."

    return {
        "version": "1.0",
        "session": data.get("session", {}),
        "response": {"text": reply, "end_session": False}
    }
