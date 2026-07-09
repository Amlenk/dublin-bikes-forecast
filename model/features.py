"""Feature builder for the t+60min availability forecast.

Grid convention (locked in docs/phase-4.md and model/EVAL.md):
regular 10-minute grid, bucket = last observation, forward-fill limited
to 3 steps (30 min); longer gaps stay NaN and any feature row touching
one is dropped.
"""
import pandas as pd

GRID = "10min"
STEPS_PER_HOUR = 6
HORIZON_STEPS = 6  # 60 minutes ahead

FEATURE_COLUMNS = [
    "bikes_now",
    "lag_1h",
    "lag_2h",
    "lag_24h",
    "lag_1w",
    "roll_3h",
    "hour",
    "dow",
    "is_weekend",
]


def resample_station(df: pd.DataFrame, station: str) -> pd.Series:
    st = df[df["name"] == station].sort_values("last_reported")
    return (
        st.set_index("last_reported")["num_bikes_available"]
        .resample(GRID)
        .last()
        .ffill(limit=3)
    )


def build_features(y: pd.Series) -> pd.DataFrame:
    """Return a frame indexed by feature time t with FEATURE_COLUMNS,
    plus `target` = y(t+60min) and `target_time` = t+60min. NaN rows
    are NOT dropped here (callers drop after splitting)."""
    out = pd.DataFrame(index=y.index)
    out["bikes_now"] = y
    out["lag_1h"] = y.shift(1 * STEPS_PER_HOUR)
    out["lag_2h"] = y.shift(2 * STEPS_PER_HOUR)
    out["lag_24h"] = y.shift(24 * STEPS_PER_HOUR)
    out["lag_1w"] = y.shift(7 * 24 * STEPS_PER_HOUR)
    out["roll_3h"] = y.rolling(3 * STEPS_PER_HOUR, min_periods=3 * STEPS_PER_HOUR).mean()
    out["hour"] = out.index.hour
    out["dow"] = out.index.dayofweek
    out["is_weekend"] = (out.index.dayofweek >= 5).astype(int)
    out["target"] = y.shift(-HORIZON_STEPS)
    out["target_time"] = out.index + pd.Timedelta(minutes=60)
    return out


def split_holdout(frame: pd.DataFrame, holdout_start: pd.Timestamp,
                  holdout_end: pd.Timestamp):
    """Chronological split on target_time; drops NaN rows in each part."""
    complete = frame.dropna(subset=FEATURE_COLUMNS + ["target"])
    train = complete[complete["target_time"] < holdout_start]
    holdout = complete[
        (complete["target_time"] >= holdout_start)
        & (complete["target_time"] < holdout_end)
    ]
    return train, holdout
