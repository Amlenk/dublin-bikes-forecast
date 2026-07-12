"""One-off: load the Smart Dublin monthly GBFS archives (data/raw/*.csv)
into the `history` table (Neon Postgres — see db/schema.sql).

Usage: python scripts/backfill_history.py data/raw/*.csv

Refuses to run against a non-empty history table (it is a one-off
backfill, not an appender). Duplicate (station_id, last_reported) rows
within/across the CSVs are dropped before COPY. Timestamps are the
CSVs' naive last_reported values stored as UTC — the same convention
model/train.py uses for these files.
"""
import os
import sys
from pathlib import Path

import pandas as pd
import psycopg

REPO = Path(__file__).resolve().parents[1]

USECOLS = [
    "last_reported",
    "station_id",
    "num_bikes_available",
    "num_docks_available",
    "name",
    "capacity",
]

COPY_SQL = (
    "COPY history"
    " (station_id, station_name, ts, available_bikes, available_stands,"
    " capacity) FROM STDIN"
)


def env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    env_file = REPO / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.strip().startswith(name + "="):
                return line.split("=", 1)[1].strip()
    sys.exit(f"{name} not set (env var or .env)")


def load_frames(paths: list) -> pd.DataFrame:
    frames = [
        pd.read_csv(p, usecols=USECOLS, parse_dates=["last_reported"])
        for p in paths
    ]
    df = pd.concat(frames, ignore_index=True)
    before = len(df)
    df = df.drop_duplicates(subset=["station_id", "last_reported"])
    df["last_reported"] = df["last_reported"].dt.tz_localize("UTC")
    print(f"csv rows: {before}  after dedupe: {len(df)}")
    return df


def main(paths: list) -> None:
    df = load_frames(paths)
    with psycopg.connect(env("DATABASE_URL")) as conn, conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM history")
        existing = cur.fetchone()[0]
        if existing:
            sys.exit(f"history already has {existing} rows — refusing to backfill twice")
        with cur.copy(COPY_SQL) as copy:
            for row in df.itertuples(index=False):
                copy.write_row(
                    (
                        int(row.station_id),
                        row.name,
                        row.last_reported,
                        int(row.num_bikes_available),
                        int(row.num_docks_available),
                        int(row.capacity),
                    )
                )
        cur.execute("SELECT count(*), count(DISTINCT station_name), min(ts), max(ts) FROM history")
        n, stations, tmin, tmax = cur.fetchone()
    print(f"history rows: {n}  stations: {stations}")
    print(f"span: {tmin} .. {tmax}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python scripts/backfill_history.py <csv> [csv ...]")
    main(sys.argv[1:])
