"""Streamlit frontend for the KZ stock classifier."""
from __future__ import annotations

import os

import requests
import streamlit as st
from app.pipeline.ingest.tickers import KASE_TICKERS, KASE_NAMES, US_TICKERS

API_URL = os.getenv("API_URL", "http://localhost:8000")

SIGNAL_COLOR = {"Buy": "🟢", "Hold": "🟡", "Sell": "🔴"}


def show_result(result: dict):
    signal = result.get("signal", "?")
    conf = result.get("confidence", 0.0)
    proba = result.get("probabilities", {})
    st.markdown(f"### {SIGNAL_COLOR.get(signal, '')} **{signal}**")
    st.metric("Confidence", f"{conf:.1%}")
    if proba:
        st.bar_chart(proba)


st.set_page_config(page_title="Stock Classifier", page_icon="📈")
st.title("📈 Stock Classifier — KZ Market")

st.subheader("Predict by ticker (live data fetch)")
st.caption("Market is detected automatically: KZ tickers are matched against KASE, everything else is treated as US.")

ticker_input = st.text_input("Ticker symbol", value="KSPI")

if st.button("Predict"):
    with st.spinner(f"Fetching data for {ticker_input.upper()} and predicting…"):
        try:
            resp = requests.post(
                f"{API_URL}/predict/ticker",
                json={"ticker": ticker_input.strip(), "market": "auto"},
                timeout=60,
            )
            resp.raise_for_status()
            result = resp.json()
            detected_market = result.get("market", "?").upper()
            st.info(f"Detected market: **{detected_market}**")
            show_result(result)
        except requests.HTTPError as e:
            try:
                detail = e.response.json().get("detail", str(e))
            except Exception:
                detail = str(e)
            st.error(f"Error: {detail}")
        except requests.RequestException as e:
            st.error(f"API error: {e}")

st.divider()

col_kz, col_us = st.columns(2)

with col_kz:
    st.markdown("#### KZ Market (KASE)")
    kz_rows = [
        f"`{t}` — {KASE_NAMES.get(t, '')}" for t in KASE_TICKERS
    ]
    st.markdown("\n\n".join(kz_rows))

with col_us:
    st.markdown("#### US Market (NYSE / Nasdaq)")
    us_rows = [f"`{t}`" for t in US_TICKERS]
    st.markdown("\n\n".join(us_rows))
