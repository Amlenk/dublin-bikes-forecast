"""Fetch one live snapshot of ALL Dublin Bikes stations and append it
to the `snapshots` table (Neon Postgres — see db/schema.sql).

Runs unattended on a GitHub Actions schedule
(.github/workflows/ingest.yml). Exits non-zero on any failure so the
workflow run shows red instead of silently green. Duplicate feed
timestamps are skipped via ON CONFLICT DO NOTHING (the feed refreshes
per-station at its own pace; re-inserts are expected).
"""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg
import requests

API_URL = "https://api.jcdecaux.com/vls/v1/stations"
CONTRACT = "dublin"
REPO = Path(__file__).resolve().parents[1]

INSERT_SQL = (
    "INSERT INTO snapshots"
    " (station_id, station_name, ts, available_bikes, available_stands)"
    " VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"
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


def parse_rows(payload: list) -> list:
    return [
        (
            int(s["number"]),
            s["name"],
            datetime.fromtimestamp(s["last_update"] / 1000, tz=timezone.utc),
            int(s["available_bikes"]),
            int(s["available_bike_stands"]),
        )
        for s in payload
    ]


def main() -> None:
    resp = requests.get(
        API_URL,
        params={"contract": CONTRACT, "apiKey": env("JCDECAUX_API_KEY")},
        timeout=30,
    )
    if resp.status_code != 200:
        sys.exit(f"feed returned HTTP {resp.status_code}")
    rows = parse_rows(resp.json())
    if not rows:
        sys.exit("feed returned zero stations")
    with psycopg.connect(env("DATABASE_URL")) as conn, conn.cursor() as cur:
        cur.executemany(INSERT_SQL, rows)
        inserted = cur.rowcount
    print(f"fetched {len(rows)} stations; inserted {inserted} new rows")


if __name__ == "__main__":
    main()
