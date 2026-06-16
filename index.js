const https = require('https');

// Твой рабочий ключ, шлюз api.gemini-proxy.ru его переварит
const API_KEY = "AQ.Ab8RN6Jdans4aBfeOVSPuUR5J-HBCoNJN-NQFTiHmyl9M9rgaA";

module.exports = async (req, res) => {
    // 1. Проверка главной страницы (GET /)
    if (req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        return res.end(JSON.stringify({ status: "working", message: "Братуха, Node.js завёлся с пол-оборота! Родной движок Вёрсела!" }));
    }

    // 2. Обработчик Алисы (POST /api/alice)
    if (req.method === 'POST') {
        let command = "";
        
        if (req.body && req.body.request) {
            command = req.body.request.command || "";
        }

        if (!command) {
            res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
            return res.end(JSON.stringify({
                version: "1.0",
                response: { text: "На связи, братуха! Что по тачке подсказать?", end_session: false }
            }));
        }

        // Данные для отправки в Gemini через прокси
        const payload = JSON.stringify({
            contents: [{
                parts: [{
                    text: `Ты опытный автомеханик. Общайся как реальный братуха, используй мат, если надо, но никогда не говори 'бро'. Ответь коротко: ${command}`
                }]
            }]
        });

        const url = `https://api.gemini-proxy.ru/v1beta/models/gemini-1.5-flash:generateContent?key=${API_KEY}`;

        // Настройки сетевого запроса встроенного модуля https
        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(payload)
            },
            timeout: 12000
        };

        // Стреляем в шлюз встроенным методом Node.js
        const request = https.request(url, options, (response) => {
            let data = '';
            response.on('data', (chunk) => { data += chunk; });
            
            response.on('end', () => {
                let reply = "";
                try {
                    const resData = JSON.parse(data);
                    if (response.statusCode === 200) {
                        reply = resData.candidates[0].content.parts[0].text;
                    } else {
                        reply = `Братуха, шлюз на JS вернул код ${response.statusCode}`;
                    }
                } catch (e) {
                    reply = "Братуха, не смог распарсить ответ от шлюза.";
                }

                res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
                res.end(JSON.stringify({
                    version: "1.0",
                    session: req.body.session || {},
                    response: { text: reply, end_session: false }
                }));
            });
        });

        request.on('error', (error) => {
            res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
            res.end(JSON.stringify({
                version: "1.0",
                session: req.body.session || {},
                response: { text: `Братуха, затык сети на JS: ${error.message}`, end_session: false }
            }));
        });

        request.write(payload);
        request.end();
    }
};

