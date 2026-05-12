# Vendored from StockClassifier commit 1bb70890f4dd9761ee486f04d3e23073d195b148
"""KASE data fetcher.

Hits kase.kz's internal TradingView UDF endpoint to pull daily OHLCV for native
KASE tickers. Only OHLCV is exposed — fundamentals are not available from this
feed (see KASE_DATA.md). Output shape matches `yfinance_fetcher.fetch_ohlcv`
so downstream code can treat both sources identically.

Endpoint: GET https://kase.kz/tv-charts/securities/history
          ?symbol=<CODE>&resolution=D&from=<unix>&to=<unix>
Response: TradingView UDF — {s, t, o, h, l, c, v} or {s:"no_data"}.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import requests

UDF_BASE = "https://kase.kz/tv-charts/securities"
DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0 (StockClassifier data ingest)"}


def _to_unix(ts: str | datetime | pd.Timestamp) -> int:
    """Accept a date/datetime/string and return unix-seconds (UTC)."""
    if isinstance(ts, (int, float)):
        return int(ts)
    if isinstance(ts, str):
        ts = pd.Timestamp(ts)
    if isinstance(ts, datetime) and ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return int(pd.Timestamp(ts).timestamp())


def fetch_ohlcv_kase(
    code: str,
    start: str | datetime = "2019-01-01",
    end: str | datetime | None = None,
    resolution: str = "D",
    timeout: int = 20,
) -> pd.DataFrame:
    """Daily OHLCV for a KASE share code.

    Returns a DataFrame with columns matching the Yahoo shape used elsewhere:
    ``Open, High, Low, Close, Adj Close, Volume``. For KASE we set
    ``Adj Close = Close`` (the feed publishes no adjusted series). Empty
    DataFrame on `no_data`.
    """
    if end is None:
        end = datetime.now(tz=timezone.utc)
    params = {
        "symbol": code,
        "resolution": resolution,
        "from": _to_unix(start),
        "to": _to_unix(end),
    }
    r = requests.get(f"{UDF_BASE}/history", params=params,
                     headers=DEFAULT_HEADERS, timeout=timeout)
    r.raise_for_status()
    j = r.json()

    if j.get("s") != "ok" or not j.get("t"):
        return pd.DataFrame()

    df = pd.DataFrame({
        "Open":   j["o"],
        "High":   j["h"],
        "Low":    j["l"],
        "Close":  j["c"],
        "Volume": j["v"],
    }, index=pd.to_datetime(j["t"], unit="s"))
    df.index.name = "Date"
    df["Adj Close"] = df["Close"]
    return df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]]


def fetch_symbol_info(code: str, timeout: int = 15) -> pd.Series:
    """Instrument metadata from the UDF ``/symbols`` endpoint. Empty Series on failure."""
    try:
        r = requests.get(f"{UDF_BASE}/symbols", params={"symbol": code},
                         headers=DEFAULT_HEADERS, timeout=timeout)
        r.raise_for_status()
        return pd.Series(r.json(), name="value")
    except (requests.RequestException, ValueError):
        return pd.Series(dtype="object", name="value")


def fetch_all_kase(code: str, start: str | datetime = "2019-01-01",
                   end: str | datetime | None = None) -> dict[str, pd.DataFrame | pd.Series]:
    """Mirror of `yfinance_fetcher.fetch_all`'s signature for KASE.

    Only ``ohlcv`` and ``info`` are populated. Fundamentals keys are returned as
    empty frames so callers can iterate uniformly — document missing artifacts
    rather than silently imputing.
    """
    return {
        "ohlcv": fetch_ohlcv_kase(code, start=start, end=end),
        "quarterly_financials": pd.DataFrame(),
        "quarterly_balance_sheet": pd.DataFrame(),
        "quarterly_cashflow": pd.DataFrame(),
        "info": fetch_symbol_info(code),
        "recommendations": pd.DataFrame(),
    }
