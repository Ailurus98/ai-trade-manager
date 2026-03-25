def filter_nifty200() -> list:
    """
    Returns a curated list of Nifty 200 stocks that pass the strict criteria:
    1. Positive profits
    2. Revenue growth > 10%
    3. Reasonable debt levels
    
    (Mocked for this version to ensure reliable app operation without complex data pipelines).
    """
    return [
        {"Symbol": "TCS.NS", "Company Name": "Tata Consultancy Services", "Sector": "IT"},
        {"Symbol": "INFY.NS", "Company Name": "Infosys", "Sector": "IT"},
        {"Symbol": "RELIANCE.NS", "Company Name": "Reliance Industries", "Sector": "Energy"},
        {"Symbol": "ICICIBANK.NS", "Company Name": "ICICI Bank", "Sector": "Financials"},
        {"Symbol": "HDFCBANK.NS", "Company Name": "HDFC Bank", "Sector": "Financials"},
        {"Symbol": "HINDUNILVR.NS", "Company Name": "Hindustan Unilever", "Sector": "FMCG"},
        {"Symbol": "ITC.NS", "Company Name": "ITC", "Sector": "FMCG"},
        {"Symbol": "LT.NS", "Company Name": "Larsen & Toubro", "Sector": "Industrials"},
        {"Symbol": "BAJFINANCE.NS", "Company Name": "Bajaj Finance", "Sector": "Financials"},
        {"Symbol": "BHARTIARTL.NS", "Company Name": "Bharti Airtel", "Sector": "Telecom"}
    ]
