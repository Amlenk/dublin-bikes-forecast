# Phase 5 — Serve the trained model

**Status:** PROVISIONAL — revise after the previous phase closes (see
re-planning checklist in docs/handover.md)

**Prerequisite:** Phase 4 closed with its anchor result pasted in
`docs/handover.md` (`model/artifacts/model_v1.joblib` exists and beat the
recorded baseline).

## Cold-start context

- **Project:** Dublin Bikes Forecast — a job-portfolio ML service.
  One-liner: a job-seeking ML-engineer candidate uses a live, publicly
  deployed Dublin Bikes availability-forecasting service to give
  recruiters clickable evidence of production ML skills. Core Value
  Transaction (CVT): a recruiter opens the public URL on their phone and
  sees, for one named Dublin Bikes station, the current available-bikes
  count fetched live and the model's predicted count one hour ahead, with
  a data timestamp under 15 minutes old. After this phase the deployed
  page serves the TRAINED model (replacing the Phase-2 persistence
  placeholder), completing the CVT in its final form.
- **Stack & versions:** Python 3.12 (≥3.11), FastAPI + Uvicorn (latest
  stable), scikit-learn ≥1.4, pandas ≥2.2, joblib. Docker on Render
  (free web service; Render builds remotely and auto-deploys on push to
  `main`). The service and its `JCDECAUX_API_KEY` environment variable
  already exist from Phase 2 (host changed from HF Spaces to Render
  2026-07-09 — see `docs/01-decisions.md` D3).
- **Repo layout (relevant paths):** Repo root =
  `dublin-bikes-forecast/`. This phase modifies `app/forecast.py` (load
  `model/artifacts/model_v1.joblib`, build serving features, predict)
  and `app/main.py`/`templates/index.html` (label `model v1`, add
  `POST /predict` parity endpoint accepting an explicit feature JSON and
  returning the prediction). Adds scikit-learn/pandas/joblib to
  `requirements.txt` and ensures the Dockerfile copies
  `model/artifacts/`.
- **Run commands:**
  - `.venv\Scripts\activate` then `pip install -r requirements.txt`
  - Local run: `uvicorn app.main:app --reload`
  - Tests: `pytest`
  - Deploy: `git push origin main` (Render auto-deploys), watch the
    service's Logs tab in the Render dashboard.
- **Prerequisites (accounts, credentials, sample data, installs):**
  - Render account + service from Phase 2; live public URL recorded in
    `docs/handover.md`.
  - The trained artifact `model/artifacts/model_v1.joblib` from Phase 4.
  - **Serving-features note:** the model's t−1h/t−24h/t−1wk lag inputs
    are not all observable from a single live snapshot. The serving
    feature builder must state its strategy in code comments and
    `model/EVAL.md`: acceptable v1 strategy = compute lags from the
    historical dataset's same hour-of-week climatology (a lookup table
    exported at train time into the artifact directory). If Phase 4
    ended with a different feature set, follow what `model/EVAL.md`
    actually records.

## Goal

Make the deployed public page serve one-hour forecasts from the Phase-4
trained model, verified by input/output parity with the offline artifact.

## Scope

**IN:**
- **Step 1 — record the golden pair BEFORE changing app code:** pick one
  input feature vector (a realistic snapshot: current availability,
  hour, day-of-week, and lag values per the serving strategy), run the
  Phase-4 artifact on it OFFLINE
  (`python -c "…joblib.load…predict…"` — a ~5-line snippet), and write
  the exact input JSON and the predicted value (4 decimal places) into
  `docs/handover.md` and this file's Iteration & deferral notes.
- `app/forecast.py`: load the artifact once at startup; build serving
  features; return the prediction clamped to [0, station capacity].
- `POST /predict`: accepts the explicit feature JSON (same schema as the
  golden pair) and returns `{"prediction": <float>}` — bypasses the live
  fetch so parity is exact.
- Page label changes from `baseline v0 (persistence)` to
  `model v1 (trained <train date>)`.
- Redeploy to the existing Render service (push to `main`).

