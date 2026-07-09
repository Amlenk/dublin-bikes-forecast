"""Phase 3 audit: verify a historical dublinbikes dataset meets the
model-training thresholds fixed in docs/phase-3.md.

Usage: python scripts/audit_historical.py data/raw/<file.csv> [more files]
"""
import os
import sys

import pandas as pd

STATION = os.getenv("STATION_NAME", "MOUNT STREET LOWER")
USECOLS = ["last_reported", "station_id", "num_bikes_available", "name", "capacity"]


def load(paths: list) -> pd.DataFrame:
    frames = [
        pd.read_csv(p, usecols=USECOLS, parse_dates=["last_reported"])
        for p in paths
    ]
    return pd.concat(frames, ignore_index=True)


def median_interval_minutes(timestamps: pd.Series) -> float:
    deltas = timestamps.sort_values().diff().dropna()
    return deltas.median().total_seconds() / 60


def main(paths: list) -> None:
    df = load(paths)
    print(f"files: {len(paths)}")
    print(f"total rows: {len(df)}")
    print(f"columns: {list(df.columns)}")
    print(f"distinct stations: {df['name'].nunique()}")

    st = df[df["name"] == STATION].sort_values("last_reported")
    print(f"\nstation: {STATION}")
    print(f"rows: {len(st)}")
    if st.empty:
        sys.exit(f"FAIL: station {STATION!r} not found")

    tmin, tmax = st["last_reported"].min(), st["last_reported"].max()
    print(f"min timestamp: {tmin}")
    print(f"max timestamp: {tmax}")
    print(f"span days: {(tmax - tmin).days}")
    print(f"median interval minutes: {median_interval_minutes(st['last_reported']):.1f}")
    gaps = st["last_reported"].diff().dropna()
    print(f"max gap hours: {gaps.max().total_seconds() / 3600:.1f}")

    bikes = st["num_bikes_available"]
    print(f"bikes min: {bikes.min()}  max: {bikes.max()}")
    print(f"capacity values seen: {sorted(st['capacity'].unique())}")

    week_end = tmax.normalize()
    week = st[
        (st["last_reported"] >= week_end - pd.Timedelta(days=7))
        & (st["last_reported"] < week_end)
    ]
    print(
        f"std of bikes over most recent full week "
        f"({(week_end - pd.Timedelta(days=7)).date()}..{week_end.date()}): "
        f"{week['num_bikes_available'].std():.2f}  (rows: {len(week)})"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python scripts/audit_historical.py <csv> [csv ...]")
    main(sys.argv[1:])
