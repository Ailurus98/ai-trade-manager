from pathlib import Path
import sys

import streamlit as st
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
	sys.path.insert(0, str(ROOT_DIR))

from backend.main import run_pipeline
from backend.utils.search import search_stock


@st.cache_data(ttl=300, show_spinner=False)
def analyze_stock(symbol):
	return run_pipeline(symbol)

st.title("📈 AI Trade Manager (Indian Market)")
st.caption("AI-powered stock analysis system for Indian markets 🇮🇳")

query = st.text_input("Search Company (e.g. Reliance, TCS)")

if query:
	results = search_stock(query)

	if results:
		selected = st.selectbox(
			"Select Company",
			list(results.keys())
		)

		symbol = results[selected]

		if st.button("Analyze"):
			try:
				result = analyze_stock(symbol)

				st.subheader(f"{selected} ({symbol})")

				col1, col2, col3 = st.columns(3)

				col1.metric("RSI", f"{result['rsi']:.2f}")
				col2.metric("Moving Avg", f"{result['moving_avg']:.2f}")
				col3.metric("Sentiment", result["sentiment"])

				decision = result["decision"]

				if decision == "BUY":
					st.success(f"📈 Decision: {decision}")
				elif decision == "SELL":
					st.error(f"📉 Decision: {decision}")
				else:
					st.warning(f"⚖️ Decision: {decision}")

				st.subheader("Confidence Level")

				confidence = result.get("confidence", 50)
				st.progress(confidence / 100)
				st.write(f"{confidence}% confidence")

				st.subheader("🧠 AI Insight")
				st.info(result["reason"])

				if "data" in result and "Close" in result["data"]:
					df = result["data"].copy()

					# Fix 1: Ensure index is datetime
					df.index = pd.to_datetime(df.index)

					# Fix 2: Keep only required columns
					df = df[["Close"]]

					# Fix 3: Add Moving Average (safer window for short histories)
					df["MA20"] = df["Close"].rolling(window=5).mean()

					# Fix 4: Remove NaN values
					df = df.dropna()

					st.subheader("📊 Price Trend with Moving Average")

					# Fix 5: Check if data exists
					if df.empty:
						st.error("No chart data available")
					else:
						st.line_chart(df)
				else:
					st.warning("Price chart data is unavailable in this run. Please click Analyze again.")
			except ValueError as err:
				analyze_stock.clear()
				st.warning(str(err))
			except Exception as err:
				analyze_stock.clear()
				st.error("We could not analyze this stock right now. Please try again in a minute.")
				st.caption(f"Debug: {type(err).__name__}: {err}")
	else:
		st.warning("No matching stocks found")
