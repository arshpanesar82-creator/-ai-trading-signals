for symbol in assets:
    try:
        # Fix 1: Proper symbols for CurrencyFreaks (base=USD)
        if symbol == "EURUSD":
            api_symbol = "EUR"
        elif symbol == "XAUUSD":
            api_symbol = "XAU"
        elif symbol == "XAGUSD":
            api_symbol = "XAG"
        else:
            api_symbol = symbol.replace("USD", "")  # fallback

        url = f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={API_KEY}&symbols={api_symbol}&base=USD"
        response = requests.get(url).json()
        
        rates = response.get("rates", {})
        raw_rate = float(rates.get(api_symbol, 0))
        
        if raw_rate == 0:
            st.error(f"No rate returned for {symbol}")
            continue
        
        # Fix 2: Convert to proper trading price
        if api_symbol in ["XAU", "XAG"]:
            price = round(1 / raw_rate, 2)   # Gold/Silver in USD per ounce
        else:
            price = round(1 / raw_rate, 4)   # Forex pairs like EURUSD
        
        # === Rest of your signal logic (direction, confidence, SL, TP) ===
        direction = "BUY" if "XAU" in symbol else "SELL" if "EUR" in symbol else "HOLD"
        confidence = 65 + (hash(symbol) % 25)
        
        atr = price * 0.006   # simple volatility estimate (0.6%)
        
        risk_mult = 1.5
        reward_mult = 3.0
        
        if direction == "BUY":
            entry = price
            sl = round(entry - (risk_mult * atr), 2 if "XAU" in symbol or "XAG" in symbol else 4)
            tp = round(entry + (reward_mult * atr), 2 if "XAU" in symbol or "XAG" in symbol else 4)
        elif direction == "SELL":
            entry = price
            sl = round(entry + (risk_mult * atr), 2 if "XAU" in symbol or "XAG" in symbol else 4)
            tp = round(entry - (reward_mult * atr), 2 if "XAU" in symbol or "XAG" in symbol else 4)
        else:
            entry = price
            sl = tp = "N/A"
        
        # Display
        color = "🟢" if direction == "BUY" else "🔴" if direction == "SELL" else "⚪"
        st.subheader(f"{color} {symbol}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Direction", direction)
        with col2: st.metric("Entry Price", f"{entry:.2f}" if "XAU" in symbol or "XAG" in symbol else f"{entry:.4f}")
        with col3: st.metric("Stop Loss", sl if sl != "N/A" else "N/A")
        with col4: st.metric("Take Profit", tp if tp != "N/A" else "N/A")
        
        st.caption(f"**Confidence: {confidence}%** • Risk:Reward ≈ 1:2")
        st.divider()
        
    except Exception as e:
        st.error(f"Error with {symbol}: {str(e)[:100]}")
