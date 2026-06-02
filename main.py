import os
import google.generativeai as genai

@app.post("/api/alice")
async def alice_handler(request: dict):
    req_data = request.get("request", {})
    command = req_data.get("command", "")
    
    if not command:
        reply = "Здорово, братуха! Гаражный Эксперт на связи. Какую тачку чиним, чё подсказать?"
    else:
        try:
            # Подтягиваем ключ из настроек Верселя
            genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Задаём характер нашему ИИ
            prompt = f"Ты — опытный, авторитетный автомеханик по прозвищу 'Гаражный Эксперт'. Отвечай как чёткий мастер из гаражей, по-свойски, но максимально профессионально и по делу. Помоги человеку с его вопросом: {command}"
            response = model.generate_content(prompt)
            reply = response.text
        except Exception as e:
            reply = "Братуха, под капотом у нейронки что-то замкнуло. Проверь, добавлен ли GEMINI_API_KEY в настройках Верселя!"

    return {
        "version": request.get("version", "1.0"),
        "session": request.get("session", {}),
        "response": {
            "text": reply,
            "end_session": False
        }
    }

