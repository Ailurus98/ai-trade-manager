import streamlit as st
from backend.main import run_pipeline
from backend.utils.search import search_stock

st.title("📈 AI Trade Manager (Indian Market)")

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
			result = run_pipeline(symbol)

			st.subheader(f"{selected} ({symbol})")
			st.write(f"RSI: {result['rsi']:.2f}")
			st.write(f"Moving Avg: {result['moving_avg']:.2f}")
			st.write(f"Sentiment: {result['sentiment']}")
			st.write(f"Decision: {result['decision']}")
			st.write(f"Reason: {result['reason']}")
	else:
		st.warning("No matching stocks found")
