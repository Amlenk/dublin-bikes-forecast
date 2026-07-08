"""Phase 1 probe: fetch live Dublin Bikes station data from the JCDecaux API.

Prints HTTP status, station count, and the 5 largest stations' live numbers
so one station can be cross-checked against the official dublinbikes map.
"""
import sys
from datetime import datetime
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_key() -> str:
    env_file = REPO_ROOT / ".env"
    if not env_file.exists():
        sys.exit(f"missing {env_file}")
    for line in env_file.read_text().splitlines():
        if line.strip().startswith("JCDECAUX_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("JCDECAUX_API_KEY not found in .env")


def main() -> None:
    resp = requests.get(
        "https://api.jcdecaux.com/vls/v1/stations",
        params={"contract": "dublin", "apiKey": load_key()},
        timeout=30,
    )
    print(f"HTTP status: {resp.status_code}")
    if resp.status_code != 200:
        print(resp.text[:500])
        sys.exit(1)
    stations = resp.json()
    print(f"stations: {len(stations)}")
    print(f"local time now: {datetime.now():%Y-%m-%d %H:%M:%S}")
    for s in sorted(stations, key=lambda s: s["bike_stands"], reverse=True)[:5]:
        updated = datetime.fromtimestamp(s["last_update"] / 1000)
        print(
            f"{s['name']:<40} capacity={s['bike_stands']:>3} "
            f"bikes={s['available_bikes']:>3} stands={s['available_bike_stands']:>3} "
            f"last_update={updated:%Y-%m-%d %H:%M:%S}"
        )


if __name__ == "__main__":
    main()
