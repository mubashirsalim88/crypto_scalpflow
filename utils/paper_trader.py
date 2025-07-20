import os
import csv
from datetime import datetime

class PaperTrader:
    def __init__(self, base_dir="data/trades"):
        self.positions = {}  # symbol: dict with position state
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def process_signal(self, symbol, action, price):
        now = datetime.utcnow().isoformat()
        position = self.positions.get(symbol, {"state": "flat", "entry": 0.0, "pnl": 0.0, "last_action": None})

        log_entry = {
            "timestamp": now,
            "symbol": symbol,
            "action": action,
            "price": price,
            "pnl": 0.0,
            "position": position["state"]
        }

        if action == "BUY" and position["state"] == "flat":
            position.update({
                "state": "long",
                "entry": price,
                "last_action": "BUY"
            })
        elif action == "SELL" and position["state"] == "long":
            pnl = price - position["entry"]
            log_entry["pnl"] = pnl
            position.update({
                "state": "flat",
                "entry": 0.0,
                "pnl": pnl,
                "last_action": "SELL"
            })
        else:
            # Ignore duplicate or invalid transitions
            return

        self.positions[symbol] = position
        log_entry["position"] = position["state"]

        self._log_trade(symbol, log_entry)

    def _log_trade(self, symbol, data):
        filename = os.path.join(self.base_dir, f"{symbol}_paper_trades.csv")
        file_exists = os.path.isfile(filename)
        with open(filename, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
