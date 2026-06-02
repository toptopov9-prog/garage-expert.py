import os
from fastapi import FastAPI
import google.generativeai as genai

# Создаем экземпляр приложения
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Мост Гаражного Эксперта запущен и готов к работе!"}

@app.post("/api/alice")
async def alice_handler(request: dict):
    req_data = request.get("request", {})
    command = req_data.get("command", "")
    
    if not command:
        reply = "Здорово, братуха! Гаражный Эксперт на связи. Какую тачку чиним, чё подсказать?"
    else:
        try:
            # Получаем ключ из переменных окружения
            api_key = os.environ.get("GEMINI_API_KEY")
            
            # Логирование для отладки (смотри в Logs на Верселе)
            print(f"DEBUG: Key exists: {bool(api_key)}, length: {len(api_key) if api_key else 0}")
            
            if not api_key:
                raise ValueError("API Key is missing")
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"Ты — опытный, авторитетный автомеханик по прозвищу 'Гаражный Эксперт'. Отвечай как чёткий мастер из гаражей, по-свойски, но максимально профессионально и по делу. Помоги человеку с его вопросом: {command}"
            response = model.generate_content(prompt)
            reply = response.text
        except Exception as e:
            # Логируем саму ошибку, чтобы понять, в чём затык
            print(f"DEBUG: ERROR: {str(e)}") 
            reply = "Братуха, под капотом у нейронки что-то замкнуло. Проверь, добавлен ли GEMINI_API_KEY в настройках Верселя!"

    return {
        "version": request.get("version", "1.0"),
        "session": request.get("session", {}),
        "response": {
            "text": reply,
            "end_session": False
        }
    }
