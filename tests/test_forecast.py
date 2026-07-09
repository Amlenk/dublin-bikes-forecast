import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

import app.forecast as forecast

GOLDEN_INPUT = json.loads(
    (Path(__file__).parent / "fixtures" / "golden_input.json").read_text()
)
GOLDEN_PREDICTION = 17.9037  # scripts/golden_offline.py, recorded 2026-07-09
                             # BEFORE this serving code existed


def test_golden_parity_locally():
    assert round(forecast.predict_from_features(GOLDEN_INPUT), 4) == GOLDEN_PREDICTION


def test_serving_features_schema():
    feats = forecast.build_serving_features(18, datetime(2026, 7, 9, 9, 0))
    assert list(feats) == forecast.FEATURE_COLUMNS
    assert feats["bikes_now"] == 18.0
    assert feats["hour"] == 9.0
    assert feats["is_weekend"] == 0.0  # 2026-07-09 is a Thursday


class _StubModel:
    def __init__(self, value):
        self.value = value

    def predict(self, X):
        return np.array([self.value])


def test_forecast_clamped_low(monkeypatch):
    monkeypatch.setattr(forecast, "MODEL", _StubModel(-3.2))
    assert forecast.forecast_bikes(5, datetime(2026, 7, 9, 9, 0), 40) == 0


def test_forecast_clamped_high(monkeypatch):
    monkeypatch.setattr(forecast, "MODEL", _StubModel(99.0))
    assert forecast.forecast_bikes(5, datetime(2026, 7, 9, 9, 0), 40) == 40


def test_missing_artifact_fails_loudly(tmp_path):
    with pytest.raises(FileNotFoundError):
        forecast.load_bundle(tmp_path / "nope.joblib")
