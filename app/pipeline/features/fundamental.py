# Vendored from StockClassifier commit 1bb70890f4dd9761ee486f04d3e23073d195b148
"""Quarterly fundamental features for US tickers."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUB_LAG_DAYS = 45

FUNDAMENTAL_COLS = [
    "eps", "revenue", "revenue_growth_yoy",
    "gross_margin", "operating_margin", "net_margin",
    "roe", "debt_to_equity", "current_ratio",
    "fcf", "operating_cf",
    "pe_ttm", "pb", "ps_ttm",
    "days_since_report",
]


def _load_statement(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, index_col=0)
    df = df.T
    df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[df.index.notna()].sort_index()
    return df.apply(pd.to_numeric, errors="coerce")


def _get(df: pd.DataFrame, *names: str) -> pd.Series:
    for n in names:
        if n in df.columns:
            return df[n]
    return pd.Series(np.nan, index=df.index, dtype=float)


def build_quarterly_features(ticker_dir: Path) -> pd.DataFrame:
    inc = _load_statement(ticker_dir / "quarterly_financials.csv")
    bs  = _load_statement(ticker_dir / "quarterly_balance_sheet.csv")
    cf  = _load_statement(ticker_dir / "quarterly_cashflow.csv")

    if inc.empty and bs.empty and cf.empty:
        return pd.DataFrame()

    idx = inc.index.union(bs.index).union(cf.index)
    out = pd.DataFrame(index=idx)

    revenue = _get(inc, "Total Revenue", "Operating Revenue")
    gross_profit = _get(inc, "Gross Profit")
    op_income = _get(inc, "Operating Income", "Total Operating Income As Reported")
    net_income = _get(inc, "Net Income", "Net Income Common Stockholders")
    eps = _get(inc, "Diluted EPS", "Basic EPS")

    out["revenue"] = revenue
    out["eps"] = eps
    out["gross_margin"]     = gross_profit / revenue
    out["operating_margin"] = op_income / revenue
    out["net_margin"]       = net_income / revenue
    out["revenue_growth_yoy"] = revenue.pct_change(periods=4)

    total_debt = _get(bs, "Total Debt", "Long Term Debt And Capital Lease Obligation")
    equity = _get(bs, "Stockholders Equity", "Common Stock Equity", "Total Equity Gross Minority Interest")
    cur_assets = _get(bs, "Current Assets")
    cur_liab   = _get(bs, "Current Liabilities")

    out["debt_to_equity"] = total_debt / equity
    out["current_ratio"]  = cur_assets / cur_liab
    out["roe"] = net_income / equity

    out["fcf"]          = _get(cf, "Free Cash Flow")
    out["operating_cf"] = _get(cf, "Operating Cash Flow", "Cash Flow From Continuing Operating Activities")

    out["shares_out"] = _get(bs, "Ordinary Shares Number", "Share Issued")
    out["equity_total"] = equity

    out = out.reset_index().rename(columns={"index": "quarter_end"})
    out["publication_date"] = out["quarter_end"] + pd.Timedelta(days=PUB_LAG_DAYS)
    return out.sort_values("publication_date").reset_index(drop=True)


def join_fundamentals_to_daily(daily: pd.DataFrame, quarterly: pd.DataFrame) -> pd.DataFrame:
    if quarterly.empty:
        for c in FUNDAMENTAL_COLS:
            daily[c] = np.nan
        return daily

    q = quarterly.sort_values("publication_date").copy()
    q["eps_ttm"]     = q["eps"].rolling(4, min_periods=4).sum()
    q["revenue_ttm"] = q["revenue"].rolling(4, min_periods=4).sum()

    d = daily.sort_values("date").copy()
    d["date"] = pd.to_datetime(d["date"])
    q_for_join = q[[
        "publication_date", "quarter_end",
        "eps", "revenue", "revenue_growth_yoy",
        "gross_margin", "operating_margin", "net_margin",
        "roe", "debt_to_equity", "current_ratio",
        "fcf", "operating_cf",
        "shares_out", "equity_total", "eps_ttm", "revenue_ttm",
    ]].copy()

    merged = pd.merge_asof(
        d, q_for_join,
        left_on="date", right_on="publication_date",
        direction="backward",
    )

    price = merged["adj_close"].astype(float)
    market_cap = price * merged["shares_out"]
    merged["pe_ttm"] = price / merged["eps_ttm"]
    merged["pb"]     = market_cap / merged["equity_total"]
    merged["ps_ttm"] = market_cap / merged["revenue_ttm"]
    merged["days_since_report"] = (merged["date"] - merged["publication_date"]).dt.days

    merged = merged.drop(columns=[
        "publication_date", "quarter_end", "shares_out", "equity_total",
        "eps_ttm", "revenue_ttm",
    ])
    return merged
