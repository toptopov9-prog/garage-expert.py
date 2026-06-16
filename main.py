import json
import urllib.request
import urllib.error
import ssl

# Твой ключ, пускай работает
API_KEY = "AQ.Ab8RN6Jdans4aBfeOVSPuUR5J-HBCoNJN-NQFTiHmyl9M9rgaA"

def app(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')

    if path == '/' and method == 'GET':
        status = '200 OK'
        response_headers = [('Content-Type', 'application/json; charset=utf-8')]
        start_response(status, response_headers)
        output = {"status": "working", "message": "Братуха, чистый Питон без библиотек готов к бою!"}
        return [json.dumps(output, ensure_ascii=False).encode('utf-8')]

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

        # Стучимся через зеркало, но теперь отключаем строгую проверку SSL встроенного urllib,
        # чтобы Вёрсел не орал "Device or resource busy"
        url = f"https://api.gemini-proxy.ru/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Ты опытный автомеханик. Общайся как реальный братуха, используй мат, если надо, но никогда не говори 'бро'. Ответь коротко: {command}"
                }]
            }]
        }
        
        req_data = json.dumps(payload).encode('utf-8')
        
        # Магия чистого Питона: создаем контекст, который пробивает сетевые блокировки Вёрсела
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(
            url, 
            data=req_data, 
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0'  # Маскируемся под браузер, чтобы шлюз не блокировал
            }
        )

        try:
            # Передаем наш контекст ctx в urlopen
            with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                reply = res_data['candidates'][0]['content']['parts'][0]['text']
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e else ""
            reply = f"Братуха, шлюз ответил ошибкой {e.code}: {error_body[:100]}"
        except Exception as e:
            reply = f"Братуха, затык сети на чистом Питоне: {str(e)}"

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
