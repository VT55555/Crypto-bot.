import time
import threading
import telebot
import ccxt
import pandas as pd

# === ВСТАВЬТЕ ВАШИ ДАННЫЕ ===
TOKEN = '563940267:AAGoGY8KsJqh1LHaUuj5UIMPPKQj65-Snys'  # Ваш токен в кавычках
CHAT_ID = 5506822047

bot = telebot.TeleBot(TOKEN)
last_processed_candle = None

def monitor_market():
    global last_processed_candle
    while True:
        try:
            symbol = 'BTC/USDT'
            timeframe = '1h'
            
            exchange = ccxt.binance()
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            df['ema_fast'] = df['close'].ewm(span=20, adjust=False).mean()
            df['ema_slow'] = df['close'].ewm(span=50, adjust=False).mean()
            
            high_low = df['high'] - df['low']
            high_close = (df['high'] - df['close'].shift()).abs()
            low_close = (df['low'] - df['close'].shift()).abs()
            df['tr'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df['atr'] = df['tr'].rolling(window=14).mean()
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            candle_time = latest['timestamp']
            
            if candle_time != last_processed_candle:
                price = latest['close']
                atr = latest['atr']
                msg = None
                
                if prev['ema_fast'] <= prev['ema_slow'] and latest['ema_fast'] > latest['ema_slow']:
                    sl = price - (1.5 * atr)
                    tp = price + (3.0 * atr)
                    msg = f"🚨 **АВТО-СИГНАЛ: LONG {symbol}**\n\n🎯 Вход: ${price:.2f}\n🛑 SL: ${sl:.2f}\n✅ TP: ${tp:.2f}"
                elif prev['ema_fast'] >= prev['ema_slow'] and latest['ema_fast'] < latest['ema_slow']:
                    sl = price + (1.5 * atr)
                    tp = price - (3.0 * atr)
                    msg = f"🚨 **АВТО-СИГНАЛ: SHORT {symbol}**\n\n🎯 Вход: ${price:.2f}\n🛑 SL: ${sl:.2f}\n✅ TP: ${tp:.2f}"
                
                if msg:
                    bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                    last_processed_candle = candle_time
        except Exception as e:
            print(f"Ошибка: {e}")
        time.sleep(180)

threading.Thread(target=monitor_market, daemon=True).start()

@bot.message_handler(commands=['start', 'ping'])
def send_welcome(message):
    bot.reply_to(message, "Бот работает и анализирует рынок 24/7!")

bot.polling(non_stop=True)
