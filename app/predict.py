"""Model loading and inference."""
from __future__ import annotations

import joblib
import numpy as np
import pandas as pd

model   = joblib.load("model_kz.pkl")
scaler  = joblib.load("scaler_kz.pkl")
encoder = joblib.load("label_encoder_kz.pkl")
features: list[str] = joblib.load("features_list.pkl")

LABEL_MAP = {0: "Buy", 1: "Hold", 2: "Sell"}


def predict_from_dict(values: dict[str, float]) -> dict:
    row = pd.DataFrame([{f: values.get(f, 0.0) for f in features}])
    scaled = scaler.transform(row)
    proba = model.predict_proba(scaled)[0]
    class_idx = int(np.argmax(proba))
    # encoder.inverse_transform gives original int label (0/1/2)
    label_int = int(encoder.inverse_transform([class_idx])[0])
    signal = LABEL_MAP.get(label_int, str(label_int))
    return {
        "signal": signal,
        "confidence": float(proba[class_idx]),
        "probabilities": {
            "Buy":  float(proba[encoder.transform([0])[0]]) if 0 in encoder.classes_ else 0.0,
            "Hold": float(proba[encoder.transform([1])[0]]) if 1 in encoder.classes_ else 0.0,
            "Sell": float(proba[encoder.transform([2])[0]]) if 2 in encoder.classes_ else 0.0,
        },
    }


def predict_from_ohlcv(df: pd.DataFrame) -> dict:
    """Compute features from a raw OHLCV frame and predict on the last row."""
    from app.pipeline.features.technical import add_technical_features
    from app.pipeline.labels.forward_return import add_forward_labels

    df = df.copy()
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    df = df.rename(columns={"adj_close": "adj_close"})

    df = add_technical_features(df)
    # sigma_20d is needed by the model
    log_ret = np.log(df["adj_close"] / df["adj_close"].shift(1))
    df["sigma_20d"] = log_ret.rolling(20, min_periods=20).std()

    last = df.iloc[-1]
    return predict_from_dict(last.to_dict())
