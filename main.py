import json
import urllib.request
import urllib.error

# Твой рабочий ключ с фото
API_KEY = "AQ.Ab8RN6Jdans4aBfeOVSPuUR5J-HBCoNJN-NQFTiHmyl9M9rgaA"

def app(environ, start_response):
    # Определяем, куда зашёл пользователь/Алиса
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')

    # 1. Главная страница для проверки в браузере (GET /)
    if path == '/' and method == 'GET':
        status = '200 OK'
        response_headers = [('Content-Type', 'application/json; charset=utf-8')]
        start_response(status, response_headers)
        output = {"status": "working", "message": "Братуха, чистый Питон запущен! Без библиотек и ебли!"}
        return [json.dumps(output, ensure_ascii=False).encode('utf-8')]

    # 2. Обработчик для Алисы (POST /api/alice)
    elif path == '/api/alice' and method == 'POST':
        status = '200 OK'
        response_headers = [('Content-Type', 'application/json; charset=utf-8')]
        start_response(status, response_headers)

        # Читаем входящий запрос от Яндекса
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            data = json.loads(request_body.decode('utf-8'))
        except Exception:
            data = {}

        command = data.get("request", {}).get("command", "")

        if not command:
            output = {
                "version": "1.0",
                "response": {"text": "На связи, братуха! Что по тачке подсказать?", "end_session": False}
            }
            return [json.dumps(output, ensure_ascii=False).encode('utf-8')]

        # Стучимся к Gemini через встроенный urllib
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Ты опытный автомеханик. Общайся как реальный братуха, используй мат, если надо, но никогда не говори 'бро'. Ответь коротко: {command}"
                }]
            }]
        }
        
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                reply = res_data['candidates'][0]['content']['parts'][0]['text']
        except urllib.error.HTTPError as e:
            reply = f"Братуха, Гугл выдал ошибку: {e.code}"
        except Exception as e:
            reply = f"Братуха, косяк с сетью: {str(e)}"

        output = {
            "version": "1.0",
            "session": data.get("session", {}),
            "response": {"text": reply, "end_session": False}
        }
        return [json.dumps(output, ensure_ascii=False).encode('utf-8')]

    # Если зашли куда-то не туда
    else:
        status = '404 NOT FOUND'
        response_headers = [('Content-Type', 'text/plain; charset=utf-8')]
        start_response(status, response_headers)
        return [b"Not Found"]
