import json
import httpx

async def fetch(request, env):
    if request.method == "POST":
        body = await request.json()
        
        if "message" in body:
            chat_id = body["message"]["chat"]["id"]
            text = body["message"].get("text", "")
            
            # Отвечаем тем же текстом
            await send_message(chat_id, f"Эхо: {text}", env)
        
        return json.dumps({"ok": True})
    
    return json.dumps({"status": "ok"})

async def send_message(chat_id, text, env):
    url = f"https://api.telegram.org/bot{env.BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": chat_id, "text": text})
