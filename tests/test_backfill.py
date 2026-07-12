"""Regression guards for scripts/backfill_history.py (no DB required)."""
from pathlib import Path

import pandas as pd

from scripts.backfill_history import COPY_SQL, load_frames

FIXTURE = Path(__file__).parent / "fixtures" / "station_status_sample.csv"


def test_load_frames_maps_fixture_columns():
    df = load_frames([FIXTURE])
    row = df.iloc[0]
    assert row["name"] == "CLARENDON ROW"
    assert int(row["station_id"]) == 1
    assert int(row["num_bikes_available"]) == 0
    assert int(row["num_docks_available"]) == 31
    assert int(row["capacity"]) == 31
    assert str(row["last_reported"]) == "2026-05-01 00:05:00+00:00"


def test_load_frames_dedupes_station_timestamp_pairs():
    df = load_frames([FIXTURE, FIXTURE])  # same file twice = all dupes
    assert len(df) == len(load_frames([FIXTURE]))
    assert not df.duplicated(subset=["station_id", "last_reported"]).any()


def test_copy_targets_history_not_snapshots():
    assert "COPY history" in COPY_SQL
    assert "snapshots" not in COPY_SQL
