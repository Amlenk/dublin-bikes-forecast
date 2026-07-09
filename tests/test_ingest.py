import json
from datetime import timezone
from pathlib import Path

import pytest

from scripts.ingest_snapshot import INSERT_SQL, main, parse_rows

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "stations_sample.json").read_text()
)


def test_parse_rows_maps_payload_to_column_tuples():
    rows = parse_rows(FIXTURE)
    assert len(rows) == 3
    station_id, name, ts, bikes, stands = rows[0]
    # Values from the captured real payload (MOUNT STREET LOWER first)
    assert name == "MOUNT STREET LOWER"
    assert isinstance(station_id, int)
    assert ts.tzinfo == timezone.utc
    assert bikes == 18
    assert stands == 22
    # Tuple arity matches the INSERT placeholders
    assert INSERT_SQL.count("%s") == len(rows[0])


def test_insert_sql_skips_duplicates():
    assert "ON CONFLICT DO NOTHING" in INSERT_SQL


def test_non_200_feed_exits_nonzero(monkeypatch):
    class FakeResponse:
        status_code = 503

    monkeypatch.setattr(
        "scripts.ingest_snapshot.requests.get", lambda *a, **k: FakeResponse()
    )
    monkeypatch.setenv("JCDECAUX_API_KEY", "dummy")
    with pytest.raises(SystemExit) as exc:
        main()
    assert "503" in str(exc.value)
