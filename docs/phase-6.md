# Phase 6 — Unattended scheduled ingestion

**Status:** PROVISIONAL — revise after the previous phase closes (see
re-planning checklist in docs/handover.md)

**Prerequisite:** Phase 5 closed with its anchor result pasted in
`docs/handover.md`.

## Cold-start context

- **Project:** Dublin Bikes Forecast — a job-portfolio ML service.
  One-liner: a job-seeking ML-engineer candidate uses a live, publicly
  deployed Dublin Bikes availability-forecasting service to give
  recruiters clickable evidence of production ML skills. Core Value
  Transaction (CVT): a recruiter opens the public URL on their phone and
  sees, for one named Dublin Bikes station, the current available-bikes
  count fetched live and the model's predicted count one hour ahead, with
  a data timestamp under 15 minutes old. The CVT is already complete
  (Phases 1–5); this phase adds the unattended data pipeline the
  project's resume-evidence goal demands: scheduled cloud ingestion of
  live snapshots into a hosted database (future retraining fuel).
- **Stack & versions:** Python 3.12 (≥3.11), `requests`,
  `psycopg[binary]` ≥3.1. Scheduler: GitHub Actions cron in the public
  repo `Amlenk/dublin-bikes-forecast`. Database: Neon free-tier Postgres
  (https://neon.tech, email signup, no card — per
  `docs/01-decisions.md` D7/A6). No app/Space changes.
- **Repo layout (relevant paths):** Repo root =
  `dublin-bikes-forecast/`. This phase creates:
  `scripts/ingest_snapshot.py`, `.github/workflows/ingest.yml`,
  `db/schema.sql` (the `snapshots` table DDL, run once by hand in the
  Neon SQL console).
- **Run commands:**
  - Local one-off test: `.venv\Scripts\activate`,
    `pip install requests "psycopg[binary]"`, set `$env:DATABASE_URL`
    and `$env:JCDECAUX_API_KEY`, then
    `python scripts/ingest_snapshot.py`
  - Workflow: runs on GitHub's schedule; manual trigger via the Actions
    tab ("Run workflow") for testing.
- **Prerequisites (accounts, credentials, sample data, installs):**
  - Neon account + project + database (free tier). Get the connection
    string from the Neon dashboard.
  - GitHub repo secrets (repo → Settings → Secrets and variables →
    Actions): `DATABASE_URL` (Neon connection string, with
    `sslmode=require`) and `JCDECAUX_API_KEY` (from Phase 1).
  - `db/schema.sql` executed once in the Neon SQL Editor:
    `CREATE TABLE snapshots (station_id INT, station_name TEXT, ts TIMESTAMPTZ, available_bikes INT, available_stands INT, PRIMARY KEY (station_id, ts));`
    (If Phase 1's winning feed uses different fields, adapt and record
    in `docs/handover.md`.)

## Goal

Run an unattended 30-minute GitHub Actions schedule that appends live
station snapshots to a hosted Neon Postgres database.

## Scope

