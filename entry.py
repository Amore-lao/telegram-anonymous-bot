import json

async def fetch(request, env):
    # Просто отвечаем на GET запрос
    if request.method == "GET":
        return new_response(json.dumps({"status": "ok"}), 200)
    
    # Обработка POST от Telegram
    if request.method == "POST":
        try:
            body = await request.json()
            
            # Если есть сообщение
            if "message" in body:
                chat_id = body["message"]["chat"]["id"]
                text = body["message"].get("text", "")
                
                # Отправляем ответ через API Telegram
                await send_telegram(chat_id, f"Принято: {text}", env)
            
            return new_response(json.dumps({"ok": True}), 200)
        except Exception as e:
            return new_response(json.dumps({"error": str(e)}), 500)
    
    return new_response(json.dumps({"error": "Method not allowed"}), 405)

async def send_telegram(chat_id, text, env):
    # Отправляем сообщение через Telegram API
    import httpx
    url = f"https://api.telegram.org/bot{env.BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": chat_id, "text": text})

def new_response(data, status=200):
    return Response.new(data, status=status, headers={"Content-Type": "application/json"})
