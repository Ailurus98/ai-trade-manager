def compute_rsi(data, window=14):
    if data.empty or 'Close' not in data:
        raise ValueError("Cannot compute RSI: missing Close price data")

    delta = data['Close'].diff()

    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    rsi = rsi.dropna()
    if rsi.empty:
        raise ValueError("Not enough price history to compute RSI")

    return float(rsi.iloc[-1])
