# Phase 1 — Live-feed probe

**Status:** CLOSED — anchor PASS 2026-07-09 (see docs/handover.md → Anchor Results)

**Prerequisite:** None (first phase).

## Cold-start context

- **Project:** Dublin Bikes Forecast — a job-portfolio ML service.
  One-liner: a job-seeking ML-engineer candidate uses a live, publicly
  deployed Dublin Bikes availability-forecasting service to give
  recruiters clickable evidence of production ML skills. Core Value
  Transaction (CVT): a recruiter opens the public URL on their phone and
  sees, for one named Dublin Bikes station, the current available-bikes
  count fetched live and the model's predicted count one hour ahead, with
  a data timestamp under 15 minutes old.
- **Stack & versions:** Python 3.12 (≥3.11 acceptable) with `requests`
  (latest stable). Nothing else — this phase is a probe, not the app.
  Full project stack (for context only, NOT built here): FastAPI +
  Uvicorn, scikit-learn ≥1.4, pandas ≥2.2, Docker on Hugging Face Spaces.
- **Repo layout (relevant paths):** Repo root is this folder
  (`dublin-bikes-forecast/`). This phase creates only
  `scripts/probe_live_feed.py` and updates `docs/handover.md`. No `app/`
  yet.
- **Run commands:**
  - `python -m venv .venv` then `.venv\Scripts\activate` (Windows
    PowerShell)
  - `pip install requests`
  - `python scripts/probe_live_feed.py`
- **Prerequisites (accounts, credentials, sample data, installs):**
  - A free JCDecaux developer API key: register at
    https://developer.jcdecaux.com (email signup, no card), create a key,
    store it in a local file `.env` at repo root as
    `JCDECAUX_API_KEY=<key>`. Never commit `.env` (add `.gitignore` with
    `.env` in it).
  - The official dublinbikes live map, viewable without an account —
    check https://www.dublinbikes.ie (or the dublinbikes mobile app) for
    the real-time count used in the anchor.

## Goal

Prove that a free live station-level Dublin Bikes feed exists by fetching
it once and cross-checking one station's count against the official
dublinbikes map.

## Scope

**IN:**
- One ≤40-line script `scripts/probe_live_feed.py` that GETs
  `https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=<key>`
  and prints: HTTP status, number of stations, and for each of the 5
  stations with the largest `bike_stands`: name, `available_bikes`,
  `available_bike_stands`, and `last_update` (converted to local time).
- Choosing THE project station (highest-capacity station that looks
  active) and recording its exact name in `docs/handover.md`.
- If the JCDecaux call fails: repeating the probe against Smart Dublin's
  real-time dublinbikes API (locate the endpoint via
  https://data.smartdublin.ie, search "dublinbikes"), same printed fields.

**OUT (do not build these in this phase, even if tempting):**
- No FastAPI app, no Dockerfile, no HF Space, no model, no database.
- No historical-data download (that is Phase 3).
- No polling loop or storage — one fetch is the phase.
- No GitHub repo creation yet (Phase 2 needs it; not required to probe).

## External success anchor

- **Ladder rung:** 1 — real external round-trip, cross-judged by a second
  external source (the official dublinbikes map).
- **Why non-circular (one line):** Both the API response and the map count
  are produced by external systems that existed before this project; the
  probe script only relays them.
- **Executable check:**
  1. Run `python scripts/probe_live_feed.py`.
  2. Note the printed `available_bikes` for the chosen station and the
     wall-clock time.
  3. Within the same minute, open the official dublinbikes live map
     (https://www.dublinbikes.ie or the app), find the same station, and
     read its available-bikes count.
- **Expected observation:** (a) HTTP status `200`; (b) station count
  ≥ 90; (c) the chosen station's printed `available_bikes` is an integer
  0–45 and matches the official map's count within ±2 bikes; (d) the
  printed `last_update` is less than 15 minutes before now.
- **Source of expected values:** Thresholds from
  `docs/00-essential-path.md` reality-check thesis (planning time,
  2026-07-08); the live comparison count from the official dublinbikes
  map at check time — external to any code here.

## Unit tests to write (regression guards)

Regression guards — these do NOT satisfy the exit gate by themselves:
- None required this phase (a one-shot probe script with no logic worth
  guarding). State this in handover if skipped.

## Exit gate

The phase is done only when ALL of these hold:
1. The external anchor was **run** and the observed result matches the
   expected observation.
2. The observed result (actual output, not a claim) is **pasted into
   `docs/handover.md`** under Anchor Results, including the chosen
   station's name.
3. The unit tests above exist and pass (or the "none required" note is
   recorded).
4. The close-out steps below are completed.

## Pre-mortem (likely failure modes)

1. If the API returns 403 → probably the key isn't activated or the query
   param is misspelled (`apiKey`, case-sensitive) → check the activation
   email and paste the full URL into a browser first.
2. If the API returns 404 or the contracts list has no `dublin` →
   JCDecaux no longer operates the feed → run the Smart Dublin fallback
   in Scope IN; if that also fails, STOP: the reality-check thesis is
   FALSE — record it in handover, mark assumption A1 TRIGGERED in
   `docs/01-decisions.md`, and re-plan per D1's reopen clause.
3. If counts differ by more than ±2 → probably a stale snapshot (check
   `last_update` age) or a same-named/similar station → compare the
   station's `position` lat/lng from the JSON with the map pin location.
4. If https://www.dublinbikes.ie shows no live map → use the dublinbikes
   mobile app as the second judge instead; the anchor is unchanged.

## Iteration & deferral notes

- 2026-07-09: `.env` was initially saved as `DublinBikes.env`; renamed to
  `.env` (the name every phase file and `.gitignore` expects).
- Local Python is 3.14.4 (not 3.12) — satisfies the "≥3.11" floor; no
  issues with `requests`.
- Unit tests skipped per this file's "none required" clause (one-shot
  probe, no logic worth guarding).

## Close-out (mandatory — the phase is not done until every step is done)

1. Run the external anchor above; paste the **observed** result (actual
   terminal output / actual map count described concretely) into
   `docs/handover.md` → Anchor Results, with the date. A claim ("it
   worked") without the pasted observation does not count.
2. Update `docs/handover.md`: Current State, and set "The ONE next task"
   to the next phase (or to a fix, if the anchor failed). Record the
   chosen station name and which endpoint (JCDecaux or Smart Dublin) won.
3. Run the **post-phase re-planning checklist** in `docs/handover.md`. If
   any answer is YES, amend the affected downstream `docs/phase-*.md`
   files NOW, before ending the session, and note what changed. (In
   particular: if the Smart Dublin fallback won, update the endpoint and
   field names in `docs/phase-2.md` and `docs/phase-6.md`.)
4. Copy anything from Iteration & deferral notes that defers work into
   `docs/handover.md` → Parking Lot.
5. If any assumption in `docs/01-decisions.md` was confirmed or
   contradicted by this phase (A1 especially), update its Status there.
6. Stop. The user accepts the phase manually before the next one starts.
