# 📄 utils/state_cache.py

import json
from pathlib import Path

STATE_DIR = Path("state")
STATE_DIR.mkdir(exist_ok=True)

def get_cache_path(symbol: str):
    filename = f"{symbol.replace('/', '')}_cache.json"
    return STATE_DIR / filename

def load_state(symbol: str):
    path = get_cache_path(symbol)
    if not path.exists():
        return None
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Failed to load state for {symbol}: {e}")
        return None

def save_state(symbol: str, state: dict):
    path = get_cache_path(symbol)
    try:
        with open(path, "w") as f:
            json.dump(state, f, indent=2, default=str)
    except Exception as e:
        print(f"❌ Failed to save state for {symbol}: {e}")