**IN:**
- `scripts/ingest_snapshot.py`: fetch the live feed once (all Dublin
  stations — one API call; per-row inserts for the chosen station AND
  the rest, since the marginal cost is nil and future multi-station work
  benefits), insert with `ON CONFLICT DO NOTHING` (feed timestamps
  repeat when the feed hasn't refreshed).
- `.github/workflows/ingest.yml`: `on: schedule: - cron: "*/30 * * * *"`
  plus `workflow_dispatch:` for manual runs; ubuntu-latest; installs
  deps; runs the script with the two secrets as env vars.
- One manual `workflow_dispatch` run to shake out secrets/connection
  before the unattended window.

**OUT (do not build these in this phase, even if tempting):**
- No retraining, no serving reads from Postgres (Parking Lot).
- No alerting on ingestion failure, no backfill of historical data into
  Postgres (Parking Lot).
- No infrastructure-as-code, no ORM, no migrations framework.

## External success anchor

- **Ladder rung:** 1 — real external round-trip: GitHub's scheduler and
  Neon's database, observed via their own dashboards/console with the
  dev machine off in between.
- **Why non-circular (one line):** Row counts and timestamps are read
  from the Neon SQL console and run outcomes from GitHub's Actions UI —
  both external systems' records, not this phase's script output; the
  unattended window makes local execution impossible.
- **Executable check:**
  1. After the manual `workflow_dispatch` run succeeds, note the time,
     shut down / disconnect the dev machine, and wait ≥ 12 hours.
  2. Open the repo's Actions tab: count scheduled `ingest` runs in the
     window and their statuses.
  3. In the Neon SQL Editor run:
     `SELECT count(*), min(ts), max(ts), count(DISTINCT ts) FROM snapshots WHERE station_id = <chosen station id> AND ts > now() - interval '12 hours';`
- **Expected observation:** (a) ≥ 18 scheduled workflow runs in the
  12-hour window with ≥ 90% concluding "Success" (24 nominal; GitHub
  cron delays tolerated per assumption A4/D7); (b) the SQL returns
  count ≥ 15 with `count(DISTINCT ts)` ≥ 15 and `max(ts) − min(ts)`
  ≥ 10 hours; (c) zero runs in the window were triggered manually
  (check the "Event" column shows `schedule`).
- **Source of expected values:** Thresholds fixed at planning time
  (2026-07-08) from D7's 30-minute cadence and GitHub's documented cron
  jitter; the observed counts come from GitHub's and Neon's own UIs.

## Unit tests to write (regression guards)

Regression guards — these do NOT satisfy the exit gate by themselves:
- Snapshot parser maps one saved real feed payload (fixture from
  Phase 2's `tests/fixtures/`) to the exact `snapshots` column tuple.
- Duplicate-timestamp insert is a no-op (exercised against a temporary
  SQLite table or a mocked cursor asserting `ON CONFLICT` SQL — do not
  require Neon in unit tests).
- The script exits non-zero when the feed returns non-200 (so the
  workflow run shows red instead of silently green).

## Exit gate

The phase is done only when ALL of these hold:
1. The external anchor was **run** (including the ≥ 12-hour unattended
   window) and the observed result matches the expected observation.
2. The observed Actions-tab summary and SQL output are **pasted into
   `docs/handover.md`** under Anchor Results.
3. The unit tests above exist and pass.
4. The close-out steps below are completed.

## Pre-mortem (likely failure modes)

1. If scheduled runs don't appear at all → probably the workflow file is
   on a non-default branch or the cron syntax is off → check it's merged
   to `main` and the Actions tab shows the workflow as enabled (GitHub
   also disables schedules on repos with 60 days of no activity).
2. If runs appear but fail on connection → probably a missing
   `sslmode=require` in `DATABASE_URL` or the secret name mismatch →
   open one failed run's log; the manual `workflow_dispatch` run exists
   to catch exactly this before the unattended window.
3. If rows exist but `count(DISTINCT ts)` is much lower than run count →
   the feed's `last_update` refreshes slower than 30 min for this
   station → this still PASSES if thresholds (b) hold; if it doesn't,
   record the observed feed cadence in `docs/handover.md` and adjust D7
   via its reopen clause rather than faking timestamps.
4. If far fewer than 18 runs occurred → GitHub cron jitter beyond
   tolerance → check the Actions tab's run timestamps for gaps; if
   median gap > 60 min, D7's reopen condition has fired — record and
   re-plan the scheduler.

## Iteration & deferral notes

— (empty at planning time)

## Close-out (mandatory — the phase is not done until every step is done)

1. Run the external anchor; paste the observed Actions summary + SQL
   output into `docs/handover.md` → Anchor Results, with the date.
2. Update `docs/handover.md`: Current State; "The ONE next task" →
   consult the user: the planned phases are complete — the Parking Lot
   (README/resume bullets, retraining, CI, multi-station) is the menu.
3. Run the post-phase re-planning checklist in `docs/handover.md`.
4. Copy deferrals into the Parking Lot.
5. Update assumption statuses (A4, A6) and D7 in `docs/01-decisions.md`.
6. Stop. The user accepts the phase manually before anything further.
