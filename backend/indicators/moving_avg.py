def moving_average(data, window=20):
    return data['Close'].rolling(window).mean().iloc[-1]
