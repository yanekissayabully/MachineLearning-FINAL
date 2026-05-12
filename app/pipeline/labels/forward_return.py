# Vendored from StockClassifier commit 1bb70890f4dd9761ee486f04d3e23073d195b148
"""Forward-return labels with volatility-adjusted thresholds."""
from __future__ import annotations

import numpy as np
import pandas as pd

BUY, HOLD, SELL = 0, 1, 2


def add_forward_labels(
    df: pd.DataFrame,
    horizon: int = 20,
    k: float = 1.0,
    vol_window: int = 20,
    price_col: str = "adj_close",
) -> pd.DataFrame:
    out = df.copy()
    price = out[price_col].astype(float)
    log_ret_1d = np.log(price / price.shift(1))
    sigma_daily = log_ret_1d.rolling(vol_window, min_periods=vol_window).std()

    out[f"sigma_{vol_window}d"] = sigma_daily
    out[f"ret_fwd_{horizon}"] = np.log(price.shift(-horizon) / price)
    out["threshold"] = k * sigma_daily * np.sqrt(horizon)

    r = out[f"ret_fwd_{horizon}"]
    thr = out["threshold"]
    label = pd.Series(np.where(r > thr, BUY, np.where(r < -thr, SELL, HOLD)), index=out.index, dtype="float")
    label[r.isna() | thr.isna()] = np.nan
    out["label"] = label
    return out


def class_distribution(labels: pd.Series) -> dict[str, float]:
    counts = labels.dropna().value_counts(normalize=True).to_dict()
    return {
        "buy":  float(counts.get(BUY, 0.0)),
        "hold": float(counts.get(HOLD, 0.0)),
        "sell": float(counts.get(SELL, 0.0)),
    }
