import os
import time
import threading
import telebot
import ccxt
import pandas as pd
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = '8563940267:AAGoGY8KsJqh1LHaUuj5UIMPPKQj65-Sn'
CHAT_ID = 5506822047

bot = telebot.TeleBot(TOKEN)
last_processed_candle = None

def monitor_market():
    global last_processed_candle
    exchange = ccxt.binance({'enableRateLimit': True})
    symbol = 'BTC/USDT'
    timeframe = '1h'
    print(f"Моніторинг ринку для {symbol}")
    while True:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=2)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            current_candle = df.iloc[-1]['timestamp']
            
            if last_processed_candle != current_candle:
                last_processed_candle = current_candle
                price = df.iloc[-1]['close']
                bot.send_message(CHAT_ID, f"Оновлення {symbol}: ціна {price}")
            
            time.sleep(60)
        except Exception as e:
            print(f"Помилка: {e}")
            time.sleep(30)

threading.Thread(target=monitor_market, daemon=True).start()

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

port = int(os.environ.get("PORT", 10000))
server = HTTPServer(("0.0.0.0", port), SimpleHandler)
server.serve_forever()
