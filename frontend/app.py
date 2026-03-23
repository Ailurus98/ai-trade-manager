import streamlit as st
from backend.main import run_pipeline

st.title("📈 AI Trade Manager (Indian Market)")

symbol = st.text_input("Enter Stock Symbol (e.g. RELIANCE.NS)")

if st.button("Analyze"):

	result = run_pipeline(symbol)

	st.subheader(f"Stock: {result['symbol']}")
	st.write(f"RSI: {result['rsi']:.2f}")
	st.write(f"Moving Avg: {result['moving_avg']:.2f}")
	st.write(f"Sentiment: {result['sentiment']}")
	st.write(f"Decision: {result['decision']}")
	st.write(f"Reason: {result['reason']}")
