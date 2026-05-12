"""Streamlit frontend for the KZ stock classifier."""
from __future__ import annotations

import os

import requests
import streamlit as st
from app.pipeline.ingest.tickers import KASE_TICKERS, KASE_NAMES, US_TICKERS

API_URL = os.getenv("API_URL", "http://localhost:8000")

FEATURES = [
    "open", "high", "low", "close", "adj_close", "volume",
    "ret_1d", "ret_5d", "ret_10d", "ret_20d",
    "sma_20", "sma_50", "ema_12", "ema_26", "price_to_sma50",
    "rsi_14", "macd", "macd_signal", "macd_hist", "stoch_k",
    "bb_upper", "bb_lower", "bb_width", "atr_14",
    "volume_ratio_20", "volume_roc", "obv",
    "overnight_gap", "intraday_range", "sigma_20d",
]

DEFAULTS = {
    "open": 1000.0, "high": 1020.0, "low": 990.0, "close": 1010.0,
    "adj_close": 1010.0, "volume": 500000.0,
    "ret_1d": 0.001, "ret_5d": 0.005, "ret_10d": 0.01, "ret_20d": 0.02,
    "sma_20": 1005.0, "sma_50": 995.0, "ema_12": 1008.0, "ema_26": 1003.0,
    "price_to_sma50": 1.015,
    "rsi_14": 55.0, "macd": 3.0, "macd_signal": 2.0, "macd_hist": 1.0,
    "stoch_k": 60.0,
    "bb_upper": 1040.0, "bb_lower": 970.0, "bb_width": 0.069,
    "atr_14": 15.0,
    "volume_ratio_20": 1.1, "volume_roc": 0.05, "obv": 1e7,
    "overnight_gap": 0.001, "intraday_range": 0.03,
    "sigma_20d": 0.012,
}

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

tab1, tab2 = st.tabs(["Manual Features", "By Ticker"])

# ── Tab 1: Manual features ────────────────────────────────────────────────────
with tab1:
    st.subheader("Enter 30 technical features")
    cols = st.columns(3)
    values: dict[str, float] = {}
    for i, feat in enumerate(FEATURES):
        with cols[i % 3]:
            values[feat] = st.number_input(feat, value=float(DEFAULTS.get(feat, 0.0)), format="%.6f", key=feat)

    if st.button("Predict", key="btn_manual"):
        with st.spinner("Calling API…"):
            try:
                resp = requests.post(f"{API_URL}/predict", json={"features": values}, timeout=10)
                resp.raise_for_status()
                show_result(resp.json())
            except requests.RequestException as e:
                st.error(f"API error: {e}")

# ── Tab 2: By ticker ──────────────────────────────────────────────────────────
with tab2:
    st.subheader("Predict by ticker (live data fetch)")
    st.caption("Market is detected automatically: KZ tickers are matched against KASE, everything else is treated as US.")

    ticker_input = st.text_input("Ticker symbol", value="KSPI")

    if st.button("Predict", key="btn_ticker"):
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
        # Show in a scrollable text area to keep the page compact
        st.markdown("\n\n".join(us_rows))
