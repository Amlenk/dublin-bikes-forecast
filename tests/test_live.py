import json
from pathlib import Path

import pytest

from app.live import LiveFeedError, parse_station

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "stations_sample.json").read_text()
)


def test_parse_station_extracts_fields():
    snap = parse_station(FIXTURE, "MOUNT STREET LOWER")
    # Values from the captured real payload (tests/fixtures/stations_sample.json)
    assert snap.station == "MOUNT STREET LOWER"
    assert snap.bikes == 18
    assert snap.stands == 22
    assert snap.capacity == 40
    assert snap.updated.year == 2026


def test_parse_station_missing_station_raises():
    with pytest.raises(LiveFeedError):
        parse_station(FIXTURE, "NO SUCH STATION")
