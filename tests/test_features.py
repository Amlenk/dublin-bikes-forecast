import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from model.features import (
    FEATURE_COLUMNS,
    build_features,
    split_holdout,
)


def ramp_series(n=1200):
    """y(i) = i on a clean 10-min grid — lag values are hand-checkable."""
    idx = pd.date_range("2026-05-01", periods=n, freq="10min")
    return pd.Series(np.arange(n, dtype=float), index=idx)


def test_lags_match_hand_computed_positions():
    frame = build_features(ramp_series())
    row = frame.iloc[1010]  # i=1010: all lags defined
    assert row["bikes_now"] == 1010
    assert row["lag_1h"] == 1010 - 6
    assert row["lag_2h"] == 1010 - 12
    assert row["lag_24h"] == 1010 - 144
    assert row["lag_1w"] == 1010 - 1008
    assert row["roll_3h"] == np.mean(np.arange(1010 - 17, 1011))
    assert row["target"] == 1010 + 6


def test_no_leakage_target_is_strictly_later():
    frame = build_features(ramp_series())
    assert (frame["target_time"] > frame.index).all()
    # target equals the series value AT target_time, never earlier
    row = frame.iloc[100]
    assert row["target"] == 100 + 6


def test_chronological_split():
    frame = build_features(ramp_series(3000))
    cut = frame["target_time"].iloc[2000]
    train, holdout = split_holdout(frame, cut, frame["target_time"].iloc[-1])
    assert train["target_time"].max() < holdout["target_time"].min()
    assert not train[FEATURE_COLUMNS + ["target"]].isna().any().any()


def test_artifact_round_trip(tmp_path):
    rng = np.random.default_rng(0)
    X = rng.uniform(0, 40, size=(200, len(FEATURE_COLUMNS)))
    y = rng.uniform(0, 40, size=200)
    model = HistGradientBoostingRegressor(random_state=0).fit(X, y)
    path = tmp_path / "m.joblib"
    joblib.dump({"model": model, "feature_columns": FEATURE_COLUMNS}, path)
    loaded = joblib.load(path)
    pred = loaded["model"].predict(X[:1])[0]
    assert -5 <= pred <= 50
