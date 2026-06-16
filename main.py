import json
import subprocess

# Твой ключ
API_KEY = "AQ.Ab8RN6Jdans4aBfeOVSPuUR5J-HBCoNJN-NQFTiHmyl9M9rgaA"

def app(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')

    if path == '/' and method == 'GET':
        status = '200 OK'
        response_headers = [('Content-Type', 'application/json; charset=utf-8')]
        start_response(status, response_headers)
        output = {"status": "working", "message": "Братуха, система на curl готова к бою!"}
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

        # Стучимся через зеркало
        url = f"https://api.gemini-proxy.ru/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Ты опытный автомеханик. Общайся как реальный братуха, используй мат, если надо, но никогда не говори 'бро'. Ответь коротко: {command}"
                }]
            }]
        }
        
        # Переводим данные запроса в строку JSON
        json_data = json.dumps(payload)

        try:
            # Наглухо обходим лимиты Вёрсела: фигачим запрос напрямую через системный curl
            cmd = [
                'curl', 
                '-s', 
                '-X', 'POST', 
                '-H', 'Content-Type: application/json', 
                '-d', json_data, 
                url
            ]
            
            # Выполняем команду в системе и забираем ответ
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
            
            if result.returncode == 0 and result.stdout:
                res_data = json.loads(result.stdout)
                reply = res_data['candidates'][0]['content']['parts'][0]['text']
            else:
                reply = f"Братуха, системный curl промахнулся. Ошибка: {result.stderr}"
                
        except Exception as e:
            reply = f"Братуха, даже через консоль не пробились: {str(e)}"

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
