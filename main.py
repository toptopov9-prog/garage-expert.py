import json
import urllib.request
import urllib.error

# Твой чёткий ключ с видео
API_KEY = "AQ.Ab8RN6Jdans4aBfeOVSPuUR5J-HBCoNJN-NQFTiHmyl9M9rgaA"

def app(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')

    # 1. Главная страница для проверки
    if path == '/' and method == 'GET':
        status = '200 OK'
        response_headers = [('Content-Type', 'application/json; charset=utf-8')]
        start_response(status, response_headers)
        output = {"status": "working", "message": "Братуха, чистый Питон на связи! Направляем запрос на Vertex!"}
        return [json.dumps(output, ensure_ascii=False).encode('utf-8')]

    # 2. Обработчик Алисы
    elif path == '/api/alice' and method == 'POST':
        status = '200 OK'
        response_headers = [('Content-Type', 'application/json; charset=utf-8')]
        start_response(status, response_headers)

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

        # МЕНЯЕМ АДРЕС: Стучимся на Vertex AI endpoint, который создан под ключи AQ.
        url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/984654305880/locations/us-central1/publishers/google/models/gemini-1.5-flash:predict"
        
        # Формат запроса для Vertex AI немного отличается, упаковываем под него
        payload = {
            "instances": [
                {
                    "content": f"Ты опытный автомеханик. Общайся как реальный братуха, используй мат, если надо, но никогда не говори 'бро'. Ответь коротко на вопрос: {command}"
                }
            ],
            "parameters": {
                "candidateCount": 1,
                "maxOutputTokens": 300,
                "temperature": 0.7
            }
        }
        
        req_data = json.dumps(payload).encode('utf-8')
        
        # Для Vertex AI ключ передаётся как Bearer токен в заголовок Authorization
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}'
        }
        
        req = urllib.request.Request(url, data=req_data, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                # Достаем ответ из структуры Vertex AI
                reply = res_data['predictions'][0]['candidates'][0]['content']
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e else ""
            reply = f"Братуха, Vertex вернул код {e.code}. Инфо: {error_body[:100]}"
        except Exception as e:
            reply = f"Братуха, затык по сети: {str(e)}"

        output = {
            "version": "1.0",
            "session": data.get("session", {}),
            "response": {"text": reply, "end_session": False}
        }
        return [json.dumps(output, ensure_ascii=False).encode('utf-8')]

    else:
        status = '404 NOT FOUND'
        response_headers = [('Content-Type', 'text/plain; charset=utf-8')]
        start_response(status, response_headers)
        return [b"Not Found"]

