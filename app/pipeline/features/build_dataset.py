# Vendored from StockClassifier commit 1bb70890f4dd9761ee486f04d3e23073d195b148
"""Assemble the final per-market training dataset (not used at serve time)."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from app.pipeline.features.technical import add_technical_features, TECHNICAL_COLS
from app.pipeline.features.fundamental import (
    build_quarterly_features,
    join_fundamentals_to_daily,
    FUNDAMENTAL_COLS,
)
from app.pipeline.labels.forward_return import add_forward_labels, class_distribution

ROOT = Path(__file__).resolve().parents[4]
RAW  = ROOT / "data" / "raw"
OUT  = ROOT / "data" / "features"

MIN_ROWS = 500


def _load_ohlcv(ticker_dir: Path) -> pd.DataFrame:
    p = ticker_dir / "ohlcv.csv"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p)
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    required = {"open", "high", "low", "close", "adj_close", "volume"}
    if not required.issubset(df.columns):
        return pd.DataFrame()
    return df[["date", "open", "high", "low", "close", "adj_close", "volume"]]


def build_ticker(ticker, ticker_dir, market, horizon=20, k=1.0):
    ohlcv = _load_ohlcv(ticker_dir)
    if len(ohlcv) < MIN_ROWS:
        return pd.DataFrame()
    df = add_technical_features(ohlcv)
    if market == "us":
        q = build_quarterly_features(ticker_dir)
        df = join_fundamentals_to_daily(df, q)
    df = add_forward_labels(df, horizon=horizon, k=k)
    df.insert(0, "ticker", ticker)
    return df


def build_market(market, horizon=20, k=1.0):
    market_dir = RAW / market
    if not market_dir.exists():
        raise FileNotFoundError(market_dir)
    frames = []
    for tdir in sorted(market_dir.iterdir()):
        if not tdir.is_dir():
            continue
        df = build_ticker(tdir.name, tdir, market, horizon=horizon, k=k)
        if not df.empty:
            frames.append(df)
    if not frames:
        raise RuntimeError(f"No viable tickers for market={market}")
    panel = pd.concat(frames, ignore_index=True)
    keep = ["ticker", "date", "open", "high", "low", "close", "adj_close", "volume"]
    keep += TECHNICAL_COLS
    if market == "us":
        keep += FUNDAMENTAL_COLS
    keep += ["sigma_20d", f"ret_fwd_{horizon}", "threshold", "label"]
    keep = [c for c in keep if c in panel.columns]
    panel = panel[keep]
    feat_cols = [c for c in TECHNICAL_COLS if c in panel.columns]
    panel = panel.dropna(subset=feat_cols + ["label"]).reset_index(drop=True)
    return panel
