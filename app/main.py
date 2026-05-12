"""FastAPI serving layer for the KZ stock classifier."""
from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Stock Classifier API", version="1.0")


# ── /info ──────────────────────────────────────────────────────────────────────

@app.get("/info")
def info():
    from app.predict import features, model, encoder
    return {
        "model": type(model).__name__,
        "market": "kz",
        "feature_count": len(features),
        "features": features,
        "classes": encoder.classes_.tolist(),
    }


# ── /predict (manual features) ────────────────────────────────────────────────

class FeaturesRequest(BaseModel):
    features: dict[str, float]


@app.post("/predict")
def predict(req: FeaturesRequest):
    from app.predict import predict_from_dict
    return predict_from_dict(req.features)


# ── /predict/ticker (live fetch) ──────────────────────────────────────────────

class TickerRequest(BaseModel):
    ticker: str
    market: Literal["kz", "us", "auto"] = "auto"


@app.post("/predict/ticker")
def predict_ticker(req: TickerRequest):
    from app.predict import predict_from_ohlcv
    from app.pipeline.ingest.tickers import KASE_TICKERS

    ticker = req.ticker.strip().upper()

    if req.market == "auto":
        # Case-insensitive lookup since KASE tickers can have mixed case (e.g. "AMGZp")
        kase_upper = {t.upper() for t in KASE_TICKERS}
        market = "kz" if ticker in kase_upper else "us"
    else:
        market = req.market

    try:
        if market == "kz":
            from app.pipeline.ingest.kase_fetcher import fetch_ohlcv_kase
            # Restore original casing for KASE endpoint
            kase_map = {t.upper(): t for t in KASE_TICKERS}
            kase_ticker = kase_map.get(ticker, ticker)
            df = fetch_ohlcv_kase(kase_ticker, start="2020-01-01")
        else:
            from app.pipeline.ingest.yfinance_fetcher import fetch_ohlcv
            df = fetch_ohlcv(ticker, period="3y")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Data fetch failed: {e}")

    if df is None or len(df) < 60:
        raise HTTPException(status_code=404, detail=f"Not enough data for {ticker}")

    try:
        result = predict_from_ohlcv(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    result["ticker"] = ticker
    result["market"] = market
    return result
