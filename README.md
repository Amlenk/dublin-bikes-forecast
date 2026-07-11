# Dublin Bikes Forecast

A live, end-to-end ML service: it shows the current bike availability at
a Dublin Bikes station and a trained model's one-hour-ahead forecast,
served from a Dockerized FastAPI app with a fully unattended data
pipeline filling a cloud Postgres database behind it.

**Live demo:** https://dublin-bikes-forecast.onrender.com
(free tier — first load may take ~30–60 s if the service is waking)

## Measured results

Every number below comes from committed script output or an external
system's own records — sources linked. The evaluation discipline:
the baseline MAE and a golden prediction value were **committed to git
before** the model/serving code that had to beat/match them existed
(`model/EVAL.md`, `tests/fixtures/`).

| What | Result | Evidence |
|---|---|---|
| Forecast error (MAE, bikes) | **1.6150** vs persistence baseline 2.0843 — **−22.5%** | `model/EVAL.md`, 2,016-row held-out fortnight (2026-05-18..31) |
| Train/serve parity | Deployed `POST /predict` reproduced the pre-committed golden value **17.9037 exactly** | `docs/handover.md` Anchor Results, Phase 5 |
| Unattended ingestion | **30/30 scheduled runs succeeded** over a 12-hour hands-off window; all 24 half-hour trigger slots hit | GitHub Actions run history; `docs/handover.md` Anchor Results, Phase 6 |
| Training data | 1.88M rows, 115 stations, Mar–May 2026 (Smart Dublin GBFS archives) | `data/DATA_AUDIT.md` |
| Tests | 20 passing (`pytest`) | `tests/` |

## Architecture

```
JCDecaux live API ──► FastAPI app (Docker, Render) ──► live count + 1-hour forecast
                          ▲ auto-deploy on push to main
                          │ model v1: HistGradientBoostingRegressor
                          │ (sklearn 1.9.0, 9 features, lags via
                          │  train-time climatology)
                          │
cron-job.org (every 30 min) ──► GitHub Actions `ingest` workflow
                                      │ snapshots all 114 stations
                                      ▼
                               Neon Postgres (`snapshots` table,
                               idempotent ON CONFLICT inserts)
```

An engineering detail worth a look: GitHub's own cron proved unreliable
for this repo (~2 h median gaps at two different schedules), so the
trigger was moved to an external pinger hitting the `workflow_dispatch`
API — the failure analysis and decision trail are in
`docs/01-decisions.md` (D7) and `docs/handover.md`.

## How it was built

The project was built phase-by-phase against pre-declared, externally
verifiable success criteria ("anchors") — each phase closed only when
an outside system (the deployed URL on mobile data, GitHub's Actions
UI, Neon's SQL console) confirmed the expected result. The full plan,
every anchor's observed output (including two failed attempts), and
all decision changes live in `docs/`; `docs/handover.md` is the
chronological record.

## Stack

Python 3.12 · FastAPI · scikit-learn 1.9.0 · pandas · Docker ·
Render (hosting, auto-deploy) · GitHub Actions · Neon Postgres ·
psycopg 3 · pytest

## Run locally

```
pip install -r requirements.txt
uvicorn app.main:app --reload      # needs JCDECAUX_API_KEY in .env
pytest                             # 20 tests, no network/DB required
```

## Data sources

- Live: [JCDecaux Open Data API](https://developer.jcdecaux.com)
  (contract `dublin`)
- Historical: [Smart Dublin](https://data.smartdublin.ie) dublinbikes
  GBFS-style monthly archives (Mar–May 2026; download URLs in
  `data/DATA_AUDIT.md` — raw CSVs are gitignored)
