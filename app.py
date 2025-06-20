import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from binance.client import Client
from binance.websockets import ThreadedWebsocketManager
import time
from datetime import datetime

# Initialize session state
if 'auto_trading' not in st.session_state:
    st.session_state.auto_trading = False
if 'trades' not in st.session_state:
    st.session_state.trades = []
if 'opportunities' not in st.session_state:
    st.session_state.opportunities = []
if 'chart_data' not in st.session_state:
    st.session_state.chart_data = pd.DataFrame(columns=['timestamp', 'price', 'imbalance'])

# Binance API setup
api_key = st.secrets["BINANCE_API_KEY"]  # Store in Streamlit secrets
api_secret = st.secrets["BINANCE_API_SECRET"]
client = Client(api_key, api_secret)

# Layout configuration
st.set_page_config(layout="wide")

# CSS styling
st.markdown("""
<style>
    .stApp {
        background-color: #1a1a2e;
        color: #e6e6e6;
    }
    .stButton>button {
        background-color: #3a7bd5;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #16213e;
        color: #e6e6e6;
    }
    .stSelectbox>div>div>select {
        background-color: #16213e;
        color: #e6e6e6;
    }
    .positive {
        color: #4ecca3;
    }
    .negative {
        color: #e43f5a;
    }
    .card {
        background-color: #16213e;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #2a3a5a;
    }
</style>
""", unsafe_allow_html=True)

# Trading parameters
def trading_parameters():
    with st.container():
        st.subheader("Trading Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            initial_investment = st.number_input(
                "Initial Investment ($)", 
                min_value=100.0, 
                value=1000.0, 
                step=100.0
            )
            amount_per_trade = st.number_input(
                "Amount per Trade ($)", 
                min_value=10.0, 
                value=100.0, 
                step=10.0
            )
            stop_loss = st.number_input(
                "Stop Loss (%)", 
                min_value=0.1, 
                value=0.2, 
                step=0.1
            )
        
        with col2:
            take_profit = st.number_input(
                "Take Profit (%)", 
                min_value=0.1, 
                value=0.4, 
                step=0.1
            )
            order_book_depth = st.selectbox(
                "Order Book Depth", 
                options=[5, 10, 20], 
                index=0
            )
            leverage = st.selectbox(
                "Leverage", 
                options=[1, 5, 10, 20], 
                index=2
            )

# Imbalance thresholds
def imbalance_thresholds():
    with st.container():
        st.subheader("Imbalance Thresholds")
        
        col1, col2 = st.columns(2)
        with col1:
            buy_threshold = st.number_input(
                "Buy Imbalance Threshold (≥)", 
                min_value=0.01, 
                max_value=1.0, 
                value=0.25, 
                step=0.01
            )
        
        with col2:
            sell_threshold = st.number_input(
                "Sell Imbalance Threshold (≤)", 
                min_value=-1.0, 
                max_value=-0.01, 
                value=-0.25, 
                step=0.01
            )

# Trading status
def trading_status():
    with st.container():
        st.subheader("Futures Orderbook Imbalance Trader")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            status_color = "green" if st.session_state.auto_trading else "red"
            status_text = "ACTIVE" if st.session_state.auto_trading else "INACTIVE"
            st.markdown(f"**Auto Trading Status:** <span style='color:{status_color}'>● {status_text}</span> | **Mode:** NET", unsafe_allow_html=True)
        
        with col2:
            if st.button("Start Auto Trading" if not st.session_state.auto_trading else "Stop Auto Trading"):
                st.session_state.auto_trading = not st.session_state.auto_trading
            if st.button("Manual Refresh"):
                pass  # Add refresh logic

# Portfolio balance
def portfolio_balance():
    with st.container():
        st.subheader("Portfolio Balance")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Balance", "$1,000.00")
        
        with col2:
            st.metric("Total P&L", "$0.00 (↑ 0.00%)")

# Trade statistics
def trade_stats():
    with st.container():
        st.subheader("Trade Statistics")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Open Trades", "0")
        
        with col2:
            st.metric("Closed Trades", "N/A")

