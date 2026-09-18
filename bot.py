import os
import time
import threading
import json
import urllib.request
import telebot
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = '8563940267:AAGoGY8KsJqh1LHaUuj5UIMPPKQj65-Sn'
CHAT_ID = 5506822047

bot = telebot.TeleBot(TOKEN)

def monitor_market():
    print("Моніторинг ринку запущено")
    while True:
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                price = data['bitcoin']['usd']
                bot.send_message(CHAT_ID, f"Оновлення BTC/USDT: ціна ${price}")
        except Exception as e:
            print(f"Помилка запиту ціни: {e}")
        time.sleep(60)

# Запускаємо моніторинг у фоновому потоці
threading.Thread(target=monitor_market, daemon=True).start()

# Вебсервер для Render
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

port = int(os.environ.get("PORT", 10000))
server = HTTPServer(("0.0.0.0", port), SimpleHandler)
server.serve_forever()
