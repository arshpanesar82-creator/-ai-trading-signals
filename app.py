import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Trader Signals", layout="wide")
st.title("🚀 My AI Trading Signals - Forex, Metals & Commodities")
st.caption("Entry • SL • TP • Confidence % • Built on iPad")

# === YOUR GOLDAPI KEY (already filled) ===
GOLD_API_KEY = "goldapi-1feasmnsszmqq-io"

assets = ["XAUUSD", "XAGUSD", "EURUSD"]

for symbol in assets:
    try:
        if symbol in ["XAUUSD", "XAGUSD"]:
            # GoldAPI.io for metals - direct price
            metal = symbol[:3]  # XAU or XAG
            url = f"https://www.goldapi.io/api/{metal}/USD"
            headers = {"x-access-token": GOLD_API_KEY}
            response = requests.get(url, headers=headers)
            data = response.json()
            
            price = float(data.get("price", 0))
            
            if price <= 0:
                st.error(f"No price returned for {symbol}. Response: {data.get('error', 'Unknown')}")
                continue
                
            # Show debug for metals
            with st.expander(f"Debug: {symbol} raw data", expanded=False):
                st.json(data)
                
        else:
            # Temporary demo for EURUSD (we'll replace with real forex API next)
            st.info("EURUSD using demo price (add free forex API in next step)")
            price = 1.0850   # Replace with real later
        
        # === Signal + SL/TP Logic ===
        direction = "BUY" if "XAU" in symbol else "SELL" if "EUR" in symbol else "HOLD"
        confidence = 72 + (hash(symbol) % 18)   # Placeholder confidence
        
        # Volatility (ATR estimate)
        atr = price * 0.006 if "XAU" in symbol or "XAG" in symbol else price * 0.0008
        
        risk_mult = 1.5
        reward_mult = 3.0
        
        if direction == "BUY":
            entry = round(price, 2)
            sl = round(entry - risk_mult * atr, 2)
            tp = round(entry + reward_mult * atr, 2)
        elif direction == "SELL":
            entry = round(price, 2)
            sl = round(entry + risk_mult * atr, 2)
            tp = round(entry - reward_mult * atr, 2)
        else:
            entry = round(price, 2)
            sl = tp = "N/A"
        
        # Display
        color = "🟢" if direction == "BUY" else "🔴" if direction == "SELL" else "⚪"
        st.subheader(f"{color} {symbol}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Direction", direction)
        with col2: st.metric("Entry Price", f"{entry:.2f}")
        with col3: st.metric("Stop Loss", sl if sl != "N/A" else "N/A")
        with col4: st.metric("Take Profit", tp if tp != "N/A" else "N/A")
        
        st.caption(f"**Confidence: {confidence}%** • Risk:Reward ≈ 1:2")
        st.divider()
        
    except Exception as e:
        st.error(f"Error with {symbol}: {str(e)[:120]}")

if st.button("🔄 Refresh Signals Now"):
    st.rerun()

st.caption("Auto-refreshing every 60s • Education only - Not financial advice • GoldAPI free tier: 100 req/month")
time.sleep(60)
st.rerun()
