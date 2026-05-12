# Vendored from StockClassifier commit 1bb70890f4dd9761ee486f04d3e23073d195b148
"""Yahoo Finance data fetcher.

Pulls daily OHLCV, quarterly financial statements, and static info for a ticker.
Each public function returns a pandas object (DataFrame or Series) ready to be
written to CSV. Network errors propagate; the caller decides retry/skip policy.
"""

from __future__ import annotations

import pandas as pd
import yfinance as yf


def fetch_ohlcv(ticker: str, period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    """Daily OHLCV with adjusted close. Index is the trade date (UTC-naive)."""
    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index.name = "Date"
    return df


def fetch_quarterly_financials(tk: yf.Ticker) -> pd.DataFrame:
    """Quarterly income statement. Columns are quarter-end dates."""
    return tk.quarterly_financials


def fetch_quarterly_balance_sheet(tk: yf.Ticker) -> pd.DataFrame:
    return tk.quarterly_balance_sheet


def fetch_quarterly_cashflow(tk: yf.Ticker) -> pd.DataFrame:
    return tk.quarterly_cashflow


def fetch_info(tk: yf.Ticker) -> pd.Series:
    """Static metadata as a single-column Series for easy CSV write."""
    info = tk.info or {}
    return pd.Series(info, name="value")


def fetch_recommendations(tk: yf.Ticker) -> pd.DataFrame:
    """Analyst recommendation history (Strategy B label source). May be empty."""
    rec = tk.recommendations
    if rec is None:
        return pd.DataFrame()
    return rec


def fetch_all(ticker: str, period: str = "5y") -> dict[str, pd.DataFrame | pd.Series]:
    """One call to grab every artifact we need for `ticker`.

    Returns a dict keyed by artifact name; values may be empty if Yahoo has no data.
    """
    tk = yf.Ticker(ticker)
    return {
        "ohlcv": fetch_ohlcv(ticker, period=period),
        "quarterly_financials": fetch_quarterly_financials(tk),
        "quarterly_balance_sheet": fetch_quarterly_balance_sheet(tk),
        "quarterly_cashflow": fetch_quarterly_cashflow(tk),
        "info": fetch_info(tk),
        "recommendations": fetch_recommendations(tk),
    }
