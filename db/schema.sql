-- Phase 6: snapshot store for scheduled ingestion (Neon Postgres).
-- Applied once via scripts/apply_schema.py (or the Neon SQL Editor).
CREATE TABLE IF NOT EXISTS snapshots (
    station_id       INT         NOT NULL,
    station_name     TEXT        NOT NULL,
    ts               TIMESTAMPTZ NOT NULL,  -- feed's last_update (UTC)
    available_bikes  INT         NOT NULL,
    available_stands INT         NOT NULL,
    PRIMARY KEY (station_id, ts)
);
