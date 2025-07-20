# 📄 utils/action_router.py

import os
import yaml
import requests
from datetime import datetime

class ActionRouter:
    def __init__(self, config_path="config/action_routes.yaml"):
        self.routes = self.load_routes(config_path)

    def load_routes(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing action_routes.yaml: {path}")
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def dispatch(self, action: str, symbol: str, signal_info: dict):
        handlers = self.routes.get(action.upper(), [])
        for handler_name in handlers:
            method = getattr(self, handler_name, None)
            if callable(method):
                method(symbol, signal_info)
            else:
                print(f"⚠️ Unknown handler: {handler_name}")

    # === HANDLER 1 ===
    def print_to_console(self, symbol, signal_info):
        print(f"[{datetime.utcnow().isoformat()}Z] {symbol} -> {signal_info['score']} MACD Score")

    # === HANDLER 2 ===
    def save_to_csv(self, symbol, signal_info):
        import csv

        folder = "data/logs"
        os.makedirs(folder, exist_ok=True)
        filename = f"{folder}/{symbol.replace('/', '_')}_actions.csv"

        fieldnames = ["timestamp", "symbol", "score", "action"]
        row = {
            "timestamp": signal_info["timestamp"],
            "symbol": symbol,
            "score": signal_info["score"],
            "action": signal_info.get("action", "UNKNOWN")
        }

        write_header = not os.path.exists(filename)

        with open(filename, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow(row)

    # === HANDLER 3 ===
    def send_telegram_alert(self, symbol, signal_info):
        try:
            # Load Telegram config from settings.yaml
            with open("config/settings.yaml", "r") as f:
                config = yaml.safe_load(f)

            telegram_cfg = config.get("telegram", {})
            if not telegram_cfg.get("enabled", False):
                print("⚠️ Telegram alerts are disabled in config.")
                return

            token = telegram_cfg.get("token")
            chat_id = telegram_cfg.get("chat_id")

            if not token or not chat_id:
                print("❌ Missing Telegram token or chat_id in config.")
                return

            # Format message
            score = signal_info["score"]
            action = signal_info.get("action", "UNKNOWN")
            layers = signal_info["signals"]

            layer_str = "\n".join([f"`{k}`: *{v}*" for k, v in layers.items()])
            msg = (
                f"📢 *{action} Signal Triggered*\n"
                f"📊 *{symbol}* | *MACD Score: {score}*\n"
                f"🕒 {signal_info['timestamp']}\n\n"
                f"{layer_str}"
            )

            # Send via Telegram Bot API
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": msg,
                "parse_mode": "Markdown"
            }

            resp = requests.post(url, json=payload)
            if resp.status_code != 200:
                print(f"❌ Telegram alert failed: {resp.status_code} – {resp.text}")

        except Exception as e:
            print(f"❌ Error sending Telegram alert: {e}")
