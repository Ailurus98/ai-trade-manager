import yfinance as yf


def fetch_stock(symbol):
    stock = yf.Ticker(symbol)
    df = stock.history(period="3mo")
    return df