**OUT (do not build these in this phase, even if tempting):**
- No retraining, no model changes (any MAE improvement idea → Parking
  Lot).
- No database reads (Phase 6 writes only; serving from stored history is
  Parking Lot).
- No UI beyond the label change and legibility.

## External success anchor

- **Ladder rung:** 3 — pre-committed golden input/output pair (offline
  prediction recorded before this phase's serving code exists), plus a
  rung-1 reachability element (the deployed public endpoint answers).
- **Why non-circular (one line):** The expected prediction value comes
  from the Phase-4 artifact executed offline BEFORE the serving code is
  written; if the serving feature path or model loading is wrong, the
  deployed number will not match it.
- **Executable check:**
  1. Confirm the golden pair (input JSON + expected prediction) is
     recorded in `docs/handover.md` dated before this phase's app-code
     commits.
  2. From any machine, run (PowerShell):
     `Invoke-RestMethod -Method Post -Uri https://<live-url>/predict -ContentType "application/json" -Body (Get-Content golden_input.json -Raw)`
     where `golden_input.json` holds the recorded input.
  3. Open `https://<live-url>` on a phone and read the model label.
- **Expected observation:** (a) the returned `prediction` equals the
  recorded offline value to 4 decimal places; (b) the page shows the
  label `model v1 (trained <date>)` and a forecast integer within
  [0, station capacity]; (c) the page's feed timestamp is < 15 minutes
  old.
- **Source of expected values:** Golden prediction from the Phase-4
  artifact run offline in Step 1 (predates serving code); label string
  and freshness threshold fixed here at planning time (2026-07-08).

## Unit tests to write (regression guards)

Regression guards — these do NOT satisfy the exit gate by themselves:
- `POST /predict` with the golden input returns the golden output (this
  duplicates the anchor locally — kept as a permanent regression guard).
- Serving feature builder produces the documented schema (names, order,
  dtypes) the artifact expects.
- Prediction clamping: a mocked model returning −3.2 yields 0; returning
  99 yields station capacity.
- App starts and `/health` returns 200 when the artifact file is present;
  startup fails loudly (clear error) when it is absent.

## Exit gate

The phase is done only when ALL of these hold:
1. The external anchor was **run** and the observed result matches the
   expected observation.
2. The observed parity response and page state are **pasted into
   `docs/handover.md`** under Anchor Results.
3. The unit tests above exist and pass.
4. The close-out steps below are completed.

## Pre-mortem (likely failure modes)

1. If the parity value differs → probably feature order/schema drift
   between `model/features.py` and the serving builder → print both
   feature vectors side by side first; do NOT retrain to make it match.
2. If the Render build fails after adding scikit-learn → probably image
   bloat or a missing system lib in `python:3.12-slim` → check the build
   log; pin package versions to those in the local venv
   (`pip freeze`).
3. If predictions are wildly off on the live page but parity passes →
   probably the climatology lag lookup is misaligned (hour-of-week
   indexing) → log the served feature vector and compare with a
   hand-computed one for the current time.
4. If the artifact fails to load on the deployed service → probably a
   scikit-learn version mismatch between training and serving → pin the
   exact same version in `requirements.txt` as recorded in
   `model/EVAL.md`.

## Iteration & deferral notes

— (empty at planning time)

## Close-out (mandatory — the phase is not done until every step is done)

1. Run the external anchor; paste the observed parity response and page
   description into `docs/handover.md` → Anchor Results, with the date.
2. Update `docs/handover.md`: Current State ("walking skeleton complete
   with real model"); "The ONE next task" → Phase 6.
3. Run the post-phase re-planning checklist in `docs/handover.md`; any
   YES → amend `docs/phase-6.md` NOW.
4. Copy deferrals into the Parking Lot.
5. Update assumption/decision statuses in `docs/01-decisions.md` (D4's
   reopen condition fires at this close — note it: multi-station is now
   eligible for the Parking Lot promotion discussion with the user).
6. Stop. The user accepts the phase manually before the next one starts.
