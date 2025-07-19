# utils/bootstrap_manager.py

import os
import pandas as pd
from utils.historical_loader import fetch_historical_ohlcv

BOOTSTRAP_DIR = "data/bootstrap"

def get_bootstrap_path(symbol: str, timeframe: str) -> str:
    safe_symbol = symbol.replace("/", "_")
    return os.path.join(BOOTSTRAP_DIR, f"{safe_symbol}_{timeframe}.csv")

def load_or_fetch_bootstrap(symbol: str, timeframe: str, limit: int = 2000) -> pd.DataFrame:
    """
    Loads cached data from CSV if available; otherwise fetches fresh and saves to CSV.

    Returns:
        pd.DataFrame: OHLCV data
    """
    os.makedirs(BOOTSTRAP_DIR, exist_ok=True)
    filepath = get_bootstrap_path(symbol, timeframe)

    if os.path.exists(filepath):
        try:
            df = pd.read_csv(filepath, parse_dates=['timestamp'])
            print(f"✅ Loaded cached bootstrap for {symbol} {timeframe}")
            return df
        except Exception as e:
            print(f"⚠️  Failed to load cache for {symbol}: {e} – fetching fresh")

    # If not exists or loading failed → fetch and save
    df = fetch_historical_ohlcv(symbol, timeframe, limit)
    df.to_csv(filepath, index=False)
    print(f"📥 Fetched and cached bootstrap for {symbol} {timeframe}")
    return df
