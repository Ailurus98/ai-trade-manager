from pathlib import Path
import sys

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

try:
    import plotly.graph_objects as go
    import plotly.express as px
except Exception:
    go = None
    px = None

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import run_pipeline
from backend.utils.search import search_stock
from backend.utils.stocks import INDEX_FUNDS, STOCKS
from backend.collector.stock_data import fetch_index_quotes
from backend.advisor.portfolio import analyze_portfolio
from backend.advisor.accel_wealth import calculate_allocation, evaluate_position_sizing, evaluate_risk_control, evaluate_exit_strategy
from backend.collector.filters import filter_nifty200

# Page Config
st.set_page_config(page_title="AccelWealth", layout="wide")


# Custom CSS styling (animations, typography, layout) - strictly NO EMOJIS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@400;500;600&display=swap');

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeIn 0.8s ease-in-out; }
.slide-up { animation: slideUp 0.6s ease-out; }

/* Custom Font mapping for clean look */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, system-ui, sans-serif;
}
h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    letter-spacing: -0.5px;
}

/* Gradient Text Fixes */
.gradient-text-blue {
    background: linear-gradient(-45deg, #58a6ff 0%, #8b949e 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    color: transparent !important;
    display: inline-block;
}
.gradient-text-green {
    background: linear-gradient(45deg, #00C9FF 0%, #92FE9D 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    color: transparent !important;
    display: inline-block;
}

/* Apple Liquid Glass Styling */
.stApp {
    background: linear-gradient(-45deg, #0d1117, #161b22, #0d1117, #1a222c);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.glass-panel {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0.01) 100%);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-top: 1px solid rgba(255, 255, 255, 0.25);
    border-left: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    color: #f0f6fc;
}

.glass-success {
    background: rgba(50, 205, 50, 0.1);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(50, 205, 50, 0.3);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    color: #a8f0b3;
    font-weight: 500;
}

.glass-warning {
    background: rgba(255, 69, 0, 0.1);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 69, 0, 0.3);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    color: #ffb3a8;
    font-weight: 500;
}

/* Range Bar Styles */
.range-container {
    width: 100%;
    margin: 15px 0;
    font-family: monospace;
    font-size: 13px;
    color: #c9d1d9;
}
.range-labels {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
}
.range-bar-bg {
    width: 100%;
    height: 6px;
    background-color: rgba(255,255,255,0.1);
    border-radius: 3px;
    position: relative;
    backdrop-filter: blur(4px);
}
.range-indicator {
    position: absolute;
    width: 12px;
    height: 12px;
    background-color: #58a6ff;
    border-radius: 50%;
    top: -3px;
    transform: translateX(-50%);
    box-shadow: 0 0 8px #58a6ff;
}

/* Card Styles */
.info-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    transition: transform 0.2s, background 0.2s;
}
.info-card:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.2);
}

/* Clean up Streamlit elements */
.stMetric {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(8px);
    padding: 15px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}
