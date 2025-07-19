# 📄 main.py
import time
import yaml
import os
from datetime import datetime
from core.macd_engine import MACDEngine

def load_config():
    with open("config/settings.yaml", "r") as f:
        return yaml.safe_load(f)

def log_to_file(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content + "\n")

start_time = time.time()

def get_uptime():
    uptime_sec = int(time.time() - start_time)
    mins, sec = divmod(uptime_sec, 60)
    hrs, mins = divmod(mins, 60)
    return f"{hrs}h {mins}m {sec}s"

if __name__ == "__main__":
    config = load_config()
    symbols = config["symbols"]
    logging_enabled = config["logging"]["enabled"]
    log_file_path = config["logging"]["file_path"]

    engines = {}
    for symbol in symbols:
        engine = MACDEngine(symbol=symbol)
        if engine.bootstrap_loaded:
            engines[symbol] = engine
        else:
            print(f"⚠️  Skipping {symbol} due to bootstrap failure.")

    prev_signals = {symbol: {} for symbol in engines.keys()}

    print("🌀 ScalpFlow Multi-Symbol MACD Engine Running...\nPress Ctrl+C to stop.\n")

    try:
        while True:
            for symbol, engine in engines.items():
                try:
                    result = engine.generate_macd_signals()

                    if result is None:
                        print(f"⚠️  Skipping {symbol} due to stale data or empty response.")
                        continue

                    signals = result["signals"]
                    score = result["score"]

                    if signals != prev_signals[symbol]:
                        msg = (
                            f"🧠 {result['timestamp']} | {symbol}\n"
                            + "\n".join([f"  {k}: {v}" for k, v in signals.items()])
                            + f"\n🧮 MACD Score: {score}\n{'-' * 40}"
                        )
                        print(msg)

                        if logging_enabled:
                            log_to_file(log_file_path, msg)

                        prev_signals[symbol] = signals.copy()
                except Exception as e:
                    print(f"❌ Error processing {symbol}: {e}. Retrying next loop.")

            print(f"✅ Loop complete | Uptime: {get_uptime()}")
            print("=" * 50)
            time.sleep(60)

    except KeyboardInterrupt:
        print("\n🛑 Engine Stopped Manually.")
