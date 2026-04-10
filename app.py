import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Trader Signals", layout="wide")
st.title("🚀 My AI Trading Signals - Forex, Metals & Commodities")
st.caption("With Entry Price • Stop Loss • Take Profit • Confidence % • Built on iPad")

# === ADD YOUR API KEY HERE (or better, use Streamlit Secrets) ===
API_KEY = "YOUR_CURRENCYFREAKS_API_KEY_HERE"   # ← Replace with your real key from currencyfreaks.com

# List of assets we want signals for
assets = ["EURUSD", "XAUUSD", "XAGUSD"]

for symbol in assets:
    try:
        # Map to CurrencyFreaks symbols (they use XAU, XAG, EUR etc.)
        if symbol == "EURUSD":
            api_symbol = "EUR"
        elif symbol == "XAUUSD":
            api_symbol = "XAU"
        elif symbol == "XAGUSD":
            api_symbol = "XAG"
        else:
            api_symbol = symbol.replace("USD", "")

        # Call the API correctly
        url = f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={API_KEY}&symbols={api_symbol}&base=USD"
        response = requests.get(url).json()
        
        rates = response.get("rates", {})
        raw_rate = float(rates.get(api_symbol, 0))
        
        if raw_rate <= 0:
            st.error(f"No valid rate for {symbol}")
            continue
        
        # Convert to proper trading price
        if api_symbol in ["XAU", "XAG"]:
            price = round(1 / raw_rate, 2)   # Gold/Silver in USD
        else:
            price = round(1 / raw_rate, 4)   # Forex like EURUSD
        
        # Simple placeholder signal (replace later with real AI)
        direction = "BUY" if "XAU" in symbol else "SELL" if "EUR" in symbol else "HOLD"
        confidence = 68 + (hash(symbol) % 22)
        
        # Simple ATR estimate (volatility)
        atr = price * 0.006
        
        risk_mult = 1.5
        reward_mult = 3.0
        
        if direction == "BUY":
            entry = price
            sl = round(entry - (risk_mult * atr), 2 if api_symbol in ["XAU","XAG"] else 4)
            tp = round(entry + (reward_mult * atr), 2 if api_symbol in ["XAU","XAG"] else 4)
        elif direction == "SELL":
            entry = price
            sl = round(entry + (risk_mult * atr), 2 if api_symbol in ["XAU","XAG"] else 4)
            tp = round(entry - (reward_mult * atr), 2 if api_symbol in ["XAU","XAG"] else 4)
        else:
            entry = price
            sl = tp = "N/A"
        
        # Nice display
        color = "🟢" if direction == "BUY" else "🔴" if direction == "SELL" else "⚪"
        st.subheader(f"{color} {symbol}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Direction", direction)
        with col2:
            st.metric("Entry Price", f"{entry:.2f}" if api_symbol in ["XAU","XAG"] else f"{entry:.4f}")
        with col3:
            st.metric("Stop Loss", sl if sl != "N/A" else "N/A")
        with col4:
            st.metric("Take Profit", tp if tp != "N/A" else "N/A")
        
        st.caption(f"**Confidence: {confidence}%** • Approx Risk:Reward 1:2")
        st.divider()
        
    except Exception as e:
        st.error(f"Error fetching {symbol}: {str(e)[:120]}")

# Controls
if st.button("🔄 Refresh Signals Now"):
    st.rerun()

st.caption("Auto-refreshing every 60 seconds • This is for education only - Not financial advice")
time.sleep(60)
st.rerun()
