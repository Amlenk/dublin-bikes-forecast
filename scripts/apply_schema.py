"""One-off: apply db/schema.sql to the DATABASE_URL database."""
import os
import sys
from pathlib import Path

import psycopg

REPO = Path(__file__).resolve().parents[1]


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


with psycopg.connect(env("DATABASE_URL")) as conn:
    conn.execute((REPO / "db" / "schema.sql").read_text())
print("schema applied")
