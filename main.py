const { GoogleGenAI } = require("@google/genai");

module.exports = async (req, res) => {
  // Нам подходят запросы и на корень /, и на любой другой путь, Яндекс больше не выдаст 404
  if (req.method !== 'POST') {
    return res.status(200).json({ message: "На связи, братуха! Скрипт дышит." });
  }

  const { request: aliceRequest, session } = req.body || {};
  const command = aliceRequest?.command || "";

  // Если Алиса просто проверяет навык (пустая команда)
  if (!command) {
    return res.status(200).json({
      version: "1.0",
      session: session || {},
      response: {
        text: "На связи, братуха! Что по технике? Какую тачку крутим?",
        end_session: false
      }
    });
  }

  try {
    // Подтягиваем твой ключ из настроек Вёрсела
    const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
    
    const response = await ai.models.generateContent({
      model: 'gemini-1.5-flash',
      contents: Ты опытный автомеханик. Общайся как реальный братуха, используй крепкое словцо и мат, если это уместно, но никогда не используй слово 'бро'. Ответь коротко на вопрос: ${command},
    });

    const reply = response.text || "Братуха, что-то пошло не так с ответом, повтори.";

    return res.status(200).json({
      version: "1.0",
      session: session || {},
      response: {
        text: reply,
        end_session: false
      }
    });

  } catch (error) {
    return res.status(200).json({
      version: "1.0",
      session: session || {},
      response: {
        text: "Братуха, косяк с подключением к нейронке, давай еще раз попробуем.",
        end_session: false
      }
    });
  }
};
