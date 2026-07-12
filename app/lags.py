"""Real lag features from the `snapshots` table (Neon Postgres).

Rebuilds the exact training grid (10-minute buckets, last observation,
forward-fill limit 3 — see model/features.py) from the station's recent
snapshot rows and reads the lag features off it. Any lag the history
cannot support (grid gap, or the table is younger than the lag horizon)
is omitted so the caller falls back to climatology for that lag only.

No DATABASE_URL in the environment, or any DB error, means (None, []):
serving then behaves exactly as before this module existed.
"""
import os
from datetime import datetime, timedelta

import pandas as pd

WINDOW_DAYS = 8  # covers lag_1w plus margin
CONNECT_TIMEOUT_S = 3

LAG_OFFSETS = {
    "lag_1h": timedelta(hours=1),
    "lag_2h": timedelta(hours=2),
    "lag_24h": timedelta(hours=24),
    "lag_1w": timedelta(days=7),
}
ROLL_STEPS = 18  # 3 h of 10-min steps, min_periods=18 in training


def lags_from_rows(rows: list, now: datetime) -> dict:
    """rows: [(ts, available_bikes), ...] UTC-aware. Returns only the
    lag features the grid can support, mirroring training semantics."""
    if not rows:
        return {}
    y = (
        pd.Series(
            [bikes for _, bikes in rows],
            index=pd.DatetimeIndex([ts for ts, _ in rows], tz="UTC"),
        )
        .sort_index()
        .resample("10min")
        .last()
        .ffill(limit=3)
    )
    t = pd.Timestamp(now).floor("10min")
    out = {}
    for name, offset in LAG_OFFSETS.items():
        when = t - offset
        if when in y.index and pd.notna(y[when]):
            out[name] = float(y[when])
    window = y[y.index > t - timedelta(minutes=10 * ROLL_STEPS)]
    window = window[window.index <= t]
    if len(window) == ROLL_STEPS and window.notna().all():
        out["roll_3h"] = float(window.mean())
    return out


def recent_lags(station_name: str, now: datetime) -> tuple:
    """Returns (lags dict or None, sorted list of live lag names)."""
    url = os.getenv("DATABASE_URL")
    if not url:
        return None, []
    try:
        import psycopg

        with psycopg.connect(url, connect_timeout=CONNECT_TIMEOUT_S) as conn:
            rows = conn.execute(
                "SELECT ts, available_bikes FROM snapshots"
                " WHERE station_name = %s AND ts > %s ORDER BY ts",
                (station_name, now - timedelta(days=WINDOW_DAYS)),
            ).fetchall()
    except Exception:
        return None, []
    lags = lags_from_rows(rows, now)
    return (lags or None), sorted(lags)
