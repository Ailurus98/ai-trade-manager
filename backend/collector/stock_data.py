import yfinance as yf
import time
from datetime import datetime, timedelta

try:
    from pandas_datareader import data as web
except Exception:
    web = None


def _fetch_from_stooq(symbol):
    if web is None:
        return None

    end = datetime.utcnow()
    start = end - timedelta(days=180)

    stooq_symbols = [symbol]
    if symbol.upper().endswith(".NS"):
        stooq_symbols.append(symbol[:-3] + ".IN")

    for stooq_symbol in stooq_symbols:
        try:
            df = web.DataReader(stooq_symbol, "stooq", start, end)
            if df is None or df.empty:
                continue
            df = df.sort_index()
            return df
        except Exception:
            continue

    return None


def fetch_stock(symbol, period="1mo", retries=1, pause_seconds=1.0):
    """Fetch stock data with fast defaults (1-month window, 1 retry)."""
    stock = yf.Ticker(symbol)

    for attempt in range(retries + 1):
        try:
            df = stock.history(period=period)
            if not df.empty:
                return df

            df = yf.download(symbol, period=period, progress=False, threads=False)
            if not df.empty:
                return df

            stooq_df = _fetch_from_stooq(symbol)
            if stooq_df is not None and not stooq_df.empty:
                return stooq_df

            raise ValueError("No market data returned")
        except Exception as exc:
            is_rate_limit = exc.__class__.__name__ == "YFRateLimitError"
            if is_rate_limit and attempt < retries:
                time.sleep(pause_seconds * (attempt + 1))
                continue

            if not is_rate_limit and attempt < retries:
                time.sleep(0.5 * (attempt + 1))
                continue

            if is_rate_limit:
                stooq_df = _fetch_from_stooq(symbol)
                if stooq_df is not None and not stooq_df.empty:
                    return stooq_df

                raise ValueError(
                    "Yahoo Finance rate limit reached. Please wait a minute and try again."
                ) from exc

            raise ValueError(
                "Unable to fetch market data right now. Please try again shortly."
            ) from exc


def fetch_fundamentals(symbol):
    """Fetch key fundamentals from yfinance .info in a single call.

    Returns a dict with market_cap, pe_ratio, pb_ratio, industry_pe,
    debt_to_equity, roe, dividend_yield, book_value, face_value,
    fifty_two_week_high, fifty_two_week_low, day_high, day_low,
    current_price, previous_close.
    """
    try:
        stock = yf.Ticker(symbol)
        info = stock.info or {}
    except Exception:
        info = {}

    def _get(key, default=None):
        val = info.get(key, default)
        return val if val is not None else default

    current = _get("currentPrice") or _get("regularMarketPrice") or _get("previousClose")
    prev_close = _get("previousClose") or _get("regularMarketPreviousClose")

    return {
        "current_price": current,
        "previous_close": prev_close,
        "day_high": _get("dayHigh") or _get("regularMarketDayHigh"),
        "day_low": _get("dayLow") or _get("regularMarketDayLow"),
        "fifty_two_week_high": _get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": _get("fiftyTwoWeekLow"),
        "market_cap": _get("marketCap"),
        "pe_ratio": _get("trailingPE"),
        "forward_pe": _get("forwardPE"),
        "pb_ratio": _get("priceToBook"),
        "industry_pe": _get("industryPe") or _get("sectorPe"),
        "debt_to_equity": _get("debtToEquity"),
        "roe": _get("returnOnEquity"),
        "dividend_yield": _get("dividendYield"),
        "book_value": _get("bookValue"),
        "face_value": _get("faceValue"),
        "eps": _get("trailingEps"),
        "sector": _get("sector"),
        "industry": _get("industry"),
        "company_name": _get("longName") or _get("shortName"),
    }


def fetch_financials(symbol):
    """Fetch yearly financials (Revenue, Net Income, Total Equity / Net Worth).

    Returns a dict with keys 'years', 'revenue', 'net_income', 'net_worth',
    each as a list aligned by index.
    """
    result = {"years": [], "revenue": [], "net_income": [], "net_worth": []}

    try:
        stock = yf.Ticker(symbol)

        # Income statement → Revenue + Net Income
        income = stock.financials
        if income is not None and not income.empty:
            years = []
            revenue = []
            net_income = []
            for col in income.columns:
                yr = col.year if hasattr(col, "year") else str(col)[:4]
                years.append(str(yr))

                # Revenue
                rev = None
                for key in ["Total Revenue", "Revenue", "Operating Revenue"]:
                    if key in income.index:
                        val = income.loc[key, col]
                        if val is not None and str(val) != "nan":
                            rev = float(val)
                            break
                revenue.append(rev)

                # Net Income
                ni = None
                for key in ["Net Income", "Net Income Common Stockholders",
                             "Net Income From Continuing Operations"]:
                    if key in income.index:
                        val = income.loc[key, col]
                        if val is not None and str(val) != "nan":
                            ni = float(val)
                            break
                net_income.append(ni)

            result["years"] = list(reversed(years))
            result["revenue"] = list(reversed(revenue))
            result["net_income"] = list(reversed(net_income))

        # Balance sheet → Net Worth (Total Stockholder Equity)
        balance = stock.balance_sheet
        if balance is not None and not balance.empty:
            net_worth = []
            b_years = []
            for col in balance.columns:
                yr = col.year if hasattr(col, "year") else str(col)[:4]
                b_years.append(str(yr))

                nw = None
                for key in ["Total Stockholder Equity", "Stockholders Equity",
                             "Common Stock Equity", "Total Equity Gross Minority Interest"]:
                    if key in balance.index:
                        val = balance.loc[key, col]
                        if val is not None and str(val) != "nan":
                            nw = float(val)
                            break
                net_worth.append(nw)

            result["net_worth"] = list(reversed(net_worth))
            # If years weren't set from income statement, use balance sheet years
            if not result["years"]:
                result["years"] = list(reversed(b_years))

    except Exception:
        pass

    return result


def fetch_index_quotes(index_map):
    """Fetch latest price + daily change for multiple indices in one batch call."""
    if not index_map:
        return {}

    tickers_str = " ".join(index_map.values())
    try:
        df = yf.download(
            tickers_str,
            period="2d",
            progress=False,
            threads=True,
            group_by="ticker",
        )
    except Exception:
        return {}

    results = {}
    for display_name, ticker in index_map.items():
        try:
            if len(index_map) == 1:
                close_col = df["Close"]
            else:
                close_col = df[(ticker, "Close")]

            close_col = close_col.dropna()
            if len(close_col) < 1:
                continue

            latest = float(close_col.iloc[-1])
            if len(close_col) >= 2:
                prev = float(close_col.iloc[-2])
                change_pct = ((latest - prev) / prev) * 100 if prev else 0.0
            else:
                change_pct = 0.0

            results[display_name] = {"price": latest, "change_pct": round(change_pct, 2)}
        except Exception:
            continue

    return results
