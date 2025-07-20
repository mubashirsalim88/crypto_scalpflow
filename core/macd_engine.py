# 📄 core/macd_engine.py

import pandas as pd
from utils.indicators import MACD_SETS, compute_macd
from utils.bootstrap_manager import load_or_fetch_bootstrap
from utils.historical_loader import fetch_historical_ohlcv
from utils.state_cache import load_state, save_state
from datetime import datetime

class MACDEngine:
    def __init__(self, symbol='BTC/USDT', timeframe='5m', limit=2000):
        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = limit

        try:
            # Load cached bootstrap once for MACD warm-up (optional)
            self.df_bootstrap = load_or_fetch_bootstrap(symbol, timeframe, limit)
            self.bootstrap_loaded = True
        except Exception as e:
            print(f"❌ Failed to bootstrap {symbol}: {e}")
            self.df_bootstrap = pd.DataFrame()
            self.bootstrap_loaded = False

        # Load previous state if available
        self.state = load_state(self.symbol) or {
            "last_timestamp": None,
            "last_macd_score": 0,
            "last_layer_flags": [0]*7,
            "last_signal_flag": None,
            "last_histogram_direction": None
        }
        print(f"🧠 Restored state for {self.symbol}: {self.state}")

    def fetch_ohlcv(self):
        # 🔁 Fetch fresh OHLCV data on every loop
        df = fetch_historical_ohlcv(self.symbol, self.timeframe, limit=self.limit)
        return df

    def is_data_fresh(self, df):
        if df.empty:
            return False
        last_ts = df['timestamp'].iloc[-1]
        delta = pd.Timestamp.utcnow() - last_ts
        return delta.total_seconds() < 600  # 10 minutes

    def generate_macd_signals(self):
        try:
            df = self.fetch_ohlcv()

            if not self.is_data_fresh(df):
                print(f"⚠️  [STALE DATA] {self.symbol} - Last candle: {df['timestamp'].iloc[-1]}")
                return None

            latest_signals = {}
            histograms = []

            for macd_set in MACD_SETS:
                macd = compute_macd(df, macd_set["fast"], macd_set["slow"], macd_set["signal"])
                recent_macd = macd.iloc[-2:]

                prev_hist = recent_macd['histogram'].iloc[0]
                curr_hist = recent_macd['histogram'].iloc[1]
                histograms.append((prev_hist, curr_hist))

                if prev_hist < 0 and curr_hist > 0:
                    signal = +1
                elif prev_hist > 0 and curr_hist < 0:
                    signal = -1
                else:
                    signal = 0

                latest_signals[macd_set["label"]] = signal

            score = sum(latest_signals.values())

            # Determine histogram direction (based on first MACD layer)
            prev_hist, curr_hist = histograms[0]
            hist_diff = curr_hist - prev_hist
            hist_direction = "rising" if hist_diff > 0 else "falling" if hist_diff < 0 else "flat"

            # Signal flag logic (simple version)
            if score >= 3:
                signal_flag = "buy"
            elif score <= -3:
                signal_flag = "sell"
            else:
                signal_flag = None

            # Update and save state
            self.state["last_timestamp"] = df["timestamp"].iloc[-1].strftime("%Y-%m-%dT%H:%M:%SZ")
            self.state["last_macd_score"] = score
            self.state["last_layer_flags"] = list(latest_signals.values())
            self.state["last_signal_flag"] = signal_flag
            self.state["last_histogram_direction"] = hist_direction
            save_state(self.symbol, self.state)

            signal_object = {
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
                "symbol": self.symbol,
                "score": score,
                "signals": latest_signals,
                "histogram": curr_hist  # ✅ Add this
            }

            return signal_object

        except Exception as e:
            print(f"❌ Exception in MACDEngine ({self.symbol}): {e}")
            return None
