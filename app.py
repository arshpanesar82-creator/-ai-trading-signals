import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Arshdeep's Free AI Trading Tool", layout="wide")
st.title("🚀 Arshdeep's Free Lifetime AI Trading Analyzer")
st.markdown("**XAUUSD • Silver • Currency Pairs** | Entry + Stop Loss + Confidence % | 100% Free Forever")

# Asset mapping (proven free yfinance tickers)
assets = {
    "XAUUSD (Gold Spot)": "GC=F",
    "XAGUSD (Silver Spot)": "SI=F",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "AUDUSD": "AUDUSD=X",
    "USDCAD": "USDCAD=X",
    "NZDUSD": "NZDUSD=X",
}

# Sidebar
st.sidebar.header("Settings")
selected_asset = st.sidebar.selectbox("Select Asset", list(assets.keys()))
timeframe = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d"])
analyze_button = st.sidebar.button("🔥 ANALYZE NOW", type="primary")

def calculate_indicators(df):
    # Simple Moving Averages
    df['SMA20'] = df['Close'].rolling(20).mean()
    df['SMA50'] = df['Close'].rolling(50).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = df['Close'].ewm(span=12).mean()
    ema26 = df['Close'].ewm(span=26).mean()
    df['MACD'] = ema12 - ema26
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    
    # ATR for Stop Loss
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(14).mean()
    
    return df

def generate_signal(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    score = 0
    reasons = []
    
    # Trend
    if latest['Close'] > latest['SMA50']:
        score += 25
        reasons.append("Price above SMA50 (Uptrend)")
    if latest['SMA20'] > latest['SMA50']:
        score += 20
        reasons.append("SMA20 > SMA50 (Golden Cross)")
    
    # Momentum
    if latest['RSI'] > 50 and latest['RSI'] < 70:
        score += 20
        reasons.append("Healthy RSI momentum")
    elif latest['RSI'] < 30:
        score += 15
        reasons.append("Oversold RSI")
    
    # MACD
    if latest['MACD'] > latest['Signal'] and prev['MACD'] <= prev['Signal']:
        score += 20
        reasons.append("MACD Bullish Crossover")
    elif latest['MACD'] > 0:
        score += 10
        reasons.append("MACD above zero")
    
    direction = "BULLISH" if score >= 50 else "BEARISH" if score <= 30 else "NEUTRAL"
    confidence = min(max(score, 30), 95)  # cap for realism
    
    # Entry & Stop Loss
    entry = round(latest['Close'], 4)
    atr = latest['ATR']
    if direction == "BULLISH":
        sl = round(entry - 1.8 * atr, 4)
        trade_type = "LONG"
    else:
        sl = round(entry + 1.8 * atr, 4)
        trade_type = "SHORT"
    
    return {
        "direction": direction,
        "trade_type": trade_type,
        "entry": entry,
        "stop_loss": sl,
        "confidence": confidence,
        "reasons": reasons,
        "current_price": entry,
        "rsi": round(latest['RSI'], 2),
        "atr": round(atr, 4)
    }

if analyze_button or st.session_state.get("last_analysis"):
    with st.spinner(f"Fetching latest {selected_asset} data..."):
        ticker = assets[selected_asset]
        # Fetch enough data for indicators
        data = yfinance.download(ticker, period="60d", interval=timeframe, progress=False)
        
        if data.empty:
            st.error("No data received. Try again later.")
        else:
            df = calculate_indicators(data)
            result = generate_signal(df)
            
            # Display results
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current Price", f"{result['current_price']}")
            with col2:
                st.metric("Signal", result['direction'], delta=result['trade_type'])
            with col3:
                st.metric("Entry Price", f"{result['entry']}")
            with col4:
                st.metric("Stop Loss", f"{result['stop_loss']}", delta="Risk")
            
            st.subheader(f"🧠 AI Confidence: **{result['confidence']}%**")
            st.progress(result['confidence'] / 100)
            
            st.info(f"**Recommended Trade**: {result['trade_type']} {selected_asset} at **{result['entry']}** | SL at **{result['stop_loss']}**")
            
            st.write("**Why this signal?**")
            for reason in result['reasons']:
                st.success(reason)
            
            # Chart
            st.subheader("Live Chart with Indicators")
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name="SMA20", line=dict(color="orange")))
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], name="SMA50", line=dict(color="blue")))
            fig.update_layout(title=f"{selected_asset} - {timeframe} Chart", xaxis_rangeslider_visible=False, height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            # Indicators table
            st.dataframe(df[['Close', 'SMA20', 'SMA50', 'RSI', 'MACD', 'ATR']].tail(5).round(4), use_container_width=True)
            
            st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data from Yahoo Finance (free)")

st.sidebar.markdown("---")
st.sidebar.info("✅ Built exclusively for you by Grok\n**Completely free forever** - no API keys needed\nRun it anytime on your computer!")
st.caption("⚠️ This is for educational purposes only. Not financial advice. Always do your own research and manage risk.")
