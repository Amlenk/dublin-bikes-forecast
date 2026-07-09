# Model evaluation record

## Step 1 — persistence baseline (recorded BEFORE any model code)

Recorded 2026-07-09 by running `scripts/baseline_persistence.py`
(pandas-only, no model imports). **This entry must not be edited.**
The Phase 4 anchor requires `model/train.py` to (a) reproduce this
number ±0.01 with its own evaluation harness and (b) achieve a
strictly lower model MAE on the same window.

- Station: MOUNT STREET LOWER
- Series definition: `num_bikes_available` resampled to a regular
  10-minute grid (bucket = last observation), forward-fill limited to
  3 steps (30 min), longer gaps NaN.
- Persistence prediction for target time T = grid value at T − 60 min.
- Held-out window: target times in [2026-05-18 00:00, 2026-06-01 00:00).
- Valid rows (target and prediction non-NaN): **2016**
- **persistence_baseline_mae = 2.0843**

Observed output:

```
files: ['dublin-bikes_station_status_032026.csv', 'dublin-bikes_station_status_042026.csv', 'dublin-bikes_station_status_052026.csv']
holdout window: 2026-05-18 00:00 <= T < 2026-06-01 00:00
valid rows: 2016
persistence_baseline_mae=2.0843
```

## Training runs

_(appended by `model/train.py`)_

### Run 2026-07-09 — HistGradientBoostingRegressor (sklearn 1.9.0)

```
train rows: 10138  holdout rows: 2016
persistence on model holdout rows: mae=2.0843
baseline_mae=2.0843 (step-1 definition, rows=2016)
model_mae=1.6150
```
