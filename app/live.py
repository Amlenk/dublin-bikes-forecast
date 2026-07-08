"""Fetch the live Dublin Bikes snapshot for the project station.

Feed: JCDecaux Open Data API, contract "dublin" (verified in Phase 1 —
see docs/handover.md). Reports the combined mechanical+electric total.
"""
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import requests

API_URL = "https://api.jcdecaux.com/vls/v1/stations"
CONTRACT = "dublin"
STATION_NAME = os.getenv("STATION_NAME", "MOUNT STREET LOWER")
REPO_ROOT = Path(__file__).resolve().parents[1]


class LiveFeedError(Exception):
    """Raised when the live feed is unreachable or malformed."""


def _api_key() -> str:
    key = os.getenv("JCDECAUX_API_KEY")
    if key:
        return key
    env_file = REPO_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.strip().startswith("JCDECAUX_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise LiveFeedError("JCDECAUX_API_KEY not set (Space secret or .env)")


@dataclass
class Snapshot:
    station: str
    bikes: int
    stands: int
    capacity: int
    updated: datetime


def parse_station(payload: list, station_name: str = STATION_NAME) -> Snapshot:
    for s in payload:
        if s.get("name") == station_name:
            return Snapshot(
                station=s["name"],
                bikes=int(s["available_bikes"]),
                stands=int(s["available_bike_stands"]),
                capacity=int(s["bike_stands"]),
                updated=datetime.fromtimestamp(s["last_update"] / 1000),
            )
    raise LiveFeedError(f"station {station_name!r} not in feed")


def get_snapshot() -> Snapshot:
    try:
        resp = requests.get(
            API_URL,
            params={"contract": CONTRACT, "apiKey": _api_key()},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise LiveFeedError(f"live feed request failed: {exc}") from exc
    if resp.status_code != 200:
        raise LiveFeedError(f"live feed returned HTTP {resp.status_code}")
    return parse_station(resp.json())
