const https = require('https');

// Твой законный ключ, шлюз api.gemini-proxy.ru его прожуёт
const API_KEY = "AQ.Ab8RN6Jdans4aBfeOVSPuUR5J-HBCoNJN-NQFTiHmyl9M9rgaA";

module.exports = async (req, res) => {
    // 1. Проверка главной страницы в браузере (GET /)
    if (req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        return res.end(JSON.stringify({ status: "working", message: "Братуха, мотор на Node.js шепчет! Родной движок Вёрсела в деле!" }));
    }

    // 2. Обработчик Алисы (POST /)
    if (req.method === 'POST') {
        let bodyBuffer = [];
        
        // Вручную собираем данные от Яндекса, чтобы точно ничего не потерять без библиотек
        req.on('data', (chunk) => {
            bodyBuffer.push(chunk);
        }).on('end', () => {
            let data = {};
            try {
                data = JSON.parse(Buffer.concat(bodyBuffer).toString());
            } catch (e) {
                data = {};
            }

            const command = (data.request && data.request.command) ? data.request.command : "";

            if (!command) {
                res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
                return res.end(JSON.stringify({
                    version: "1.0",
                    session: data.session || {},
                    response: { text: "На связи, братуха! Что по тачке подсказать?", end_session: false }
                }));
            }

            // Упаковываем запрос под Gemini
            const payload = JSON.stringify({
                contents: [{
                    parts: [{
                        text: `Ты опытный автомеханик. Общайся как реальный братуха, используй мат, если надо, но никогда не говори 'бро'. Ответь коротко: ${command}`
                    }]
                }]
            });

            const url = `https://api.gemini-proxy.ru/v1beta/models/gemini-1.5-flash:generateContent?key=${API_KEY}`;

            const options = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Content-Length': Buffer.byteLength(payload)
                },
                timeout: 10000
            };

            // Стреляем в европейский шлюз, Node.js делает это без сучка и задоринки
            const geminiRequest = https.request(url, options, (geminiResponse) => {
                let resBody = '';
                geminiResponse.on('data', (chunk) => { resBody += chunk; });
                
                geminiResponse.on('end', () => {
                    let reply = "";
                    try {
                        const resData = JSON.parse(resBody);
                        if (geminiResponse.statusCode === 200) {
                            reply = resData.candidates[0].content.parts[0].text;
                        } else {
                            reply = `Братуха, шлюз вернул ошибку ${geminiResponse.statusCode}`;
                        }
                    } catch (e) {
                        reply = "Братуха, косяк при чтении ответа от шлюза.";
                    }

                    // Отдаём чистый JSON обратно Алисе
                    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
                    res.end(JSON.stringify({
                        version: "1.0",
                        session: data.session || {},
                        response: { text: reply, end_session: false }
                    }));
                });
            });

            geminiRequest.on('error', (error) => {
                res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
                res.end(JSON.stringify({
                    version: "1.0",
                    session: data.session || {},
                    response: { text: `Братуха, обрыв сети на JS: ${error.message}`, end_session: false }
                }));
            });

            geminiRequest.write(payload);
            geminiRequest.end();
        });
    }
};
