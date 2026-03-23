try:
    from backend.collector.stock_data import fetch_stock
    from backend.collector.news_data import fetch_news
    from backend.indicators.rsi import compute_rsi
    from backend.indicators.moving_avg import moving_average
    from backend.ai.sentiment import get_sentiment
    from backend.ai.reasoning import generate_reason
    from backend.advisor.decision import make_decision
except ModuleNotFoundError:
    # Fallback for running this file directly: python backend/main.py
    from collector.stock_data import fetch_stock
    from collector.news_data import fetch_news
    from indicators.rsi import compute_rsi
    from indicators.moving_avg import moving_average
    from ai.sentiment import get_sentiment
    from ai.reasoning import generate_reason
    from advisor.decision import make_decision


def run_pipeline(symbol):

    data = fetch_stock(symbol)

    rsi = compute_rsi(data)
    ma = moving_average(data)

    news = fetch_news()
    sentiment = get_sentiment(news)

    decision = make_decision(rsi, sentiment)
    reason = generate_reason(rsi, sentiment)

    return {
        "symbol": symbol,
        "rsi": rsi,
        "moving_avg": ma,
        "sentiment": sentiment,
        "decision": decision,
        "reason": reason
    }


if __name__ == "__main__":
    result = run_pipeline("RELIANCE.NS")
    print(result)
