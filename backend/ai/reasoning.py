def generate_reason(rsi, sentiment):

    reason = []

    if rsi < 30:
        reason.append("Stock is oversold (RSI low)")
    elif rsi > 70:
        reason.append("Stock is overbought (RSI high)")
    else:
        reason.append("RSI is in normal range")

    if sentiment == "Positive":
        reason.append("News sentiment is positive")
    elif sentiment == "Negative":
        reason.append("News sentiment is negative")

    return " | ".join(reason)
