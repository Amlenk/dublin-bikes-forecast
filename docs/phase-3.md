# Phase 3 — Historical-data audit

**Status:** PROVISIONAL — revise after the previous phase closes (see
re-planning checklist in docs/handover.md)

**Prerequisite:** Phase 2 closed with its anchor result pasted in
`docs/handover.md`.

## Cold-start context

- **Project:** Dublin Bikes Forecast — a job-portfolio ML service.
  One-liner: a job-seeking ML-engineer candidate uses a live, publicly
  deployed Dublin Bikes availability-forecasting service to give
  recruiters clickable evidence of production ML skills. Core Value
  Transaction (CVT): a recruiter opens the public URL on their phone and
  sees, for one named Dublin Bikes station, the current available-bikes
  count fetched live and the model's predicted count one hour ahead, with
  a data timestamp under 15 minutes old. This phase secures the TRAINING
  DATA for the real model (Phase 4); the deployed skeleton (Phase 2)
  currently serves a persistence placeholder.
- **Stack & versions:** Python 3.12 (≥3.11), pandas ≥2.2 (first phase
  that installs it). No model code, no app changes.
- **Repo layout (relevant paths):** Repo root =
  `dublin-bikes-forecast/`. This phase creates: `data/raw/` (the
  downloaded file(s); if any file exceeds ~50 MB, keep it out of git —
  add `data/raw/` to `.gitignore` and record the download URL in
  `data/DATA_AUDIT.md` instead), `scripts/audit_historical.py`, and
  `data/DATA_AUDIT.md` (observed schema: column names, dtypes, time
  range, interval, row counts — written from actual output).
- **Run commands:**
  - `.venv\Scripts\activate` then `pip install pandas`
  - `python scripts/audit_historical.py data\raw\<downloaded-file>`
- **Prerequisites (accounts, credentials, sample data, installs):**
  - No accounts needed. Source: https://data.gov.ie — search
    `dublinbikes`; Smart Dublin's historical station-availability
    archives (typically quarterly CSV/JSON). Also acceptable:
    https://data.smartdublin.ie equivalents.
  - The chosen station name: read it from `docs/handover.md` (Phase 1).

## Goal

Obtain a historical dublinbikes dataset that verifiably covers the chosen
station at model-trainable granularity and duration.

## Scope

**IN:**
- Locating and downloading the most recent historical
  station-availability dataset(s) from data.gov.ie / Smart Dublin.
- `scripts/audit_historical.py`: loads the file(s) and prints — total
  rows; column names; for the chosen station: row count, min/max
  timestamp, median interval between consecutive timestamps, availability
  min/max, and standard deviation of availability over the most recent
  full week.
- `data/DATA_AUDIT.md` recording the printed facts and the exact download
  URL(s).

**OUT (do not build these in this phase, even if tempting):**
- No feature engineering, no model, no train/test split (Phase 4).
- No loading into Postgres (Phase 6 concerns live snapshots only;
  historical backfill is in the Parking Lot).
- No cleaning beyond what the audit script needs to parse the file.

## External success anchor

- **Ladder rung:** 1 — real external artifact (a dataset published by
  Smart Dublin / data.gov.ie), checked against thresholds fixed at
  planning time.
- **Why non-circular (one line):** The dataset's contents were produced
  by the bike scheme's telemetry years before this project, and the
  pass thresholds below were fixed in this file on 2026-07-08 — the audit
  script only reports, it cannot make a thin dataset thick.
- **Executable check:**
  1. Run `python scripts/audit_historical.py data\raw\<downloaded-file>`.
  2. Read the printed facts for the chosen station.
- **Expected observation:** For the chosen station: (a) ≥ 60 consecutive
  days between min and max timestamp; (b) median interval between
  consecutive records ≤ 60 minutes; (c) availability values are integers
  within [0, 45]; (d) standard deviation of availability over the most
  recent full week > 2.0 bikes; (e) the station is identified by the
  same name as the live feed OR a mapping line is written in
  `data/DATA_AUDIT.md` citing matching lat/lng.
- **Source of expected values:** Thresholds (a)–(d) fixed at planning
  time in this file (2026-07-08), derived from Phase 4's needs (60 days
  ≈ enough for weekly seasonality; σ > 2 per assumption A8 in
  `docs/01-decisions.md`); station name from `docs/handover.md`.

## Unit tests to write (regression guards)

Regression guards — these do NOT satisfy the exit gate by themselves:
- The audit's interval computation is correct on a 5-row hand-written
  fixture with known gaps (e.g. timestamps 10 min apart → median 10).
- Timestamp parsing handles the dataset's actual format (copy 3 real
  rows into a fixture once downloaded).

## Exit gate

The phase is done only when ALL of these hold:
1. The external anchor was **run** and the observed result matches the
   expected observation.
2. The observed audit output is **pasted into `docs/handover.md`** under
   Anchor Results.
3. The unit tests above exist and pass.
4. The close-out steps below are completed.

## Pre-mortem (likely failure modes)

1. If no dataset on data.gov.ie meets the thresholds → probably looking
   at aggregated/summary files instead of raw snapshots → check Smart
   Dublin's own portal and the dataset's resource list (many datasets
   hide quarterly files as separate resources). If genuinely absent:
   assumption A2 in `docs/01-decisions.md` is TRIGGERED — the fallback is
   to collect live snapshots via Phase 6's pipeline first (re-order
   phases per the re-planning checklist).
2. If the chosen station is missing from the file → assumption A4
   TRIGGERED → pick the highest-capacity station present in BOTH the
   live feed and the file, record the change in `docs/handover.md`, and
   update the station name used by the deployed app.
3. If timestamps parse as strings/epoch inconsistently → probably mixed
   formats across quarterly files → audit one file at a time and record
   each file's format in `data/DATA_AUDIT.md`.
4. If σ over the last week ≤ 2.0 → assumption A8 TRIGGERED → choose a
   busier station (same procedure as pre-mortem 2).

## Iteration & deferral notes

— (empty at planning time)

## Close-out (mandatory — the phase is not done until every step is done)

1. Run the external anchor; paste the observed audit output into
   `docs/handover.md` → Anchor Results, with the date.
2. Update `docs/handover.md`: Current State; "The ONE next task" → Phase 4.
3. Run the post-phase re-planning checklist in `docs/handover.md`; any
   YES → amend downstream `docs/phase-*.md` files NOW (Phase 4's
   baseline-week instructions depend on this dataset's actual date range).
4. Copy deferrals into the Parking Lot.
5. Update assumption statuses (A2, A4, A8) in `docs/01-decisions.md`.
6. Stop. The user accepts the phase manually before the next one starts.
