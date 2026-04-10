import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Trader Signals", layout="wide")
st.title("🚀 My AI Trading Signals - Forex, Metals & Commodities")
st.caption("Entry • SL • TP • Confidence % • Built on iPad")

# === REPLACE THIS WITH YOUR REAL KEY ===
API_KEY = "YOUR_ACTUAL_CURRENCYFREAKS_KEY_HERE"   # ← Put your key here

assets = ["EURUSD", "XAUUSD", "XAGUSD"]

for symbol in assets:
    try:
        # Map to CurrencyFreaks symbol
        if symbol == "EURUSD":
            api_symbol = "EUR"
        elif symbol == "XAUUSD":
            api_symbol = "XAU"
        elif symbol == "XAGUSD":
            api_symbol = "XAG"
        else:
            api_symbol = symbol.replace("USD", "")

        url = f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={API_KEY}&symbols={api_symbol}&base=USD"
        
        response = requests.get(url)
        data = response.json()
        
        # Debug: Show raw response (helpful for troubleshooting)
        with st.expander(f"Debug: Raw API response for {symbol}", expanded=False):
            st.json(data)
        
        rates = data.get("rates", {})
        raw_rate = float(rates.get(api_symbol, 0))
        
        if raw_rate <= 0:
            st.error(f"No valid rate returned for {symbol} (raw_rate = {raw_rate})")
            st.info(f"API URL tried: {url}")
            continue
        
        # Convert to proper price
        if api_symbol in ["XAU", "XAG"]:
            price = round(1 / raw_rate, 2)
        else:
            price = round(1 / raw_rate, 4)
        
        # Placeholder signals (we'll make real AI later)
        direction = "BUY" if "XAU" in symbol else "SELL" if "EUR" in symbol else "HOLD"
        confidence = 68 + (hash(symbol) % 22)
        
        atr = price * 0.006  # simple volatility
        
        risk_mult = 1.5
        reward_mult = 3.0
        
        if direction == "BUY":
            entry = price
            sl = round(entry - risk_mult * atr, 2 if api_symbol in ["XAU","XAG"] else 4)
            tp = round(entry + reward_mult * atr, 2 if api_symbol in ["XAU","XAG"] else 4)
        elif direction == "SELL":
            entry = price
            sl = round(entry + risk_mult * atr, 2 if api_symbol in ["XAU","XAG"] else 4)
            tp = round(entry - reward_mult * atr, 2 if api_symbol in ["XAU","XAG"] else 4)
        else:
            entry = price
            sl = tp = "N/A"
        
        color = "🟢" if direction == "BUY" else "🔴" if direction == "SELL" else "⚪"
        st.subheader(f"{color} {symbol}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Direction", direction)
        with col2: st.metric("Entry Price", f"{entry:.2f}" if api_symbol in ["XAU","XAG"] else f"{entry:.4f}")
        with col3: st.metric("Stop Loss", sl if sl != "N/A" else "N/A")
        with col4: st.metric("Take Profit", tp if tp != "N/A" else "N/A")
        
        st.caption(f"**Confidence: {confidence}%** • Risk:Reward ≈ 1:2")
        st.divider()
        
    except Exception as e:
        st.error(f"Error with {symbol}: {str(e)}")

if st.button("🔄 Refresh Signals Now"):
    st.rerun()

st.caption("Auto-refreshing every 60s • Education only - Not financial advice")
time.sleep(60)
st.rerun()
