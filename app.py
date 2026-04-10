import streamlit as st
import requests
import time
import pandas as pd

st.set_page_config(page_title="AI Trader Signals", layout="wide")
st.title("🚀 My AI Trading Signals - Forex, Metals & Commodities")
st.caption("With Entry Price • Stop Loss • Take Profit • Confidence %")

# === YOUR API KEY (add as secret in Streamlit Cloud settings) ===
API_KEY = st.secrets.get("CURRENCYFREAKS_KEY", "YOUR_KEY_HERE")  # Better: use secrets

assets = ["EURUSD", "XAUUSD", "XAGUSD"]  # Add more (e.g. oil if supported)

for symbol in assets:
    try:
        # Fetch latest price
        url = f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={API_KEY}&symbols={symbol.replace('USD','') if 'USD' in symbol else symbol}"
        response = requests.get(url).json()
        
        # Extract price (adapt based on exact response - test once)
        base = "USD"
        rate_key = symbol.replace("USD", "") if "USD" in symbol else symbol
        price = float(response.get("rates", {}).get(rate_key, 0))
        
        if price == 0:
            st.error(f"Could not get price for {symbol}")
            continue
        
        # === Fake/Placeholder Signal + Confidence (replace with your model later) ===
        direction = "BUY" if "XAU" in symbol else "SELL" if "EUR" in symbol else "HOLD"
        confidence = 65 + (hash(symbol) % 25)  # Demo value
        
        # === Simple ATR simulation (in real version fetch history and calculate) ===
        # For demo: assume ATR ~ 0.5% to 1% of price (tweak per asset)
        atr = price * 0.006  # Example: 0.6% volatility
        
        # Calculate SL and TP
        risk_multiplier = 1.5
        reward_multiplier = 3.0
        
        if direction == "BUY":
            entry = price
            sl = round(entry - (risk_multiplier * atr), 4 if "USD" in symbol and len(symbol)<7 else 2)
            tp = round(entry + (reward_multiplier * atr), 4 if "USD" in symbol and len(symbol)<7 else 2)
        elif direction == "SELL":
            entry = price
            sl = round(entry + (risk_multiplier * atr), 4 if "USD" in symbol and len(symbol)<7 else 2)
            tp = round(entry - (reward_multiplier * atr), 4 if "USD" in symbol and len(symbol)<7 else 2)
        else:
            entry = price
            sl = "N/A"
            tp = "N/A"
        
        # Display nicely
        color = "🟢" if direction == "BUY" else "🔴" if direction == "SELL" else "⚪"
        st.subheader(f"{color} {symbol}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Direction", direction)
        with col2:
            st.metric("Entry Price", f"{entry:.4f}" if "USD" in symbol and len(symbol)<7 else f"{entry:.2f}")
        with col3:
            st.metric("Stop Loss", f"{sl}" if sl != "N/A" else "N/A")
        with col4:
            st.metric("Take Profit", f"{tp}" if tp != "N/A" else "N/A")
        
        st.caption(f"Confidence: **{confidence}%** • Risk:Reward ≈ 1:{reward_multiplier/risk_multiplier}")
        
        st.divider()
        
    except Exception as e:
        st.write(f"Error with {symbol}: {e}")

# Refresh button + auto
if st.button("🔄 Refresh Signals Now"):
    st.rerun()

st.caption("Auto-refreshing every 60 seconds • Not financial advice")
time.sleep(60)
st.rerun()
