# Data audit — historical dublinbikes dataset (Phase 3)

Audited 2026-07-09 with `scripts/audit_historical.py`. Verdict: PASS on
every threshold in `docs/phase-3.md`.

## Source

Dataset: "Dublinbikes API DCC" — monthly historical station-status
files published by Smart Dublin, listed on
https://data.gov.ie/dataset/dublinbikes-api and hosted on
data.smartdublin.ie.

Files downloaded to `data/raw/` (77 MB each — excluded from git via
`.gitignore`; re-download with these URLs):

- https://data.smartdublin.ie/dataset/33ec9fe2-4957-4e9a-ab55-c5e917c7a9ab/resource/33bbe7a6-3b30-49cf-a13d-0ef622dbedb1/download/dublin-bikes_station_status_032026.csv
- https://data.smartdublin.ie/dataset/33ec9fe2-4957-4e9a-ab55-c5e917c7a9ab/resource/92857912-1a36-4c8e-bd85-d26177609dbf/download/dublin-bikes_station_status_042026.csv
- https://data.smartdublin.ie/dataset/33ec9fe2-4957-4e9a-ab55-c5e917c7a9ab/resource/03dd67ef-33b0-4102-8329-42c67fdbf53e/download/dublin-bikes_station_status_052026.csv

URL pattern for other months:
`https://data.smartdublin.ie/dataset/33ec9fe2-4957-4e9a-ab55-c5e917c7a9ab/resource/<resource-id>/download/dublin-bikes_station_status_MMYYYY.csv`
(resource ids listed on the dataset page).

## Observed schema (GBFS-style)

Columns: `system_id, last_reported, station_id, num_bikes_available,
num_docks_available, is_installed, is_renting, is_returning, name,
short_name, address, lat, lon, region_id, capacity`

- `last_reported`: `YYYY-MM-DD HH:MM:SS` strings, 5–10 min cadence.
- `name`: uppercase, exactly matching the live JCDecaux feed's `name`
  (e.g. `MOUNT STREET LOWER`) — assumption A4 confirmed.
- `num_bikes_available`: integer, combined mechanical+electric total
  (same definition as the live feed's `available_bikes`).

## Audit output (observed 2026-07-09)

```
files: 3
total rows: 1880190
columns: ['last_reported', 'station_id', 'num_bikes_available', 'name', 'capacity']
distinct stations: 115

station: MOUNT STREET LOWER
rows: 16874
min timestamp: 2026-03-01 00:10:00
max timestamp: 2026-05-31 23:55:00
span days: 91
median interval minutes: 10.0
max gap hours: 1.2
bikes min: 0  max: 40
capacity values seen: [40]
std of bikes over most recent full week (2026-05-24..2026-05-31): 9.46  (rows: 1310)
```

## Thresholds (fixed in docs/phase-3.md at planning time) vs observed

| Threshold | Required | Observed | Verdict |
|---|---|---|---|
| Consecutive days | ≥ 60 | 91 (max gap 1.2 h) | PASS |
| Median interval | ≤ 60 min | 10.0 min | PASS |
| Availability range | integers in [0, 45] | 0–40 | PASS |
| σ, most recent full week | > 2.0 bikes | 9.46 | PASS |
| Station identity vs live feed | same name or documented mapping | exact name match, capacity 40 both sources | PASS |
