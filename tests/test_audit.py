from pathlib import Path

import pandas as pd

from scripts.audit_historical import load, median_interval_minutes

FIXTURE = Path(__file__).parent / "fixtures" / "station_status_sample.csv"


def test_median_interval_on_known_gaps():
    # 10, 10, 30, 10 minute gaps -> median 10
    ts = pd.Series(
        pd.to_datetime(
            ["2026-03-01 00:00", "2026-03-01 00:10", "2026-03-01 00:20",
             "2026-03-01 00:50", "2026-03-01 01:00"]
        )
    )
    assert median_interval_minutes(ts) == 10.0


def test_load_parses_real_rows():
    df = load([FIXTURE])
    assert len(df) == 3
    assert pd.api.types.is_datetime64_any_dtype(df["last_reported"])
    assert df["last_reported"].iloc[0] == pd.Timestamp("2026-05-01 00:05:00")
    assert set(df["name"]) == {"CLARENDON ROW", "DAME STREET", "HEUSTON BRIDGE (SOUTH)"}
    assert df["num_bikes_available"].tolist() == [0, 7, 24]
