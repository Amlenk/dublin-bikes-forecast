"""Phase 4 Step 1: persistence-baseline MAE, computed BEFORE any model
code exists (no sklearn imports — pandas arithmetic only).

Definition (locked, from docs/phase-4.md):
- Series: MOUNT STREET LOWER num_bikes_available, resampled to a regular
  10-min grid (bucket = last observation), forward-fill limited to 3
  steps (30 min); longer gaps stay NaN.
- Persistence prediction for target time T = grid value at T - 60 min.
- Held-out window: target times in [2026-05-18 00:00, 2026-06-01 00:00).
- MAE over rows where target and prediction are both non-NaN.
"""
from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
FILES = sorted(RAW.glob("dublin-bikes_station_status_*.csv"))
STATION = "MOUNT STREET LOWER"

frames = [
    pd.read_csv(
        f,
        usecols=["last_reported", "name", "num_bikes_available"],
        parse_dates=["last_reported"],
    )
    for f in FILES
]
st = pd.concat(frames)
st = st[st["name"] == STATION].sort_values("last_reported")
y = (
    st.set_index("last_reported")["num_bikes_available"]
    .resample("10min")
    .last()
    .ffill(limit=3)
)
pred = y.shift(6)  # value 60 minutes earlier
window = (y.index >= pd.Timestamp("2026-05-18")) & (
    y.index < pd.Timestamp("2026-06-01")
)
valid = window & y.notna() & pred.notna()
mae = (y[valid] - pred[valid]).abs().mean()
print(f"files: {[f.name for f in FILES]}")
print(f"holdout window: 2026-05-18 00:00 <= T < 2026-06-01 00:00")
print(f"valid rows: {int(valid.sum())}")
print(f"persistence_baseline_mae={mae:.4f}")
