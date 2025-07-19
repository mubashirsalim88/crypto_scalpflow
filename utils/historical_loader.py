# utils/historical_loader.py

import ccxt
import pandas as pd
import time
from datetime import datetime

def fetch_historical_ohlcv(symbol: str, timeframe: str, limit: int = 2000, max_retries: int = 5):
    """
    Fetches historical OHLCV data for a given symbol and timeframe from Binance using CCXT.

    Args:
        symbol (str): e.g., 'BTC/USDT'
        timeframe (str): e.g., '5m', '1h', etc.
        limit (int): Number of candles to fetch (default 2000).
        max_retries (int): Max retries if Binance rate limits or fails.

    Returns:
        pd.DataFrame: DataFrame with columns: ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    """
    binance = ccxt.binance()
    attempt = 0

    while attempt < max_retries:
        try:
            raw = binance.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(raw, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
            return df
        except Exception as e:
            print(f"[Retry {attempt+1}/{max_retries}] Error fetching {symbol} {timeframe} candles: {e}")
            attempt += 1
            time.sleep(3)
    
    raise RuntimeError(f"Failed to fetch OHLCV for {symbol} after {max_retries} retries.")
