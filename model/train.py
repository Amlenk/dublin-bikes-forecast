"""Phase 4 trainer: HistGradientBoostingRegressor vs the pre-committed
persistence baseline (model/EVAL.md Step 1 — recorded before this file
existed; the anchor requires reproducing it +/-0.01 and beating it).

Run from repo root: python model/train.py
"""
import sys
from datetime import date
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.ensemble import HistGradientBoostingRegressor

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from model.features import (  # noqa: E402
    FEATURE_COLUMNS,
    HORIZON_STEPS,
    build_features,
    resample_station,
    split_holdout,
)

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "data" / "raw"
ARTIFACTS = REPO / "model" / "artifacts"
STATION = "MOUNT STREET LOWER"
HOLDOUT_START = pd.Timestamp("2026-05-18")
HOLDOUT_END = pd.Timestamp("2026-06-01")


def load_series() -> pd.Series:
    files = sorted(RAW.glob("dublin-bikes_station_status_*.csv"))
    frames = [
        pd.read_csv(
            f,
            usecols=["last_reported", "name", "num_bikes_available"],
            parse_dates=["last_reported"],
        )
        for f in files
    ]
    return resample_station(pd.concat(frames), STATION)


def persistence_mae_step1_definition(y: pd.Series) -> tuple:
    """Identical definition to scripts/baseline_persistence.py."""
    pred = y.shift(HORIZON_STEPS)
    window = (y.index >= HOLDOUT_START) & (y.index < HOLDOUT_END)
    valid = window & y.notna() & pred.notna()
    return (y[valid] - pred[valid]).abs().mean(), int(valid.sum())


def main() -> None:
    y = load_series()
    baseline_mae, baseline_rows = persistence_mae_step1_definition(y)

    frame = build_features(y)
    train, holdout = split_holdout(frame, HOLDOUT_START, HOLDOUT_END)
    model = HistGradientBoostingRegressor(random_state=42)
    model.fit(train[FEATURE_COLUMNS], train["target"])
    pred = model.predict(holdout[FEATURE_COLUMNS])
    model_mae = (holdout["target"] - pred).abs().mean()
    persistence_same_rows = (holdout["target"] - holdout["bikes_now"]).abs().mean()

    ARTIFACTS.mkdir(exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "feature_columns": FEATURE_COLUMNS,
            "station": STATION,
            "trained": str(date.today()),
            "sklearn_version": sklearn.__version__,
        },
        ARTIFACTS / "model_v1.joblib",
    )
    # Hour-of-week climatology from TRAIN rows only (Phase 5 serving lags).
    train_y = y[y.index < HOLDOUT_START].dropna()
    how = train_y.index.dayofweek * 24 + train_y.index.hour
    train_y.groupby(how).mean().rename("mean_bikes").rename_axis(
        "hour_of_week"
    ).round(3).to_csv(ARTIFACTS / "climatology.csv")

    lines = [
        f"train rows: {len(train)}  holdout rows: {len(holdout)}",
        f"persistence on model holdout rows: mae={persistence_same_rows:.4f}",
        f"baseline_mae={baseline_mae:.4f} (step-1 definition, rows={baseline_rows})",
        f"model_mae={model_mae:.4f}",
    ]
    print("\n".join(lines))

    with open(REPO / "model" / "EVAL.md", "a", encoding="utf-8") as fh:
        fh.write(
            f"\n### Run {date.today()} — HistGradientBoostingRegressor"
            f" (sklearn {sklearn.__version__})\n\n```\n" + "\n".join(lines) + "\n```\n"
        )


if __name__ == "__main__":
    main()
