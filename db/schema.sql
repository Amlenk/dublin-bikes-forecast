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

-- Historical backfill of the Smart Dublin monthly GBFS archives
-- (data/raw/*.csv), loaded once by scripts/backfill_history.py.
-- Kept SEPARATE from snapshots: history.station_id is the Smart
-- Dublin id space, NOT the JCDecaux ids in snapshots.station_id.
-- Join the two sources on station_name (exact match verified in
-- Phase 3). ts is the CSV's naive last_reported stored as UTC —
-- the same convention model/train.py used for these files.
CREATE TABLE IF NOT EXISTS history (
    station_id       INT         NOT NULL,  -- Smart Dublin id space
    station_name     TEXT        NOT NULL,
    ts               TIMESTAMPTZ NOT NULL,
    available_bikes  INT         NOT NULL,
    available_stands INT         NOT NULL,  -- num_docks_available
    capacity         INT         NOT NULL,
    PRIMARY KEY (station_id, ts)
);