</style>
""", unsafe_allow_html=True)


# Ticker Tape (No Emojis, clean UI)
@st.cache_data(ttl=120, show_spinner=False)
def get_index_data():
    return fetch_index_quotes(INDEX_FUNDS)

def render_ticker_tape():
    index_data = get_index_data()
    if not index_data:
        return

    items_html = ""
    for name, info in index_data.items():
        price = info["price"]
        change = info["change_pct"]
        
        if change > 0:
            arrow = "[UP]"
            css_class = "ticker-up"
            sign = "+"
        elif change < 0:
            arrow = "[DN]"
            css_class = "ticker-down"
            sign = ""
        else:
            arrow = "[--]"
            css_class = "ticker-flat"
            sign = ""

        items_html += f'''
        <span class="ticker-item">
            <span class="ticker-name">{name}</span>
            <span class="ticker-price">INR {price:,.2f}</span>
            <span class="{css_class}">{arrow} {sign}{change:.2f}%</span>
        </span>
        <span class="ticker-sep">|</span>
        '''

    ticker_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: transparent;
            overflow: hidden;
            font-family: 'Inter', -apple-system, sans-serif;
        }}
        .ticker-wrap {{
            width: 100%;
            overflow: hidden;
            background: linear-gradient(90deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
            border-radius: 8px;
            padding: 12px 0;
            border: 1px solid #30363d;
        }}
        .ticker-content {{
            display: inline-flex;
            white-space: nowrap;
            animation: ticker-scroll 35s linear infinite;
        }}
        .ticker-content:hover {{
            animation-play-state: paused;
        }}
        @keyframes ticker-scroll {{
            0%   {{ transform: translateX(0); }}
            100% {{ transform: translateX(-50%); }}
        }}
        .ticker-item {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 0 20px;
            font-size: 13px;
            color: #c9d1d9;
        }}
        .ticker-name {{
            font-weight: 700;
            color: #f0f6fc;
            letter-spacing: 0.3px;
        }}
        .ticker-price {{ color: #c9d1d9; }}
        .ticker-up {{ color: #3fb950; font-weight: 600; }}
        .ticker-down {{ color: #f85149; font-weight: 600; }}
        .ticker-flat {{ color: #8b949e; font-weight: 600; }}
        .ticker-sep {{ color: #30363d; padding: 0 2px; font-size: 16px; }}
    </style>
    </head>
    <body>
        <div class="ticker-wrap">
            <div class="ticker-content">
                {items_html}{items_html}
            </div>
        </div>
    </body>
    </html>
    """
    components.html(ticker_html, height=50, scrolling=False)


# Sidebar Navigation
st.sidebar.title("AccelWealth")
app_mode = st.sidebar.radio("Navigation", ["Stock Analysis", "AccelWealth (Portfolio)"])

if st.sidebar.button("Reset Engine Profile", type="secondary"):
    if "onboarding_done" in st.session_state:
        st.session_state.onboarding_done = False
    if "portfolio" in st.session_state:
        st.session_state.portfolio = [
            {"Symbol": "TCS.NS", "Quantity": 20, "avg_price": 3800.0, "current_price": 4050.0, "dma_200": 3900.0},
            {"Symbol": "HDFCBANK.NS", "Quantity": 50, "avg_price": 1600.0, "current_price": 1450.0, "dma_200": 1500.0},
            {"Symbol": "RELIANCE.NS", "Quantity": 15, "avg_price": 2700.0, "current_price": 2950.0, "dma_200": 2600.0},
            {"Symbol": "INFY.NS", "Quantity": 30, "avg_price": 1650.0, "current_price": 1400.0, "dma_200": 1500.0}
        ]
    st.rerun()


@st.cache_data(ttl=300, show_spinner=False)
def analyze_stock(symbol):
    return run_pipeline(symbol)

