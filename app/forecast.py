"""Model-v1 serving: loads the Phase-4 artifact and predicts bikes at
t+60 minutes.

Serving-features strategy (v1, documented in docs/phase-5.md): the lag
features are approximated by the hour-of-week climatology exported at
train time (model/artifacts/climatology.csv) because the service does
not yet store recent true history (see Parking Lot). `bikes_now` is the
live value; calendar features come from the feed timestamp (Dublin
time).
"""
import csv
from datetime import datetime, timedelta
from pathlib import Path

import joblib
import pandas as pd

ARTIFACT_DIR = Path(__file__).resolve().parents[1] / "model" / "artifacts"
HORIZON_MINUTES = 60


def load_bundle(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"model artifact missing: {path} — run model/train.py (Phase 4)"
        )
    return joblib.load(path)


def load_climatology(path: Path) -> dict:
    with open(path, newline="") as fh:
        return {
            int(row["hour_of_week"]): float(row["mean_bikes"])
            for row in csv.DictReader(fh)
        }


_BUNDLE = load_bundle(ARTIFACT_DIR / "model_v1.joblib")
MODEL = _BUNDLE["model"]
FEATURE_COLUMNS = _BUNDLE["feature_columns"]
MODEL_LABEL = f"model v1 (trained {_BUNDLE['trained']})"
CLIMATOLOGY = load_climatology(ARTIFACT_DIR / "climatology.csv")


def _clim(dt: datetime) -> float:
    return CLIMATOLOGY[dt.weekday() * 24 + dt.hour]


def build_serving_features(bikes_now: int, now: datetime) -> dict:
    return {
        "bikes_now": float(bikes_now),
        "lag_1h": _clim(now - timedelta(hours=1)),
        "lag_2h": _clim(now - timedelta(hours=2)),
        "lag_24h": _clim(now - timedelta(hours=24)),
        "lag_1w": _clim(now - timedelta(days=7)),
        "roll_3h": (
            _clim(now) + _clim(now - timedelta(hours=1)) + _clim(now - timedelta(hours=2))
        )
        / 3.0,
        "hour": float(now.hour),
        "dow": float(now.weekday()),
        "is_weekend": 1.0 if now.weekday() >= 5 else 0.0,
    }


def predict_from_features(features: dict) -> float:
    X = pd.DataFrame(
        [[features[c] for c in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS
    )
    return float(MODEL.predict(X)[0])


def forecast_bikes(bikes_now: int, now: datetime, capacity: int) -> int:
    raw = predict_from_features(build_serving_features(bikes_now, now))
    return max(0, min(capacity, round(raw)))
