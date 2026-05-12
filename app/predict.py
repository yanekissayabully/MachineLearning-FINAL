"""Model loading and inference."""
from __future__ import annotations

import joblib
import numpy as np
import pandas as pd

model   = joblib.load("model_kz.pkl")
scaler  = joblib.load("scaler_kz.pkl")
encoder = joblib.load("label_encoder_kz.pkl")
features: list[str] = joblib.load("features_list.pkl")

def _normalize_label(raw) -> str:
    return str(raw).capitalize()


def predict_from_dict(values: dict[str, float]) -> dict:
    row = pd.DataFrame([{f: values.get(f, 0.0) for f in features}])
    scaled = scaler.transform(row)
    proba = model.predict_proba(scaled)[0]
    class_idx = int(np.argmax(proba))
    raw_label = encoder.inverse_transform([class_idx])[0]
    signal = _normalize_label(raw_label)

    # Build per-signal probabilities keyed by normalized class name
    classes = [_normalize_label(c) for c in encoder.classes_]
    prob_dict = {cls: float(proba[i]) for i, cls in enumerate(classes)}

    return {
        "signal": signal,
        "confidence": float(proba[class_idx]),
        "probabilities": {
            "Buy":  prob_dict.get("Buy", 0.0),
            "Hold": prob_dict.get("Hold", 0.0),
            "Sell": prob_dict.get("Sell", 0.0),
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
