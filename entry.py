import json
import secrets
import string
from datetime import datetime

async def on_request(request, env):
    if request.method == "POST":
        body = await request.json()
        
        if "message" in body:
            message = body["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            
            if text.startswith("/start"):
                args = text.split()
                if len(args) > 1:
                    key = args[1]
                    # Проверяем ключ в базе
                    result = await env.DB.prepare(
                        "SELECT user_id FROM keys WHERE key = ? AND used = 0"
                    ).bind(key).first()
                    
                    if result:
                        owner_id = result["user_id"]
                        if str(owner_id) == str(chat_id):
                            await send_telegram(chat_id, "❌ Нельзя писать самому себе", env)
                        else:
                            # Сохраняем разрешение
                            await env.DB.prepare(
                                "INSERT OR REPLACE INTO permissions (user_id, can_send_to) VALUES (?, ?)"
                            ).bind(str(chat_id), str(owner_id)).run()
                            await send_telegram(chat_id, "✅ Теперь ты можешь писать этому человеку анонимно. Просто отправь мне сообщение.", env)
                            await send_telegram(owner_id, "🔔 Кто-то перешёл по твоей ссылке!", env)
                    else:
                        await send_telegram(chat_id, "❌ Недействительная ссылка", env)
                else:
                    # Генерируем новый ключ
                    key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
                    await env.DB.prepare(
                        "INSERT INTO keys (key, user_id, created_at, used) VALUES (?, ?, ?, 0)"
                    ).bind(key, str(chat_id), int(datetime.now().timestamp())).run()
                    
                    link = f"https://t.me/{env.BOT_ID}?start={key}"
                    await send_telegram(chat_id, f"🔗 Твоя анонимная ссылка:\n{link}\n\nОтправь её тому, кто хочет написать тебе.", env)
            
            elif text.startswith("/help"):
                await send_telegram(chat_id, "📖 Отправь /start, чтобы получить свою анонимную ссылку.", env)
            
            else:
                # Обычное сообщение — проверяем, кому его отправить
                perm = await env.DB.prepare(
                    "SELECT can_send_to FROM permissions WHERE user_id = ?"
                ).bind(str(chat_id)).first()
                
                if perm:
                    target_id = perm["can_send_to"]
                    await send_telegram(target_id, f"📨 *Аноним:*\n{text}", env, parse_mode="Markdown")
                    await send_telegram(chat_id, "✅ Сообщение отправлено анонимно!", env)
                else:
                    await send_telegram(chat_id, "ℹ️ У тебя нет активной анонимной связи. Отправь /start, чтобы получить ссылку.", env)
        
        return json.dumps({"ok": True})
    
    return json.dumps({"status": "ok"})

async def send_telegram(chat_id, text, env, parse_mode=None):
    import httpx
    url = f"https://api.telegram.org/bot{env.BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

async def fetch(request, env):
    return await on_request(request, env)
