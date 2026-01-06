import os
import requests
import time
import json

BOT_TOKEN = os.environ.get('BOT_TOKEN', 'ВАШ_ТОКЕН_БОТА')
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

print("🤖 Бот запущен!")
print(f"🔑 Токен: {BOT_TOKEN[:10]}...")

users_data = {}
food_log = {}
products = {
    "курица": {"калории": 165, "белки": 31, "жиры": 3.6, "углеводы": 0},
    "рис": {"калории": 130, "белки": 2.7, "жиры": 0.3, "углеводы": 28},
    "яйцо": {"калории": 155, "белки": 13, "жиры": 11, "углеводы": 1.1},
}

def send_message(chat_id, text):
    url = BASE_URL + "sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=data, timeout=5)
    except:
        pass

def handle_message(chat_id, user_id, text):
    if text == "/start":
        return "🏋️ <b>Привет! Я бот для подсчёта калорий на Railway!</b>\n\nКоманды:\n/add рис 150 - добавить еду\n/stats - статистика\n/products - список продуктов"
    elif text == "/products":
        prod_list = "\n".join([f"• {p}: {d['калории']} ккал/100г" for p, d in products.items()])
        return f"🍎 <b>Продукты:</b>\n\n{prod_list}"
    elif text.startswith("/add "):
        parts = text[5:].split()
        if len(parts) < 2:
            return "Формат: /add продукт граммы\nПример: /add рис 150"
        prod_name = parts[0].lower()
        try:
            grams = float(parts[1])
        except:
            return "Ошибка в количестве"
        found = None
        for key in products:
            if prod_name in key:
                found = key
                break
        if not found:
            return "Продукт не найден"
        product = products[found]
        calories = product["калории"] * grams / 100
        if user_id not in food_log:
            food_log[user_id] = []
        food_log[user_id].append({"product": found, "grams": grams, "calories": calories})
        total = sum(item["calories"] for item in food_log[user_id])
        return f"✅ Добавлено: {found} - {grams}г ({calories:.0f} ккал)\nВсего сегодня: {total:.0f} ккал"
    elif text == "/stats":
        if user_id not in food_log or not food_log[user_id]:
            return "📊 Ещё ничего не съедено"
        total = sum(item["calories"] for item in food_log[user_id])
        items = "\n".join([f"• {item['product']}: {item['calories']:.0f} ккал" for item in food_log[user_id]])
        return f"📊 <b>Статистика:</b>\n\n{items}\n\nВсего: <b>{total:.0f} ккал</b>"
    else:
        return "Не понял. Используй /start"

print("⏳ Ожидание сообщений...")
offset = 0
while True:
    try:
        url = BASE_URL + "getUpdates"
        params = {"offset": offset, "timeout": 30}
        response = requests.get(url, params=params, timeout=35).json()
        if "result" in response:
            for update in response["result"]:
                offset = update["update_id"] + 1
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    user_id = update["message"]["from"]["id"]
                    text = update["message"]["text"]
                    print(f"📨 {user_id}: {text}")
                    response_text = handle_message(chat_id, user_id, text)
                    if response_text:
                        send_message(chat_id, response_text)
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Ошибка: {e}")
        time.sleep(5)
