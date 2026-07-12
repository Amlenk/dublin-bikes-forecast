"""Regression guards for app/sparkline.py and the 24h point filter."""
from datetime import datetime, timedelta, timezone

from app.lags import points_last_24h
from app.sparkline import HEIGHT, PAD_BOTTOM, PAD_TOP, build_sparkline

NOW = datetime(2026, 7, 12, 12, 0, tzinfo=timezone.utc)


def points(n: int, bikes: int = 5) -> list:
    return [(NOW - timedelta(minutes=30 * (n - 1 - i)), bikes) for i in range(n)]


def test_fewer_than_two_points_yields_no_chart():
    assert build_sparkline([], 40) is None
    assert build_sparkline(points(1), 40) is None


def test_one_hover_target_per_point():
    svg = build_sparkline(points(48), 40)
    assert svg.count("<title>") == 48
    assert svg.count("bikes</title>") == 48


def test_y_scale_pins_zero_to_baseline_and_capacity_to_top():
    base = HEIGHT - PAD_BOTTOM
    svg_empty = build_sparkline([(NOW - timedelta(hours=1), 0), (NOW, 0)], 40)
    assert f"points=\"26.0,{float(base)} 312.0,{float(base)}\"" in svg_empty
    svg_full = build_sparkline([(NOW - timedelta(hours=1), 40), (NOW, 40)], 40)
    assert f"312.0,{float(PAD_TOP)}" in svg_full


def test_values_above_capacity_are_clamped():
    svg = build_sparkline([(NOW - timedelta(hours=1), 99), (NOW, 99)], 40)
    assert f"312.0,{float(PAD_TOP)}" in svg  # clamped to capacity line


def test_points_last_24h_filters_older_rows():
    rows = [(NOW - timedelta(hours=30), 3), (NOW - timedelta(hours=2), 4), (NOW, 5)]
    assert points_last_24h(rows, NOW) == rows[1:]
