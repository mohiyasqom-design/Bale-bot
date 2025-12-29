import os
import requests
import time
import openai
from dotenv import load_dotenv

# ====== بارگذاری فایل .env ======
load_dotenv()  # فایل .env کنار bot.py باید باشه

# ====== تنظیمات ======
BALE_TOKEN = os.getenv("BALE_TOKEN")
BALE_API = f"https://tapi.bale.ai/bot{BALE_TOKEN}"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# ====== دریافت پیام‌ها ======
def get_updates(offset=None):
    url = f"{BALE_API}/getUpdates"
    params = {}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(url, params=params, timeout=30)
        data = r.json()
        print("Debug getUpdates:", data)
        return data
    except Exception as e:
        print("Error getting updates:", e)
        return None

# ====== ارسال پیام ======
def send_message(chat_id, text):
    url = f"{BALE_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        data = r.json()
        print("Debug sendMessage:", data)
        return data
    except Exception as e:
        print("Error sending message:", e)
        return None

# ====== گرفتن پاسخ از OpenAI ======
def get_openai_response(prompt):
    try:
        response = openai.responses.create(
            model="gpt-5-nano",
            input=prompt
        )
        print("Debug OpenAI:", response)
        if hasattr(response, "output_text"):
            return response.output_text
        elif isinstance(response, dict) and "output_text" in response:
            return response["output_text"]
        else:
            return "❌ خطای OpenAI"
    except Exception as e:
        print("Error from OpenAI:", e)
        return "❌ خطای OpenAI"

# ====== حلقه اصلی ======
def main():
    print("🤖 ربات آماده و اجراست...")
    last_update_id = None
    while True:
        updates = get_updates(offset=(last_update_id + 1) if last_update_id else None)
        if updates and updates.get("ok") and updates.get("result"):
            for u in updates["result"]:
                last_update_id = u["update_id"]
                m = u.get("message")
                if not m or "text" not in m:
                    continue
                chat_id = m["chat"]["id"]
                text = m["text"]

                # پاسخ OpenAI
                reply = get_openai_response(text)
                send_message(chat_id, reply)
        time.sleep(1)

if __name__ == "__main__":
    main()