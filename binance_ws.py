import asyncio
import websockets
import json
from collections import deque
import pandas as pd

# Store last N klines
candles = deque(maxlen=100)

async def get_kline_data(symbol="btcusdt", interval="1m"):
    url = f"wss://fstream.binance.com/ws/{symbol}@kline_{interval}"
    async with websockets.connect(url) as ws:
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            k = data['k']
            candle = {
                "time": k['t'],
                "open": float(k['o']),
                "high": float(k['h']),
                "low": float(k['l']),
                "close": float(k['c']),
                "volume": float(k['v']),
            }
            candles.append(candle)
            await asyncio.sleep(0.1)

def get_df():
    return pd.DataFrame(candles)
