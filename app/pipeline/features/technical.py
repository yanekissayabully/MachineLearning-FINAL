# Vendored from StockClassifier commit 1bb70890f4dd9761ee486f04d3e23073d195b148
"""Technical indicators for a single-ticker OHLCV frame.

Input: DataFrame with columns [open, high, low, close, adj_close, volume], sorted by date.
Output: same frame with ~23 technical feature columns appended.
All features use only information available up to row t (no look-ahead).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

TECHNICAL_COLS = [
    "ret_1d", "ret_5d", "ret_10d", "ret_20d",
    "sma_20", "sma_50", "ema_12", "ema_26", "price_to_sma50",
    "rsi_14", "macd", "macd_signal", "macd_hist", "stoch_k",
    "bb_upper", "bb_lower", "bb_width", "atr_14",
    "volume_ratio_20", "volume_roc", "obv",
    "overnight_gap", "intraday_range",
]


def add_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    close = out["adj_close"].astype(float)
    high  = out["high"].astype(float)
    low   = out["low"].astype(float)
    open_ = out["open"].astype(float)
    vol   = out["volume"].astype(float)

    # Returns (log)
    log_close = np.log(close)
    out["ret_1d"]  = log_close.diff(1)
    out["ret_5d"]  = log_close.diff(5)
    out["ret_10d"] = log_close.diff(10)
    out["ret_20d"] = log_close.diff(20)

    # Trend
    out["sma_20"] = SMAIndicator(close, window=20).sma_indicator()
    out["sma_50"] = SMAIndicator(close, window=50).sma_indicator()
    out["ema_12"] = EMAIndicator(close, window=12).ema_indicator()
    out["ema_26"] = EMAIndicator(close, window=26).ema_indicator()
    out["price_to_sma50"] = close / out["sma_50"]

    # Momentum
    out["rsi_14"] = RSIIndicator(close, window=14).rsi()
    macd = MACD(close)
    out["macd"]        = macd.macd()
    out["macd_signal"] = macd.macd_signal()
    out["macd_hist"]   = macd.macd_diff()
    out["stoch_k"] = StochasticOscillator(high=high, low=low, close=close, window=14, smooth_window=3).stoch()

    # Volatility
    bb = BollingerBands(close, window=20, window_dev=2)
    out["bb_upper"] = bb.bollinger_hband()
    out["bb_lower"] = bb.bollinger_lband()
    out["bb_width"] = (out["bb_upper"] - out["bb_lower"]) / out["sma_20"]
    out["atr_14"]   = AverageTrueRange(high=high, low=low, close=close, window=14).average_true_range()

    # Volume
    vol_sma20 = vol.rolling(20, min_periods=20).mean()
    out["volume_ratio_20"] = vol / vol_sma20
    out["volume_roc"] = vol.pct_change(10)
    out["obv"] = OnBalanceVolumeIndicator(close=close, volume=vol).on_balance_volume()

    # Microstructure
    out["overnight_gap"]   = np.log(open_ / close.shift(1))
    out["intraday_range"]  = (high - low) / open_

    return out