def build_price_chart(raw_data):
    if not isinstance(raw_data, pd.DataFrame) or raw_data.empty:
        return None

    df = raw_data.copy()

    close_obj = None
    if "Close" in df.columns:
        close_obj = df["Close"]
    else:
        for col in df.columns:
            if str(col).lower() == "close":
                close_obj = df[col]
                break

    if close_obj is None:
        return None

    if isinstance(close_obj, pd.DataFrame):
        close_series = None
        for idx in range(close_obj.shape[1]):
            candidate = pd.to_numeric(close_obj.iloc[:, idx], errors="coerce")
            if candidate.notna().any():
                close_series = candidate
                break
        if close_series is None:
            return None
    else:
        close_series = pd.to_numeric(close_obj, errors="coerce")

    chart_df = pd.DataFrame({"Close": close_series})
    chart_df["MA20"] = chart_df["Close"].rolling(window=5, min_periods=1).mean()
    chart_df = chart_df.dropna(subset=["Close"]).reset_index(drop=True)

    if go is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=chart_df["Close"], mode="lines", name="Close", line=dict(color="#58a6ff", width=2)))
        fig.add_trace(go.Scatter(y=chart_df["MA20"], mode="lines", name="MA20", line=dict(color="#f0883e", width=2, dash="dot")))
        fig.update_layout(
            height=360, margin=dict(l=20, r=20, t=30, b=20),
            plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
            font_color="#c9d1d9", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig
    return None

def build_financial_bar_chart(years, values, title, color):
    if not years or not values or go is None:
        return None
    min_len = min(len(years), len(values))
    df = pd.DataFrame({"Year": years[:min_len], "Value": values[:min_len]})
    df = df.dropna()
    if df.empty:
        return None
        
    max_val = df["Value"].abs().max()
    scale = 1
    suffix = ""
    
    if max_val >= 10_000_000:
        scale = 10_000_000
        suffix = " Cr"
    elif max_val >= 100_000:
        scale = 100_000
        suffix = " L"

    if scale > 1:
        df["Value_Scaled"] = df["Value"] / scale
        y_axis = "Value_Scaled"
        full_title = f"{title} (in{suffix})"
        labels = {"Value_Scaled": f"Amount ({suffix.strip()})"}
    else:
        y_axis = "Value"
        full_title = title
        labels = {"Value": "Amount"}
    
    fig = px.bar(df, x="Year", y=y_axis, title=full_title, color_discrete_sequence=[color], labels=labels)
    fig.update_layout(
        height=300, margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="#0d1117", paper_bgcolor="#0d1117", font_color="#c9d1d9"
    )
    return fig

def render_range_bar(label, low, high, current):
    if low is None or high is None or current is None or low == high:
        st.write(f"**{label}**: Data unavailable")
        return
        
    pct = ((current - low) / (high - low)) * 100
    pct = max(0, min(100, pct))  # Clamp between 0 and 100
    
    st.markdown(f"""
    <div class="range-container">
        <div class="range-labels">
            <span>{label} Low: INR {low:,.2f}</span>
            <span style="color:#58a6ff; font-weight:bold;">Current: INR {current:,.2f}</span>
            <span>{label} High: INR {high:,.2f}</span>
        </div>
        <div class="range-bar-bg">
            <div class="range-indicator" style="left: {pct}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


if app_mode == "Stock Analysis":
    st.markdown("""
    <div style="text-align: center; margin-bottom: 25px; animation: slideUp 0.8s ease-out;">
        <h1 class="gradient-text-blue" style="font-size: 3.5rem; font-weight: 800; margin-bottom: 0px; padding-bottom: 10px;">AccelWealth Analysis</h1>
        <p style="color: #8b949e; font-size: 1.1rem; font-weight: 400; margin-top: -10px;">Comprehensive AI-driven insights for NSE Indian Stocks</p>
    </div>
    """, unsafe_allow_html=True)
    
    render_ticker_tape()

    query = st.text_input(
        "Search by company name, ticker, or abbreviation",
        placeholder="e.g. TCS, Reliance, bajaj, INFY, zomato..."
    )

    if query:
        results = search_stock(query)

        if results:
            top_match = list(results.keys())[0]
            if query.lower().strip() != top_match.lower().strip():
                st.caption(f"Best match: **{top_match}** ({results[top_match]})")

            selected = st.selectbox("Select Company", list(results.keys()))
            symbol = results[selected]

            if st.button("Analyze Stock", type="primary"):
                with st.spinner(f"Analyzing {selected}..."):
                    try:
                        result = analyze_stock(symbol)
                    except ValueError as err:
                        analyze_stock.clear()
                        st.warning(str(err))
                        st.stop()
                    except Exception as err:
                        analyze_stock.clear()
                        import traceback
                        st.error(f"We could not analyze this stock right now. Please try again. Error: {type(err).__name__} - {str(err)}")
                        st.code(traceback.format_exc())
                        st.stop()
                        
                    st.markdown(f"<div class='glass-panel slide-up'><h2 style='margin:0;'>{selected} ({symbol})</h2></div>", unsafe_allow_html=True)
                    
                    # Decision Banner
                    decision = result["decision"]
                    confidence = result.get("confidence", 50)
                        
                    if decision == "BUY":
                        st.markdown(f"<div class='glass-success'>Action Recommendation: BUY ({confidence}% confidence)</div>", unsafe_allow_html=True)
                    elif decision == "SELL":
                        st.markdown(f"<div class='glass-warning'>Action Recommendation: SELL ({confidence}% confidence)</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='glass-panel'>Action Recommendation: HOLD ({confidence}% confidence)</div>", unsafe_allow_html=True)

                    # Core Metrics Row (Animated)
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Tech: RSI", f"{result['rsi']:.2f}")
                    col2.metric("Tech: Moving Avg", f"INR {result['moving_avg']:.2f}")
                    col3.metric("News Sentiment", result["sentiment"])
                    col4.metric("AI Score", f"{result['score']:+.1f}")

                    if True:
                        st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
                        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Fundamentals", "Financials", "News"])
                        
                        # --- TAB 1: OVERVIEW ---
                        with tab1:
                            st.subheader("AI Insight")
                            st.markdown(f"<div class='glass-panel'>{result['reason']}</div>", unsafe_allow_html=True)
                            
                            st.subheader("Price Action")
                            fig_price = build_price_chart(result.get("data"))
                            if fig_price:
                                st.plotly_chart(fig_price, use_container_width=True)
                            else:
                                st.warning("Chart data unavailable")
                                
                            fund = result.get("fundamentals", {})
                            st.subheader("Trading Range")
                            render_range_bar("Day Range", fund.get("day_low"), fund.get("day_high"), fund.get("current_price"))
                            render_range_bar("52-Week Range", fund.get("fifty_two_week_low"), fund.get("fifty_two_week_high"), fund.get("current_price"))

                        # --- TAB 2: FUNDAMENTALS ---
                        with tab2:
                            fund = result.get("fundamentals", {})
                            if not fund:
                                st.warning("Fundamental data not currently available for this stock.")
                            else:
                                st.subheader("Key Statistics")
                                fcol1, fcol2, fcol3 = st.columns(3)
                                
                                mcap = fund.get("market_cap")
                                mcap_str = f"INR {mcap / 1e7:,.2f} Cr" if mcap else "N/A"
                                fcol1.metric("Market Cap", mcap_str)
                                
                                pe = fund.get("pe_ratio")
                                fcol2.metric("PE Ratio", f"{pe:,.2f}" if pe else "N/A")
                                
                                pb = fund.get("pb_ratio")
                                fcol3.metric("PB Ratio", f"{pb:,.2f}" if pb else "N/A")
                                
                                fcol4, fcol5, fcol6 = st.columns(3)
                                
                                ind_pe = fund.get("industry_pe")
                                fcol4.metric("Industry PE", f"{ind_pe:,.2f}" if ind_pe else "N/A")
                                
                                dte = fund.get("debt_to_equity")
                                fcol5.metric("Debt to Equity", f"{dte:,.2f}%" if dte else "N/A")
                                
                                roe = fund.get("roe")
                                fcol6.metric("Return on Equity (ROE)", f"{roe*100:,.2f}%" if roe else "N/A")
                                
                                fcol7, fcol8, fcol9 = st.columns(3)
                                div = fund.get("dividend_yield")
                                fcol7.metric("Dividend Yield", f"{div*100:,.2f}%" if div else "N/A")
                                bv = fund.get("book_value")
                                fcol8.metric("Book Value", f"INR {bv:,.2f}" if bv else "N/A")
                                fv = fund.get("face_value")
                                fcol9.metric("Face Value", f"INR {fv:,.2f}" if fv else "N/A")

                        # --- TAB 3: FINANCIALS ---
                        with tab3:
                            fin = result.get("financials", {})
                            years = fin.get("years", [])
                            if not years:
                                st.warning("Yearly financial data is not currently available.")
                            else:
                                st.subheader("Yearly Performance Trend")
                                
                                rev_fig = build_financial_bar_chart(years, fin.get("revenue"), "Total Revenue", "#58a6ff")
                                if rev_fig: st.plotly_chart(rev_fig, use_container_width=True)
                                
                                inc_fig = build_financial_bar_chart(years, fin.get("net_income"), "Net Profit (Income)", "#3fb950")
                                if inc_fig: st.plotly_chart(inc_fig, use_container_width=True)
                                
                                nw_fig = build_financial_bar_chart(years, fin.get("net_worth"), "Total Equity (Net Worth)", "#f0883e")
                                if nw_fig: st.plotly_chart(nw_fig, use_container_width=True)

                        # --- TAB 4: NEWS ---
                        with tab4:
                            news_list = result.get("news", [])
                            if not news_list:
                                st.info("No recent news found.")
                            else:
                                st.subheader("Recent Headlines")
                                for article in news_list:
                                    st.markdown(f"""
                                    <div class="info-card">
                                        <h4>{article.get('title', 'Headline Unavailable')}</h4>
                                        <p style="color: #8b949e; font-size: 13px;">
                                            Publisher: {article.get('publisher', 'Unknown')} | Date: {article.get('date', 'Recent')}
                                        </p>
                                        <a href="{article.get('link', '#')}" target="_blank" style="color: #58a6ff; text-decoration: none;">Read Full Article ></a>
                                    </div>
                                    """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No matching stocks found. Try a different name.")
    else:
        st.markdown("<div class='glass-panel' style='text-align: center;'><h3>Welcome to AccleWealth Stock Analysis</h3><p>Search for a stock above to view detailed AI-driven insights, financials, and news.</p></div>", unsafe_allow_html=True)

elif app_mode == "AccelWealth (Portfolio)":
    st.markdown("""
    <div style="text-align: center; margin-top: 20px; margin-bottom: 40px; animation: slideUp 0.8s ease-out;">
        <h1 class="gradient-text-green" style="font-size: 4.5rem; font-weight: 800; margin-bottom: 0; padding-bottom: 5px; line-height: 1.1;">AccelWealth</h1>
        <p style="color: #c9d1d9; font-size: 1.25rem; font-family: 'Inter', sans-serif; font-weight: 400; letter-spacing: 0.2px; margin-top: 5px;">Disciplined investing through automation, risk control, and behavioral guardrails.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = [
            {"Symbol": "TCS.NS", "Quantity": 20, "avg_price": 3800.0, "current_price": 4050.0, "dma_200": 3900.0},
            {"Symbol": "HDFCBANK.NS", "Quantity": 50, "avg_price": 1600.0, "current_price": 1450.0, "dma_200": 1500.0},
            {"Symbol": "RELIANCE.NS", "Quantity": 15, "avg_price": 2700.0, "current_price": 2950.0, "dma_200": 2600.0},
            {"Symbol": "INFY.NS", "Quantity": 30, "avg_price": 1650.0, "current_price": 1400.0, "dma_200": 1500.0}
        ]
        
    if "onboarding_done" not in st.session_state:
        st.session_state.onboarding_done = False
        
    if not st.session_state.onboarding_done:
        st.subheader("Investor Profile Setup")
        st.write("Let's set up your strict, rule-based portfolio engine.")
        
        with st.form("onboarding_form"):
            investable_amount = st.number_input("Monthly Investable Amount (INR)", min_value=1000, value=10000, step=1000)
            risk_tolerance = st.selectbox("Risk Tolerance", ["Low", "Medium", "High"])
            horizon = st.selectbox("Investment Horizon", ["Short (<3y)", "Medium (3-7y)", "Long (>7y)"])
            
            submit = st.form_submit_button("Initialize AccelWealth Engine", type="primary")
            if submit:
                st.session_state.profile = {
                    "amount": investable_amount,
                    "risk": risk_tolerance,
                    "horizon": horizon
                }
                st.session_state.onboarding_done = True
                st.rerun()
    else:
        # Display the Main Dashboard
        alloc = calculate_allocation(
            st.session_state.profile["amount"],
            st.session_state.profile["risk"],
            st.session_state.profile["horizon"]
        )
        
        st.subheader("Target Allocation Strategy")
        alloc_html = f"""
        <div class='glass-panel' style='padding: 24px; display: flex; justify-content: space-around; flex-wrap: wrap; margin-bottom: 30px;'>
            <div style='text-align: center;'>
                <p style='color: #8b949e; font-size: 0.95rem; margin-bottom: 5px; font-weight: 500;'>Index Exposure (Nifty 50)</p>
                <div style='display: flex; align-items: baseline; justify-content: center; gap: 10px;'>
                    <h2 style='margin: 0; font-size: 2.2rem; color: #f0f6fc; font-weight: 700;'>{alloc['Index Exposure (Nifty 50)']}%</h2>
                    <span style='color: #3fb950; font-weight: 600; font-size: 1.1rem;'>INR {alloc['Index Amount']:,.0f} / mo</span>
                </div>
            </div>
            <div style='text-align: center;'>
                <p style='color: #8b949e; font-size: 0.95rem; margin-bottom: 5px; font-weight: 500;'>Curated Stock Basket</p>
                <div style='display: flex; align-items: baseline; justify-content: center; gap: 10px;'>
                    <h2 style='margin: 0; font-size: 2.2rem; color: #f0f6fc; font-weight: 700;'>{alloc['Curated Stock Basket']}%</h2>
                    <span style='color: #58a6ff; font-weight: 600; font-size: 1.1rem;'>INR {alloc['Stock Amount']:,.0f} / mo</span>
                </div>
            </div>
        </div>
        """
        st.markdown(alloc_html, unsafe_allow_html=True)
        
        # Add Stocks Section
        st.subheader("Manage Holdings (Curated Nifty 200 Universe)")
        
        nifty200 = filter_nifty200()
        n200_symbols = [f"{s['Company Name']} ({s['Symbol']})" for s in nifty200]
        
        with st.expander("Add New Position", expanded=False):
            colA, colB, colC = st.columns([3, 1, 1])
            with colA:
                selected_stock = st.selectbox("Select Valid Nifty 200 Stock", [""] + n200_symbols)
            with colB:
                qty = st.number_input("Quantity", min_value=1, value=10, key="aw_qty")
            with colC:
                avg_p = st.number_input("Avg Price", min_value=1.0, value=100.0, key="aw_avgp")
            
            if st.button("Add to Engine", type="primary") and selected_stock:
                symbol = selected_stock.split("(")[-1].strip(")")
                # Mock current price for demo as 95% of avg or random
                st.session_state.portfolio.append({
                    "Symbol": symbol, 
                    "Quantity": qty, 
                    "avg_price": avg_p,
                    "current_price": avg_p * 0.98, # mock value
                    "dma_200": avg_p * 0.95 # mock value
                })
                st.success(f"Added {qty} units of {symbol}")
                st.rerun()
                
        # Editable Data Grid
        df_port = pd.DataFrame(st.session_state.portfolio)
        if not df_port.empty:
            df_port = df_port[["Symbol", "Quantity", "avg_price", "current_price", "dma_200"]]
            edited_df = st.data_editor(
                df_port, 
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True
            )
            st.session_state.portfolio = edited_df.to_dict('records')
        
        if st.session_state.portfolio:
            port_input = []
            total_val = 0.0
            for r in st.session_state.portfolio:
                if "Symbol" in r and r["Symbol"]:
                    qty_val = float(r.get("Quantity", 0.0))
                    price_val = float(r.get("current_price", 0.0))
                    val = qty_val * price_val
                    total_val += val
                    port_input.append(r)
            
            if total_val > 0:
                st.markdown("<h3 style='margin-top: 10px;'>System Diagnostics</h3>", unsafe_allow_html=True)
                
                # Run Logic
                sizing_alerts = evaluate_position_sizing(port_input, total_val)
                risk_data = evaluate_risk_control(port_input, total_val)
                
                # Portfolio Level Stats
                port_drawdown = risk_data["portfolio_drawdown"]
                
                metric_col1, metric_col2 = st.columns(2)
                metric_col1.metric("Stock Portfolio Value", f"INR {total_val:,.2f}")
                metric_col2.metric("Aggregate Drawdown", f"{port_drawdown:.1f}%")
                
                if risk_data["portfolio_alerts"]:
                    for al in risk_data["portfolio_alerts"]:
                        st.markdown(f"<div class='glass-warning'>[CRITICAL] {al['message']}<br/><b>ACTION:</b> {al['action']}</div>", unsafe_allow_html=True)
                        
                for al in sizing_alerts:
                    if al['type'] in ['WARNING', 'BLOCKED']:
                        st.markdown(f"<div class='glass-warning'>⚠️ {al['message']} (Symbol: {al['symbol']})<br/><b>ACTION:</b> {al['action']}</div>", unsafe_allow_html=True)
                
                st.markdown("### Position Matrix", unsafe_allow_html=True)
                for item in port_input:
                    sym = item["Symbol"]
                    risk_m = item.get("risk_metrics", {})
                    exit_alerts = evaluate_exit_strategy(item)
                    
                    st.markdown(f"#### {sym}")
                    
                    html_metrics = f"""
                    <div class='glass-panel' style='padding: 24px; display: flex; justify-content: space-between; flex-wrap: wrap; margin-bottom: 20px;'>
                        <div style='flex: 1; text-align: left;'>
                            <p style='color: #8b949e; font-size: 0.9rem; margin-bottom: 5px; font-weight: 500;'>Drawdown</p>
                            <h3 style='margin-top: 0; font-size: 2rem; color: #f0f6fc; font-weight: 600;'>{risk_m.get('drawdown', 0):.1f}%</h3>
                        </div>
                        <div style='flex: 1; text-align: left;'>
                            <p style='color: #8b949e; font-size: 0.9rem; margin-bottom: 5px; font-weight: 500;'>Normal Downside</p>
                            <h3 style='margin-top: 0; font-size: 2rem; color: #f0f6fc; font-weight: 600;'>INR {risk_m.get('normal_downside', 0):,.2f}</h3>
                        </div>
                        <div style='flex: 1; text-align: left;'>
                            <p style='color: #8b949e; font-size: 0.9rem; margin-bottom: 5px; font-weight: 500;'>Crisis Downside</p>
                            <h3 style='margin-top: 0; font-size: 2rem; color: #f0f6fc; font-weight: 600;'>INR {risk_m.get('crisis_downside', 0):,.2f}</h3>
                        </div>
                    </div>
                    """
                    st.markdown(html_metrics, unsafe_allow_html=True)
                    
                    pos_alerts_for_this = [a for a in risk_data["position_alerts"] if a["symbol"] == sym]
                    
                    if not pos_alerts_for_this and not exit_alerts:
                        st.markdown("<div class='glass-success' style='margin-bottom: 30px;'>[OK] Position within standard parameters. HOLD.</div>", unsafe_allow_html=True)
                    else:
                        for al in pos_alerts_for_this:
                            st.markdown(f"<div class='glass-warning' style='margin-bottom: 10px;'>[ALERT] {al['message']}<br/><b>ACTION:</b> {al['action']}</div>", unsafe_allow_html=True)
                        for al in exit_alerts:
                            if "WINNER" in al['type']:
                                st.markdown(f"<div class='glass-success' style='margin-bottom: 10px;'>[PROGRESS] {al['message']}<br/><b>ACTION:</b> {al['action']}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div class='glass-warning' style='margin-bottom: 10px;'>⚠️ {al['message']}<br/><b>ACTION:</b> {al['action']}</div>", unsafe_allow_html=True)
                        st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

