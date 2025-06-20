import streamlit as st
import asyncio
import threading
from binance_ws import get_kline_data, get_df
from strategy import apply_indicators, generate_signal
import time

st.set_page_config(layout="wide")
st.title("📊 Futures Orderbook Imbalance Bot (Live)")

# Start background WebSocket
def start_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(get_kline_data())

t = threading.Thread(target=start_loop)
t.start()

# Main loop
while True:
    df = get_df()
    if len(df) > 30:
        df = apply_indicators(df)
        signal = generate_signal(df)

        st.subheader("📈 Latest Signal")
        st.metric("Action", signal)

        st.subheader("📊 Price Chart")
        st.line_chart(df[['close', 'EMA9', 'EMA18']])

        st.subheader("🔍 MACD")
        st.line_chart(df[['MACD_12_26_9', 'MACDs_12_26_9']])
    else:
        st.warning("Waiting for data...")

    time.sleep(10)
