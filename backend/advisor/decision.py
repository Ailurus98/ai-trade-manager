def make_decision(rsi, sentiment):

    if rsi < 30 and sentiment == "Positive":
        return "BUY"

    elif rsi > 70 and sentiment == "Negative":
        return "SELL"

    else:
        return "HOLD"
