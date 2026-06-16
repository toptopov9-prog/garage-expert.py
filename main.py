from flask import Flask, request, jsonify
import httpx

app = Flask(__name__)

# Твой свежий API-ключ Gemini с фото
API_KEY = "AQ.Ab8RN6Jdans4aBfeOVSPuUR5J-HBCoNJN-NQFTiHmyl9M9rgaA"

# Главная страница для проверки в браузере
@app.route('/', methods=['GET'])
def root():
    return jsonify({"status": "working", "message": "Братуха, движок на Flask запущен! Всё чётко!"})

# Обработчик для Алисы
@app.route('/api/alice', methods=['POST'])
async def alice_handler():
    try:
        data = request.get_json(silent=True) or {}
    except Exception:
        return jsonify({"version": "1.0", "response": {"text": "Братуха, пустой запрос.", "end_session": False}})
        
    command = data.get("request", {}).get("command", "")
    
    if not command:
        return jsonify({
            "version": "1.0",
            "response": {"text": "На связи, братуха! Что по тачке подсказать?", "end_session": False}
        })

    # Стучимся к Gemini напрямую через URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Ты опытный автомеханик. Общайся как реальный братуха, используй мат, если надо, но никогда не используй слово 'бро'. Ответь коротко: {command}"
            }]
        }]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)
            
        if response.status_code == 200:
            res_data = response.json()
            reply = res_data['candidates'][0]['content']['parts'][0]['text']
        else:
            reply = f"Братуха, Гугл ответил кодом {response.status_code}."
            
    except Exception as e:
        reply = f"Братуха, сеть легла: {str(e)}"

    return jsonify({
        "version": "1.0",
        "response": {"text": reply, "end_session": False}
    })

# Точка входа для Вёрсела
handler = app