# Price chart
def price_chart():
    fig = go.Figure()
    
    if not st.session_state.chart_data.empty:
        fig.add_trace(go.Scatter(
            x=st.session_state.chart_data['timestamp'],
            y=st.session_state.chart_data['price'],
            name='Price',
            line=dict(color='#3a7bd5')
        ))
        
        fig.add_trace(go.Scatter(
            x=st.session_state.chart_data['timestamp'],
            y=st.session_state.chart_data['imbalance'],
            name='Imbalance',
            yaxis='y2',
            line=dict(color='#4ecca3')
        ))
    
    fig.update_layout(
        height=400,
        plot_bgcolor='#16213e',
        paper_bgcolor='#1a1a2e',
        font=dict(color='#e6e6e6'),
        xaxis=dict(gridcolor='#2a3a5a'),
        yaxis=dict(
            title='Price',
            gridcolor='#2a3a5a',
            side='left'
        ),
        yaxis2=dict(
            title='Imbalance',
            overlaying='y',
            side='right',
            range=[-1, 1],
            gridcolor='#2a3a5a'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Trading opportunities
def trading_opportunities():
    with st.container():
        st.subheader("Trading Opportunities")
        
        # Mock data
        data = {
            "timestamp": [
                "2026-06-17 11:31:28 UTC",
                "2026-06-17 11:31:29 UTC",
                "2026-06-17 11:31:30 UTC"
            ],
            "symbol": ["SOULSOT", "DOGELISOT", "JORDENIBUSDT"],
            "side": ["BUY", "BUY", "BUY"],
            "price": [150.785, 0.1711, 0.0117],
            "imbalance": [0.0026, 0.3353, 0.3186]
        }
        
        df = pd.DataFrame(data)
        styled_df = df.style.applymap(
            lambda x: 'color: #4ecca3' if x == 'BUY' else 'color: #e43f5a', 
            subset=['side']
        )
        
        st.dataframe(
            styled_df.format({
                "price": "{:.4f}",
                "imbalance": "{:.4f}"
            }),
            hide_index=True,
            use_container_width=True
        )

# Open trades
def open_trades():
    with st.container():
        st.subheader("Open Trades")
        
        if not st.session_state.trades:
            st.write("No open trades")
        else:
            st.dataframe(
                pd.DataFrame(st.session_state.trades),
                hide_index=True,
                use_container_width=True
            )

# WebSocket handler
def handle_socket_message(msg):
    try:
        # Process WebSocket message
        if msg['e'] == 'depthUpdate':
            # Calculate order book imbalance
            bids = pd.DataFrame(msg['b'], columns=['price', 'quantity'], dtype=float)
            asks = pd.DataFrame(msg['a'], columns=['price', 'quantity'], dtype=float)
            
            total_bid = bids['quantity'].sum()
            total_ask = asks['quantity'].sum()
            imbalance = (total_bid - total_ask) / (total_bid + total_ask)
            
            # Get current price (midpoint)
            best_bid = float(msg['b'][0][0])
            best_ask = float(msg['a'][0][0])
            price = (best_bid + best_ask) / 2
            
            # Update chart data
            new_data = pd.DataFrame({
                'timestamp': [datetime.now()],
                'price': [price],
                'imbalance': [imbalance]
            })
            
            st.session_state.chart_data = pd.concat([
                st.session_state.chart_data, 
                new_data
            ]).tail(50)  # Keep last 50 data points
            
            # Check for trading signals
            buy_threshold = st.session_state.get('buy_threshold', 0.25)
            sell_threshold = st.session_state.get('sell_threshold', -0.25)
            
            if st.session_state.auto_trading:
                if imbalance >= buy_threshold:
                    # Execute buy logic
                    st.session_state.trades.append({
                        'symbol': msg['s'],
                        'side': 'BUY',
                        'price': price,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                elif imbalance <= sell_threshold:
                    # Execute sell logic
                    st.session_state.trades.append({
                        'symbol': msg['s'],
                        'side': 'SELL',
                        'price': price,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
    
    except Exception as e:
        st.error(f"Error processing WebSocket message: {e}")

# Main app layout
def main():
    # Sidebar with parameters
    with st.sidebar:
        st.title("Trading Parameters")
        trading_parameters()
        imbalance_thresholds()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        trading_status()
        price_chart()
        
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            portfolio_balance()
        with subcol2:
            trade_stats()
    
    with col2:
        trading_opportunities()
        open_trades()
    
    # Start WebSocket connection
    if 'wm' not in st.session_state:
        st.session_state.wm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
        st.session_state.wm.start()
        
        # Subscribe to BTCUSDT order book
        st.session_state.wm.start_depth_socket(
            symbol='BTCUSDT',
            callback=handle_socket_message,
            interval=Client.KLINE_INTERVAL_1MINUTE
        )

if __name__ == "__main__":
    main()
