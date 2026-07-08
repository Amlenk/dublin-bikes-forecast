# 00 — Essential Path

## Project

**One-liner:** A job-seeking ML-engineer candidate (Aman) uses a live,
publicly deployed Dublin Bikes availability-forecasting service to give
recruiters clickable, verifiable evidence of production ML skills (deployed
model, real external data, automated pipeline).

**Core Value Transaction (CVT):** A recruiter opens the public URL on their
phone and sees, for one named Dublin Bikes station, the current
available-bikes count fetched live from the real feed AND the model's
predicted count one hour ahead, with a data timestamp under 15 minutes old.

## The essential path (spine)

1. Live Dublin Bikes station feed (EXTERNAL — JCDecaux Open Data API,
   contract `dublin`; fallback: Smart Dublin real-time API) returns the
   current `available_bikes` for the chosen station.
2. Historical Dublin Bikes dataset (EXTERNAL — data.gov.ie / Smart Dublin
   published archives) provides the training series for that station.
3. A trained forecasting model artifact (scikit-learn, committed to the
   repo) maps recent availability + calendar features → predicted
   availability at t+60 minutes.
4. A FastAPI service fetches the live snapshot, builds features, runs the
   model, and renders one HTML page: station name, live actual, +60 min
   forecast, data timestamp.
5. The service runs Dockerized on a free public host (EXTERNAL — Hugging
   Face Spaces free CPU tier), reachable at a public URL from any phone.

## Spine vs. flesh

| Component | Verdict | Delete Test result (one line) |
|---|---|---|
| Live feed fetch | SPINE | No live feed → no current count on the page → CVT fails. |
| Historical dataset + trained model | SPINE | No trained model → no credible forecast; "job-worthy ML" is the product's value (a permanent naive placeholder fails the one-liner). |
| Public deployment (HF Space) | SPINE | CVT says "recruiter opens the public URL on their phone" — localhost completes nothing. |
| Dockerfile / packaging | SPINE | HF Spaces Docker SDK requires a Dockerfile to serve FastAPI; without it the app cannot be hosted there (platform-demanded packaging). |
| Scheduled ingestion → Postgres | FLESH (demanded breadth) | Forecast from the live snapshot + calendar features completes the CVT without stored history; kept as Phase 6 because the user's goal (ML-engineer resume evidence) explicitly demands an unattended data pipeline. |
| Automated retraining | FLESH | Model trained once completes the CVT → Parking Lot. |
| Multi-station support / map UI | FLESH | CVT names ONE station → Parking Lot. |
| Charts / history sparklines | FLESH | Two numbers + timestamp complete the CVT → Parking Lot. |
| Uncertainty intervals | FLESH | A point forecast completes the CVT → Parking Lot. |
| CI (pytest on push, badge) | FLESH | CVT completes with untested pushes → Parking Lot (resume keyword, build later). |
| Monitoring / alerting | FLESH | CVT completes unmonitored → Parking Lot. |
| Auth | FLESH | Public read-only demo; no user data → Parking Lot (not needed at all). |

## Rejected framings

1. **Framing:** "Collect live data with a scheduled pipeline for 3–4 weeks
   first, then train on the collected data, then deploy." —
   **REJECTED: WRONG-RISK.** It delays killing the two hard risks (does a
   free live feed exist? does the free host actually serve this?) by weeks
   of calendar time, and blocks all progress on data accumulation the
   historical archives make unnecessary.
2. **Framing:** "Train and evaluate the model in a notebook on the
   historical CSVs; deployment comes later if there's time." —
   **REJECTED: NOT-END-TO-END.** It stops before the observable output (a
   public URL). The resume already has notebook-grade projects; the entire
   differentiating value of this project is the live deployed system.
3. **Framing:** "Build the full product: all ~115 stations, map UI, history
   charts, uncertainty bands, deployed at the end." —
   **REJECTED: TOO-FAT.** Every added station/chart is flesh by the Delete
   Test; bundling it into the spine multiplies surface area before any risk
   is retired.

## Candidate assumptions and scoring

| # | Assumption (short) | Category | P | D | P×D |
|---|---|---|---|---|---|
| 1 | A free, live, station-level Dublin Bikes feed is obtainable today (JCDecaux `dublin` contract or Smart Dublin API) | External-system reality | 3 (no direct recent evidence; the operator/feed has migrated over the years) | 3 (no live feed → essential path invalid; pivot to another dataset) | **9** |
| 2 | Historical station-level availability data (≥60 days, ≤60-min granularity) is downloadable from data.gov.ie / Smart Dublin | Data reality | 2 (documented datasets exist but coverage/granularity unverified) | 2 (model phases rework: bootstrap by collecting live data for weeks) | 4 |
| 3 | Hugging Face Spaces free CPU tier serves a Dockerized FastAPI app + sklearn model publicly, no credit card | Environment | 2 (documented, but free-tier conditions unverified for this workload) | 2 (deploy phase rework on another host) | 4 |
| 4 | Live-feed station IDs/names join to the historical dataset's stations | Integration | 2 (two different publishers; naming drift plausible) | 2 (feature/serving rework via manual mapping) | 4 |
| 5 | A tabular sklearn model beats naive persistence at t+60 on held-out data | Technical feasibility | 2 (bike demand is autocorrelated; not verified for this horizon) | 1 (worst case: ship the honest baseline + calendar model and say so) | 2 |
| 6 | GitHub Actions cron on a free public repo runs a 30-min ingestion schedule reliably enough | Integration | 2 (known scheduling delays on free runners) | 1 (ingestion is flesh; delays tolerable) | 2 |

**Winner:** #1 (max P×D = 9; no tie-break needed).

## The reality-check thesis (kill this first)

> A station-level live Dublin Bikes availability feed is freely accessible
> today: a GET request to
> `https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=<key>`
> (key obtained free at developer.jcdecaux.com) returns HTTP 200 with a
> JSON array of ≥ 90 stations, each containing a station `name` and a
> numeric `available_bikes` field, and the `available_bikes` value for one
> chosen station matches the count shown on the official dublinbikes
> map/app for that same station within ±2 bikes at the same minute.
> Fallback counting as PASS: the same field-level checks succeed against
> Smart Dublin's real-time dublinbikes API (found via data.smartdublin.ie).
> If both fail, the thesis is FALSE.

**Tested by:** Phase 1 (see `docs/phase-1.md`).
