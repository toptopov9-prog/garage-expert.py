import json
import urllib.request
import urllib.error

# Твой законный ключ с видео, теперь мы его приручим
API_KEY = "AQ.Ab8RN6Jdans4aBfeOVSPuUR5J-HBCoNJN-NQFTiHmyl9M9rgaA"

def app(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')

    # 1. Главная страница
    if path == '/' and method == 'GET':
        status = '200 OK'
        response_headers = [('Content-Type', 'application/json; charset=utf-8')]
        start_response(status, response_headers)
        output = {"status": "working", "message": "Братуха, код готов принимать новые ключи!"}
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

        # Теперь URL чистый, без точки из ключа!
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Ты опытный автомеханик. Общайся как реальный братуха, используй мат, если надо, но никогда не говори 'бро'. Ответь коротко на вопрос: {command}"
                }]
            }]
        }
        
        req_data = json.dumps(payload).encode('utf-8')
        
        # Передаем ключ в заголовках x-goog-api-key — так Гугл поймет ключ формата AQ.Ab8
        headers = {
            'Content-Type': 'application/json',
            'x-goog-api-key': API_KEY
        }
        
        req = urllib.request.Request(url, data=req_data, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                reply = res_data['candidates'][0]['content']['parts'][0]['text']
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e else ""
            reply = f"Братуха, Гугл выдал ошибку {e.code}. Ответ сервера: {error_body[:100]}"
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
