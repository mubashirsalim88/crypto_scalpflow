# 📄 core/macd_engine.py

import pandas as pd
from utils.indicators import MACD_SETS, compute_macd
from utils.bootstrap_manager import load_or_fetch_bootstrap
from utils.historical_loader import fetch_historical_ohlcv
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

            for macd_set in MACD_SETS:
                macd = compute_macd(df, macd_set["fast"], macd_set["slow"], macd_set["signal"])
                recent_macd = macd.iloc[-2:]

                prev_hist = recent_macd['histogram'].iloc[0]
                curr_hist = recent_macd['histogram'].iloc[1]

                if prev_hist < 0 and curr_hist > 0:
                    signal = +1
                elif prev_hist > 0 and curr_hist < 0:
                    signal = -1
                else:
                    signal = 0

                latest_signals[macd_set["label"]] = signal

            score = sum(latest_signals.values())

            signal_object = {
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
                "symbol": self.symbol,
                "score": score,
                "signals": latest_signals
            }

            return signal_object

        except Exception as e:
            print(f"❌ Exception in MACDEngine ({self.symbol}): {e}")
            return None
