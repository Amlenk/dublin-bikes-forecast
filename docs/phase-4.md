# Phase 4 — Trained model beats the persistence baseline

**Status:** CLOSED — anchor PASS 2026-07-09 (baseline 2.0843 reproduced
exactly; model 1.6150; see docs/handover.md → Anchor Results)

**Prerequisite:** Phase 3 closed with its anchor result pasted in
`docs/handover.md` (the audited dataset exists in `data/raw/` and
`data/DATA_AUDIT.md` records its schema and date range).

## Cold-start context

- **Project:** Dublin Bikes Forecast — a job-portfolio ML service.
  One-liner: a job-seeking ML-engineer candidate uses a live, publicly
  deployed Dublin Bikes availability-forecasting service to give
  recruiters clickable evidence of production ML skills. Core Value
  Transaction (CVT): a recruiter opens the public URL on their phone and
  sees, for one named Dublin Bikes station, the current available-bikes
  count fetched live and the model's predicted count one hour ahead, with
  a data timestamp under 15 minutes old. This phase produces the REAL
  model as a repo artifact; Phase 5 swaps it into the deployed service.
- **Stack & versions:** Python 3.12 (≥3.11), pandas ≥2.2, scikit-learn
  ≥1.4 (`HistGradientBoostingRegressor` first, per `docs/01-decisions.md`
  D2), joblib for the artifact. No app/deploy changes in this phase.
- **Repo layout (relevant paths):** Repo root =
  `dublin-bikes-forecast/`. This phase creates: `model/features.py`
  (feature builder), `model/train.py` (train + evaluate + save),
  `model/artifacts/model_v1.joblib`, `model/EVAL.md` (recorded baseline
  and model scores), `tests/test_features.py`. Reads
  `data/raw/<file>` per `data/DATA_AUDIT.md`.
- **Run commands:**
  - `.venv\Scripts\activate` then `pip install scikit-learn joblib`
  - Baseline (step 1 below): `python model/train.py --baseline-only`
  - Train + evaluate: `python model/train.py`
  - Tests: `pytest tests/test_features.py`
