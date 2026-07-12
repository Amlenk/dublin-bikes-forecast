"""Regression guards for app/lags.py (no DB required)."""
from datetime import datetime, timedelta, timezone

from app.forecast import build_serving_features
from app.lags import lags_from_rows, recent_lags

NOW = datetime(2026, 7, 11, 12, 0, tzinfo=timezone.utc)


def rows_every_30min(start: datetime, end: datetime, bikes: int = 7) -> list:
    rows, t = [], start
    while t <= end:
        rows.append((t, bikes))
        t += timedelta(minutes=30)
    return rows


def test_full_week_of_rows_yields_all_five_lags():
    rows = rows_every_30min(NOW - timedelta(days=8), NOW)
    lags = lags_from_rows(rows, NOW)
    assert sorted(lags) == sorted(["lag_1h", "lag_2h", "lag_24h", "lag_1w", "roll_3h"])
    assert lags["lag_1h"] == 7.0
    assert lags["roll_3h"] == 7.0


def test_short_history_yields_only_supported_lags():
    # 4 hours of data: lag_1h/2h/roll_3h supported, 24h/1w not
    rows = rows_every_30min(NOW - timedelta(hours=4), NOW)
    lags = lags_from_rows(rows, NOW)
    assert sorted(lags) == ["lag_1h", "lag_2h", "roll_3h"]


def test_gap_beyond_ffill_limit_drops_the_lag():
    # rows stop 90 min before NOW: 10-min grid + ffill(limit=3) cannot
    # reach NOW-1h, so lag_1h must be absent
    rows = rows_every_30min(NOW - timedelta(hours=4), NOW - timedelta(minutes=90))
    lags = lags_from_rows(rows, NOW)
    assert "lag_1h" not in lags
    assert "roll_3h" not in lags


def test_empty_rows_yield_no_lags():
    assert lags_from_rows([], NOW) == {}


def test_real_lags_overlay_climatology():
    base = build_serving_features(10, NOW)
    mixed = build_serving_features(10, NOW, {"lag_1h": 3.0, "roll_3h": 4.5})
    assert mixed["lag_1h"] == 3.0
    assert mixed["roll_3h"] == 4.5
    assert mixed["lag_1w"] == base["lag_1w"]  # untouched lags keep climatology
    assert mixed["bikes_now"] == 10.0


def test_recent_lags_without_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert recent_lags("MOUNT STREET LOWER", NOW) == (None, [])
