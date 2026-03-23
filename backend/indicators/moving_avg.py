def moving_average(data, window=20):
    if data.empty or 'Close' not in data:
        raise ValueError("Cannot compute moving average: missing Close price data")

    ma = data['Close'].rolling(window).mean().dropna()
    if ma.empty:
        raise ValueError("Not enough price history to compute moving average")

    return float(ma.iloc[-1])
