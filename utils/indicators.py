import pandas as pd

MACD_SETS = [
    {"fast": 12, "slow": 26, "signal": 9, "label": "L1"},
    {"fast": 36, "slow": 78, "signal": 27, "label": "L2"},
    {"fast": 72, "slow": 156, "signal": 54, "label": "L3"},
    {"fast": 144, "slow": 312, "signal": 108, "label": "L4"},
    {"fast": 432, "slow": 936, "signal": 324, "label": "L5"},
    {"fast": 900, "slow": 1950, "signal": 675, "label": "L6"},
    {"fast": 4500, "slow": 9750, "signal": 3375, "label": "L7"},
]

def compute_macd(df: pd.DataFrame, fast: int, slow: int, signal: int):
    """
    Compute MACD and signal line.
    Assumes df has a column 'close'
    Returns a DataFrame with columns: macd_line, signal_line, histogram
    """
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    return pd.DataFrame({
        'macd_line': macd_line,
        'signal_line': signal_line,
        'histogram': histogram
    })
