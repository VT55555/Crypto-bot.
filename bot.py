import time
import threading
import telebot
import ccxt
import pandas as pd

# === ВАШІ ДАНІ ЗБЕРЕЖЕНО ===
TOKEN ='8563940267:AAGoGY8KsJqhlLHaUuj5UIMPPKQj65-Snys'
CHAT_ID = 5506822047

bot = telebot.TeleBot(TOKEN)
last_processed_candle = None

def monitor_market():
    global last_processed_candle
    
    exchange = ccxt.binance({
        'enableRateLimit': True,
    })
    
    symbol = 'BTC/USDT'
    timeframe = '1h'

    print(f"Моніторинг ринку для {symbol} запущено...")

    while True:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            current_candle = df['timestamp'].iloc[-1]
            if last_processed_candle == current_candle:
                time.sleep(30)
                continue

            df['ema_fast'] = df['close'].ewm(span=9, adjust=False).mean()
            df['ema_slow'] = df['close'].ewm(span=21, adjust=False).mean()

            df['high_low'] = df['high'] - df['low']
            df['high_close'] = (df['high'] - df['close'].shift()).abs()
            df['low_close'] = (df['low'] - df['close'].shift()).abs()
            df['tr'] = pd.concat([df['high_low'], df['high_close'], df['low_close']], axis=1).max(axis=1)
            df['atr'] = df['tr'].rolling(window=14).mean()

            last_row = df.iloc(-1)
            message = (
                f"📊 *Сигнал ринку {symbol}*\n"
                f"• Таймфрейм: `{timeframe}`\n"
                f"• Ціна закриття: `{last_row['close']}`\n"
                f"• EMA (9): `{last_row['ema_fast']:.2f}`\n"
                f"• EMA (21): `{last_row['ema_slow']:.2f}`\n"
                f"• ATR (14): `{last_row['atr']:.2f}`"
            )
            
            bot.send_message(CHAT_ID, message, parse_mode='Markdown')
            last_processed_candle = current_candle
            
            time.sleep(60)

        except Exception as e:
            print(f"Сталася помилка: {e}")
            time.sleep(30)

if __name__ == '__main__':
    t = threading.Thread(target=monitor_market)
    t.daemon = True
    t.start()

    bot.infinity_polling()