- **Prerequisites (accounts, credentials, sample data, installs):**
  - No accounts. Needs `data/raw/` dataset from Phase 3 (three monthly
    GBFS-style CSVs, Mar–May 2026; re-download URLs in
    `data/DATA_AUDIT.md`) and the chosen station name from
    `docs/handover.md`.
  - **Data-cadence note (from Phase 3's audit):** timestamps are
    irregular (median 10 min, some 5-min runs, gaps up to 1.2 h).
    Before feature building, resample the station's series to a regular
    10-minute grid with forward-fill limited to 3 steps (30 min);
    leave longer gaps as NaN and drop feature rows that touch them.
    The persistence baseline in Step 1 must be computed on this same
    resampled grid so model and baseline see identical rows.

## Goal

Train a forecasting model whose held-out one-hour-ahead mean absolute
error for the chosen station is lower than the persistence baseline's
error recorded before any model code was written.

## Scope

**IN:**
- **Step 1 — commit the yardstick BEFORE model code:** define the
  held-out window as the LAST 14 full days in the audited dataset
  (exact dates from `data/DATA_AUDIT.md`). Compute the persistence
  baseline (prediction for t+60 min = value at t) MAE over that window
  using a standalone ~15-line script or a spreadsheet — no model imports
  — and **write the number, the window dates, and the row count into
  `model/EVAL.md` and `docs/handover.md` NOW.** This number is the
  anchor's expected bound and must not be edited afterwards.
- `model/features.py`: lag features (t−1h, t−2h, t−24h, t−1wk
  availability), rolling mean (3h), calendar features (hour-of-day,
  day-of-week, weekend flag). Target: availability at t+60 min.
- `model/train.py`: chronological split (train = everything before the
  held-out window; NO shuffling), train
  `HistGradientBoostingRegressor`, report MAE on the held-out window,
  save `model/artifacts/model_v1.joblib`, and append results to
  `model/EVAL.md`. It must ALSO recompute the persistence MAE on the same
  window and print it — this must reproduce the Step-1 number (±0.01),
  proving the evaluation harness itself is sound.
- Up to two documented feature iterations if the first model loses to
  the baseline (log each in Iteration & deferral notes).

**OUT (do not build these in this phase, even if tempting):**
- No serving/deploy changes (Phase 5).
- No hyperparameter search frameworks, no experiment trackers, no
  deep-learning models (Parking Lot; D2 in `docs/01-decisions.md`).
- No multi-station training, no uncertainty intervals (Parking Lot).

## External success anchor

- **Ladder rung:** 2 — reference value fixed independently of the model
  code (persistence MAE, computed and recorded in Step 1 before any
  model code exists).
- **Why non-circular (one line):** The pass bound (baseline MAE) is
  derived from the raw Phase-3 dataset by a model-free calculation
  recorded in `model/EVAL.md` before `model/train.py` exists; the
  harness-reproduction check guards against a broken evaluator flattering
  the model.
- **Executable check:**
  1. Confirm `model/EVAL.md` contains the Step-1 baseline entry with a
     date earlier than the first commit of `model/train.py`
     (`git log --follow model/train.py` vs the EVAL.md entry).
  2. Run `python model/train.py`.
  3. Read the final printed lines: `baseline_mae=<x>` and
     `model_mae=<y>` for the held-out window.
- **Expected observation:** (a) `baseline_mae` matches the Step-1
  recorded number ±0.01; (b) `model_mae` < the Step-1 recorded
  `baseline_mae` (strictly); (c) `model/artifacts/model_v1.joblib`
  exists and `model/EVAL.md` records both numbers and the window dates.
- **Source of expected values:** The baseline MAE is computed in Step 1
  from the Phase-3 dataset before model code exists (the literal number
  cannot be written at planning time because the dataset arrives in
  Phase 3 — the phase file instead fixes the procedure and the
  commit-before-code rule); the strict-inequality criterion is fixed
  here at planning time (2026-07-08).

## Unit tests to write (regression guards)

Regression guards — these do NOT satisfy the exit gate by themselves:
- Feature builder on a 30-row hand-written fixture produces the expected
  lag values (hand-checked in the test file).
- No-leakage test: every feature row's inputs have timestamps strictly
  earlier than its target's timestamp.
- Chronological split test: max train timestamp < min held-out timestamp.
- Model artifact round-trip: saved joblib loads and predicts on one
  feature row without error, output within [−5, 50].

## Exit gate

The phase is done only when ALL of these hold:
1. The external anchor was **run** and the observed result matches the
   expected observation.
2. The observed output (both MAE lines) is **pasted into
   `docs/handover.md`** under Anchor Results.
3. The unit tests above exist and pass.
4. The close-out steps below are completed.

## Pre-mortem (likely failure modes)

1. If `model_mae` ≥ `baseline_mae` → persistence is genuinely strong at
   60 min → check the t−24h and t−1wk lags are actually populated (NaNs
   silently dropped can gut the training set) before adding features;
   two documented iterations max, then D2's reopen clause applies —
   record honestly and consult the user.
2. If `baseline_mae` from `train.py` doesn't reproduce the Step-1 number
   → probably a different row set (NaN handling or window boundary
   off-by-one) → diff the row counts against the Step-1 script first.
3. If MAE looks implausibly good (< 0.5 bikes) → probably target leakage
   (a feature at or after t+60) → run the no-leakage unit test and
   inspect feature timestamps.
4. If training data is far smaller than the audit's row count → probably
   the 1-week lag requires 7 days of warm-up rows dropped per gap →
   check gap handling in `model/features.py`.

## Iteration & deferral notes

- 2026-07-09: First model iteration beat the baseline (no feature
  iterations needed): HistGradientBoostingRegressor defaults,
  model_mae 1.6150 vs baseline 2.0843 (−22.5%). D2's reopen condition
  never fired.
- 2026-07-09: The feature-complete holdout row count (2016) equals the
  Step-1 baseline row count — no >30-min gaps or missing lags inside
  the holdout window, so the comparison needed no caveats.
- 2026-07-09: `bikes_now` (value at t) was included as a feature
  alongside the phase file's lag list — it is the persistence signal
  itself and its timestamp (t) is strictly earlier than the target
  (t+60), so the no-leakage rule holds.
- 2026-07-09: Artifact is a joblib dict:
  `{model, feature_columns, station, trained, sklearn_version}`
  (sklearn 1.9.0). `model/artifacts/climatology.csv` has columns
  `hour_of_week (0-167), mean_bikes`, computed from train rows only.

## Close-out (mandatory — the phase is not done until every step is done)

1. Run the external anchor; paste the observed MAE lines into
   `docs/handover.md` → Anchor Results, with the date.
2. Update `docs/handover.md`: Current State; "The ONE next task" → Phase 5.
3. Run the post-phase re-planning checklist in `docs/handover.md`; any
   YES → amend downstream `docs/phase-*.md` files NOW (Phase 5's parity
   check depends on this artifact's exact feature inputs).
4. Copy deferrals into the Parking Lot.
5. Update assumption statuses (A8; D2 reopen if triggered) in
   `docs/01-decisions.md`.
6. Stop. The user accepts the phase manually before the next one starts.
