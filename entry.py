# Простой анонимный бот для Cloudflare Workers
import json
import secrets
import string

async def on_request(request, env):
    # Обработка webhook от Telegram
    if request.method == "POST":
        body = await request.json()
        
        # Проверка на команду /start
        if "message" in body and "text" in body["message"]:
            text = body["message"]["text"]
            chat_id = body["message"]["chat"]["id"]
            
            if text.startswith("/start"):
                # Генерация ключа
                key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
                
                # Сохраняем ключ в D1
                await env.DB.prepare(
                    "INSERT INTO keys (key, user_id, created_at) VALUES (?, ?, ?)"
                ).bind(key, str(chat_id), int(__import__('time').time())).run()
                
                link = f"https://t.me/{env.BOT_ID}?start={key}"
                
                # Отправляем сообщение через Telegram API
                await send_telegram(chat_id, f"Твоя анонимная ссылка:\n{link}", env)
        
        return json.dumps({"ok": True})
    
    # GET запрос для проверки
    return json.dumps({"status": "ok"})

async def send_telegram(chat_id, text, env):
    import httpx
    url = f"https://api.telegram.org/bot{env.BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": chat_id, "text": text})

# Точка входа для Cloudflare Workers
async def fetch(request, env):
    return await on_request(request, env)
