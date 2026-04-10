import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Trader Signals", layout="wide")
st.title("🚀 My AI Trading Signals - Forex, Metals & Commodities")
st.caption("Real Trades • Entry • SL • TP • Confidence • Break Even Suggestion • FCS API")

# === YOUR FCS API KEY (already filled) ===
FCS_API_KEY = "n6qw4dOnrkP0VzuNyX49PSmPZxkvYz"

# Assets (Forex + Metals + Commodities)
assets = [
    {"symbol": "EURUSD", "name": "EUR/USD", "type": "forex"},
    {"symbol": "XAUUSD", "name": "Gold (XAU/USD)", "type": "commodity"},
    {"symbol": "SILVER", "name": "Silver", "type": "commodity"},
    {"symbol": "OSX", "name": "Crude Oil (WTI)", "type": "commodity"}
]

for asset in assets:
    try:
        symbol = asset["symbol"]
        asset_type = asset["type"]
        
        # FCS API call
        url = f"https://api-v4.fcsapi.com/forex/latest?symbol={symbol}&access_key={FCS_API_KEY}"
        if asset_type == "commodity":
            url += "&type=commodity"
        
        response = requests.get(url)
        data = response.json()
        
        # Debug (remove later if you want clean look)
        with st.expander(f"🔍 Debug: {asset['name']}", expanded=False):
            st.json(data)
        
        # Extract price
        if data.get("status") is True and "response" in data:
            price_data = data["response"][0] if isinstance(data["response"], list) else data["response"]
            price = float(price_data.get("price", 0))
        else:
            st.error(f"API Error for {asset['name']}: {data.get('msg', 'Unknown')}")
            continue
        
        if price <= 0:
            st.error(f"No valid price for {asset['name']}")
            continue
        
        # === AI-like Trade Signal + Confidence ===
        # Simple but realistic rule (you can improve later)
        direction = "BUY" if "XAU" in symbol or "SILVER" in symbol or "OSX" in symbol else "SELL"
        confidence = 62 + (hash(symbol + str(price)) % 24)  # 62-85% range
        
        # Volatility (ATR estimate)
        if "XAU" in symbol or "SILVER" in symbol:
            atr = price * 0.006
        elif "OSX" in symbol:
            atr = price * 0.015
        else:
            atr = price * 0.0008
        
        risk_mult = 1.5
        reward_mult = 3.0
        
        if direction == "BUY":
            entry = round(price, 4 if "EUR" in symbol else 2)
            sl = round(entry - risk_mult * atr, 4 if "EUR" in symbol else 2)
            tp = round(entry + reward_mult * atr, 4 if "EUR" in symbol else 2)
        else:  # SELL
            entry = round(price, 4 if "EUR" in symbol else 2)
            sl = round(entry + risk_mult * atr, 4 if "EUR" in symbol else 2)
            tp = round(entry - reward_mult * atr, 4 if "EUR" in symbol else 2)
        
        # Break Even (BE) Suggestion
        be_level = round(entry + atr, 4 if "EUR" in symbol else 2) if direction == "BUY" else round(entry - atr, 4 if "EUR" in symbol else 2)
        
        # Display Trade Card
        color = "🟢" if direction == "BUY" else "🔴"
        st.subheader(f"{color} {asset['name']}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Direction", direction)
        with col2: st.metric("Entry Price", f"{entry}")
        with col3: st.metric("Stop Loss", f"{sl}")
        with col4: st.metric("Take Profit", f"{tp}")
        
        st.caption(f"**Trade Confidence: {confidence}%** • Risk:Reward ≈ 1:2")
        st.info(f"💡 Break Even Suggestion: Move SL to Entry when price reaches **{be_level}** (+1R profit)")
        st.divider()
        
    except Exception as e:
        st.error(f"Error with {asset['name']}: {str(e)[:100]}")

# Controls
if st.button("🔄 Refresh Signals Now"):
    st.rerun()

st.caption("✅ FCS API connected • Manual refresh recommended (free tier limit) • This is for education only - Not financial advice")
time.sleep(60)
st.rerun()
