from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

import app.main
from app.live import LiveFeedError, Snapshot

client = TestClient(app.main.app)

FAKE_SNAP = Snapshot(
    station="MOUNT STREET LOWER",
    bikes=18,
    stands=22,
    capacity=40,
    updated=datetime.now(timezone.utc) - timedelta(minutes=3),
)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_index_renders_station(monkeypatch):
    monkeypatch.setattr(app.main, "get_snapshot", lambda: FAKE_SNAP)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "MOUNT STREET LOWER" in resp.text
    assert "baseline v0 (persistence)" in resp.text
    assert "18" in resp.text
    assert "min ago" in resp.text


def test_index_feed_failure_renders_error_state(monkeypatch):
    def boom():
        raise LiveFeedError("live feed returned HTTP 500")

    monkeypatch.setattr(app.main, "get_snapshot", boom)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "feed unavailable" in resp.text
    assert "Traceback" not in resp.text
