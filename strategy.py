import pandas as pd
import pandas_ta as ta

def apply_indicators(df: pd.DataFrame):
    df['EMA9'] = ta.ema(df['close'], length=9)
    df['EMA18'] = ta.ema(df['close'], length=18)
    macd = ta.macd(df['close'])
    df = pd.concat([df, macd], axis=1)

    atr = ta.atr(df['high'], df['low'], df['close'], length=10)
    hl2 = (df['high'] + df['low']) / 2
    df['supertrend_long'] = hl2 - 3 * atr
    df['supertrend_short'] = hl2 + 3 * atr

    return df

def generate_signal(df: pd.DataFrame):
    last = df.iloc[-1]
    if last['EMA9'] > last['EMA18'] and last['MACD_12_26_9'] > last['MACDs_12_26_9']:
        return "BUY"
    elif last['EMA9'] < last['EMA18'] and last['MACD_12_26_9'] < last['MACDs_12_26_9']:
        return "SELL"
    return "HOLD"
