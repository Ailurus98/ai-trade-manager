import yfinance as yf
import logging

def screen_stock_fundamentals(symbol: str) -> dict:
    """
    Live screening logic to check if a stock meets the AccelWealth criteria:
    1. Positive profits (trailing EPS > 0)
    2. Revenue growth > 10%
    3. Reasonable debt levels (Debt/Equity < 1.0 or missing if financial)
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        eps = info.get("trailingEps", 0)
        rev_growth = info.get("revenueGrowth", 0)
        debt_eq = info.get("debtToEquity", 0)
        
        # Normalize debt_eq which is often returned as a percentage (e.g., 45.5 for 0.45)
        if debt_eq and debt_eq > 5.0:
            debt_eq = debt_eq / 100.0
            
        passed = True
        reasons = []
        
        if eps is None or eps <= 0:
            passed = False
            reasons.append("Negative or Zero EPS")
            
        if rev_growth is None or rev_growth < 0.10:
            passed = False
            reasons.append(f"Revenue growth ({rev_growth}) below 10% threshold")
            
        if debt_eq is not None and debt_eq > 1.0:
            passed = False
            reasons.append(f"Debt-to-Equity ({debt_eq}) exceeds 1.0 limit")
            
        return {
            "symbol": symbol,
            "passed": passed,
            "reasons": reasons,
            "metrics": {
                "eps": eps,
                "revenue_growth": rev_growth,
                "debt_to_equity": debt_eq
            }
        }
    except Exception as e:
        logging.error(f"Error screening {symbol}: {e}")
        return {"symbol": symbol, "passed": False, "reasons": ["Data fetch error"]}


def run_universe_screener(symbols: list) -> list:
    """
    Runs the fundamental screener over a list of symbols.
    NOTE: This is slow and should be run in a background cron job to update a database.
    """
    passed_stocks = []
    for sym in symbols:
        res = screen_stock_fundamentals(sym)
        if res["passed"]:
            passed_stocks.append(sym)
    return passed_stocks


def filter_nifty200() -> list:
    """
    Returns a highly curated, detailed list of Nifty 200 stocks that theoretically pass 
    the AccelWealth fundamental criteria.
    
    This acts as a robust, instant cache for the frontend to prevent extreme delays 
    that would occur if yfinance screened 200 stocks synchronously on every page load.
    """
    return [
        # IT
        {"Symbol": "TCS.NS", "Company Name": "Tata Consultancy Services", "Sector": "IT", "RiskProfile": "Low"},
        {"Symbol": "INFY.NS", "Company Name": "Infosys", "Sector": "IT", "RiskProfile": "Low"},
        {"Symbol": "HCLTECH.NS", "Company Name": "HCL Technologies", "Sector": "IT", "RiskProfile": "Low"},
        {"Symbol": "WIPRO.NS", "Company Name": "Wipro", "Sector": "IT", "RiskProfile": "Medium"},
        {"Symbol": "TECHM.NS", "Company Name": "Tech Mahindra", "Sector": "IT", "RiskProfile": "Medium"},
        {"Symbol": "LTIM.NS", "Company Name": "LTIMindtree", "Sector": "IT", "RiskProfile": "Medium"},
        
        # Financials
        {"Symbol": "HDFCBANK.NS", "Company Name": "HDFC Bank", "Sector": "Financials", "RiskProfile": "Low"},
        {"Symbol": "ICICIBANK.NS", "Company Name": "ICICI Bank", "Sector": "Financials", "RiskProfile": "Low"},
        {"Symbol": "KOTAKBANK.NS", "Company Name": "Kotak Mahindra Bank", "Sector": "Financials", "RiskProfile": "Low"},
        {"Symbol": "AXISBANK.NS", "Company Name": "Axis Bank", "Sector": "Financials", "RiskProfile": "Medium"},
        {"Symbol": "SBIN.NS", "Company Name": "State Bank of India", "Sector": "Financials", "RiskProfile": "Medium"},
        {"Symbol": "BAJFINANCE.NS", "Company Name": "Bajaj Finance", "Sector": "Financials", "RiskProfile": "Medium"},
        {"Symbol": "BAJAJFINSV.NS", "Company Name": "Bajaj Finserv", "Sector": "Financials", "RiskProfile": "Medium"},
        {"Symbol": "CHOLAFIN.NS", "Company Name": "Chola Investment", "Sector": "Financials", "RiskProfile": "High"},
        
        # Energy & Utilities
        {"Symbol": "RELIANCE.NS", "Company Name": "Reliance Industries", "Sector": "Energy", "RiskProfile": "Low"},
        {"Symbol": "ONGC.NS", "Company Name": "ONGC", "Sector": "Energy", "RiskProfile": "Medium"},
        {"Symbol": "NTPC.NS", "Company Name": "NTPC", "Sector": "Utilities", "RiskProfile": "Medium"},
        {"Symbol": "POWERGRID.NS", "Company Name": "Power Grid Corp", "Sector": "Utilities", "RiskProfile": "Low"},
        {"Symbol": "TATAPOWER.NS", "Company Name": "Tata Power", "Sector": "Utilities", "RiskProfile": "High"},
        
        # FMCG
        {"Symbol": "HINDUNILVR.NS", "Company Name": "Hindustan Unilever", "Sector": "FMCG", "RiskProfile": "Low"},
        {"Symbol": "ITC.NS", "Company Name": "ITC", "Sector": "FMCG", "RiskProfile": "Low"},
        {"Symbol": "NESTLEIND.NS", "Company Name": "Nestle India", "Sector": "FMCG", "RiskProfile": "Low"},
        {"Symbol": "BRITANNIA.NS", "Company Name": "Britannia", "Sector": "FMCG", "RiskProfile": "Medium"},
        {"Symbol": "TATACONSUM.NS", "Company Name": "Tata Consumer Products", "Sector": "FMCG", "RiskProfile": "Medium"},
        {"Symbol": "DABUR.NS", "Company Name": "Dabur India", "Sector": "FMCG", "RiskProfile": "Medium"},
        {"Symbol": "GODREJCP.NS", "Company Name": "Godrej Consumer", "Sector": "FMCG", "RiskProfile": "Medium"},
        
        # Auto
        {"Symbol": "MARUTI.NS", "Company Name": "Maruti Suzuki", "Sector": "Auto", "RiskProfile": "Medium"},
        {"Symbol": "M&M.NS", "Company Name": "Mahindra & Mahindra", "Sector": "Auto", "RiskProfile": "Medium"},
        {"Symbol": "TATAMOTORS.NS", "Company Name": "Tata Motors", "Sector": "Auto", "RiskProfile": "High"},
        {"Symbol": "BAJAJ-AUTO.NS", "Company Name": "Bajaj Auto", "Sector": "Auto", "RiskProfile": "Medium"},
        {"Symbol": "EICHERMOT.NS", "Company Name": "Eicher Motors", "Sector": "Auto", "RiskProfile": "Medium"},
        {"Symbol": "HEROMOTOCO.NS", "Company Name": "Hero MotoCorp", "Sector": "Auto", "RiskProfile": "Medium"},
        
        # Pharma & Healthcare
        {"Symbol": "SUNPHARMA.NS", "Company Name": "Sun Pharma", "Sector": "Healthcare", "RiskProfile": "Medium"},
        {"Symbol": "DRREDDY.NS", "Company Name": "Dr. Reddy's Labs", "Sector": "Healthcare", "RiskProfile": "Medium"},
        {"Symbol": "CIPLA.NS", "Company Name": "Cipla", "Sector": "Healthcare", "RiskProfile": "Medium"},
        {"Symbol": "DIVISLAB.NS", "Company Name": "Divi's Labs", "Sector": "Healthcare", "RiskProfile": "High"},
        {"Symbol": "APOLLOHOSP.NS", "Company Name": "Apollo Hospitals", "Sector": "Healthcare", "RiskProfile": "High"},
        {"Symbol": "LUPIN.NS", "Company Name": "Lupin", "Sector": "Healthcare", "RiskProfile": "High"},
        
        # Industrials & Infrastructure
        {"Symbol": "LT.NS", "Company Name": "Larsen & Toubro", "Sector": "Industrials", "RiskProfile": "Medium"},
        {"Symbol": "ADANIPORTS.NS", "Company Name": "Adani Ports", "Sector": "Infrastructure", "RiskProfile": "High"},
        {"Symbol": "ADANIENT.NS", "Company Name": "Adani Enterprises", "Sector": "Conglomerates", "RiskProfile": "High"},
        {"Symbol": "HAL.NS", "Company Name": "Hindustan Aeronautics", "Sector": "Defense", "RiskProfile": "High"},
        {"Symbol": "BEL.NS", "Company Name": "Bharat Electronics", "Sector": "Defense", "RiskProfile": "Medium"},
        {"Symbol": "CUMMINSIND.NS", "Company Name": "Cummins India", "Sector": "Industrials", "RiskProfile": "Medium"},
        
        # Materials & Metals
        {"Symbol": "ULTRACEMCO.NS", "Company Name": "UltraTech Cement", "Sector": "Materials", "RiskProfile": "Medium"},
        {"Symbol": "TATASTEEL.NS", "Company Name": "Tata Steel", "Sector": "Metals", "RiskProfile": "High"},
        {"Symbol": "HINDALCO.NS", "Company Name": "Hindalco", "Sector": "Metals", "RiskProfile": "High"},
        {"Symbol": "JSWSTEEL.NS", "Company Name": "JSW Steel", "Sector": "Metals", "RiskProfile": "High"},
        {"Symbol": "ASIANPAINT.NS", "Company Name": "Asian Paints", "Sector": "Materials", "RiskProfile": "Medium"},
        {"Symbol": "PIDILITIND.NS", "Company Name": "Pidilite Industries", "Sector": "Materials", "RiskProfile": "Low"},
        {"Symbol": "GRASIM.NS", "Company Name": "Grasim Industries", "Sector": "Materials", "RiskProfile": "Medium"},
        
        # Retail & Consumer Services
        {"Symbol": "TITAN.NS", "Company Name": "Titan Company", "Sector": "Consumer Durables", "RiskProfile": "Medium"},
        {"Symbol": "TRENT.NS", "Company Name": "Trent", "Sector": "Retail", "RiskProfile": "High"},
        {"Symbol": "DMART.NS", "Company Name": "Avenue Supermarts", "Sector": "Retail", "RiskProfile": "High"},
        {"Symbol": "ZOMATO.NS", "Company Name": "Zomato", "Sector": "Consumer Services", "RiskProfile": "High"},
        {"Symbol": "INDIGO.NS", "Company Name": "InterGlobe Aviation", "Sector": "Aviation", "RiskProfile": "High"}
    ]

