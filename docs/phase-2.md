# Phase 2 — Deployed walking skeleton

**Status:** PROVISIONAL — revise after the previous phase closes (see
re-planning checklist in docs/handover.md)

**Prerequisite:** Phase 1 closed with its anchor result pasted in
`docs/handover.md` (which names the chosen station and the winning live
endpoint).

## Cold-start context

- **Project:** Dublin Bikes Forecast — a job-portfolio ML service.
  One-liner: a job-seeking ML-engineer candidate uses a live, publicly
  deployed Dublin Bikes availability-forecasting service to give
  recruiters clickable evidence of production ML skills. Core Value
  Transaction (CVT): a recruiter opens the public URL on their phone and
  sees, for one named Dublin Bikes station, the current available-bikes
  count fetched live and the model's predicted count one hour ahead, with
  a data timestamp under 15 minutes old. This phase completes that
  transaction end-to-end with a PLACEHOLDER forecast (persistence — see
  Goal); the trained model replaces it in Phases 4–5.
- **Stack & versions:** Python 3.12 (≥3.11), FastAPI + Uvicorn (latest
  stable), `requests`, `jinja2` (for the single HTML page). Packaged with
  a Dockerfile (base image `python:3.12-slim`); Hugging Face Spaces
  builds the image remotely — no local Docker needed. Host: Hugging Face
  Space, Docker SDK, free CPU tier (see `docs/01-decisions.md` D3).
- **Repo layout (relevant paths):** Repo root =
  `dublin-bikes-forecast/`. This phase creates: `app/main.py` (FastAPI
  app + page route), `app/live.py` (live-feed fetch), `app/forecast.py`
  (placeholder forecast), `templates/index.html`, `requirements.txt`,
  `Dockerfile`, `README.md` (stub: project name + live URL),
  `.gitignore` (must include `.env`). Existing:
  `scripts/probe_live_feed.py` from Phase 1.
- **Run commands:**
  - `python -m venv .venv` then `.venv\Scripts\activate`
  - `pip install -r requirements.txt`
  - Local run: `uvicorn app.main:app --reload` → http://127.0.0.1:8000
  - Tests: `pytest`
  - Deploy: create the Space (steps in Scope IN), then
    `git push space main` (the Space is a git remote).
- **Prerequisites (accounts, credentials, sample data, installs):**
  - The live-feed API key from Phase 1, in local `.env` as
    `JCDECAUX_API_KEY` — and added as a **Space secret** with the same
    name (Space → Settings → Variables and secrets). Never in git.
  - Free Hugging Face account (email signup, no card) at
    https://huggingface.co, plus a write access token (Settings →
    Access Tokens) to push.
  - Public GitHub repo `Amlenk/dublin-bikes-forecast` created and this
    folder pushed to it (GitHub is the primary remote; the Space is a
    second remote).
  - The chosen station name and winning endpoint: read them from
    `docs/handover.md` (recorded at Phase 1 close).

## Goal

Deploy a Dockerized FastAPI page on a free Hugging Face Space that shows
the chosen station's live availability alongside a labeled placeholder
one-hour forecast.

## Scope

**IN:**
- `app/live.py`: fetch the live snapshot for the chosen station from the
  Phase-1-winning endpoint; expose available bikes, capacity, and the
  feed's own last-update timestamp.
- `app/forecast.py`: placeholder forecast defined as **persistence** —
  predicted available bikes at t+60 minutes equals the current value —
  labeled on the page as `baseline v0 (persistence)`.
- `templates/index.html` + `app/main.py`: one page showing station name,
  current available bikes, forecast for +60 min, feed timestamp, and the
  model label. A `/health` route returning `{"status": "ok"}` (for the
  Space's own checks; NOT the anchor).
- `Dockerfile` per HF Spaces Docker SDK conventions (app must listen on
  port 7860).
- Creating the Space: huggingface.co → New Space → name
  `dublin-bikes-forecast`, SDK = Docker, hardware = CPU basic (free),
  visibility = Public. Add the Space as a git remote and push.
- Setting the API-key secret on the Space before the anchor run.

**OUT (do not build these in this phase, even if tempting):**
- No trained model, no historical data, no pandas/scikit-learn (Phases
  3–5).
- No database, no scheduled ingestion (Phase 6).
- No multi-station support, charts, styling beyond legible defaults, CI
  workflows, custom domain (Parking Lot in `docs/handover.md`).

## External success anchor

- **Ladder rung:** 1 — real external round-trip (public host serves the
  page; live count judged against the official dublinbikes map).
- **Why non-circular (one line):** The page's actual-count value is
  judged by the official dublinbikes map, and reachability/freshness are
  judged by the HF-hosted public URL on a phone — none of these expected
  values are produced by this phase's code.
- **Executable check:**
  1. On a phone NOT on the dev machine's network (use mobile data), open
     `https://<hf-username>-dublin-bikes-forecast.hf.space` (exact URL:
     Space page → "Embed this Space" shows the direct URL; record it in
     `docs/handover.md`).
  2. Read the displayed station name, current bikes, forecast, and
     timestamp; note the wall-clock time.
  3. Within the same minute, open the official dublinbikes live map
     (https://www.dublinbikes.ie or the app) and read the same station's
     count.
- **Expected observation:** (a) the page loads on mobile data in ≤ 120 s
  on first hit (cold start) and shows the station name recorded in
  `docs/handover.md`; (b) displayed current bikes equals the official
  map's count ±2; (c) displayed forecast is an integer between 0 and the
  station's capacity; (d) displayed feed timestamp is < 15 minutes old;
  (e) the label `baseline v0 (persistence)` is visible.
- **Source of expected values:** Freshness/±2/cold-start thresholds from
  `docs/00-essential-path.md` and `docs/01-decisions.md` D3 (planning
  time, 2026-07-08); the comparison count from the official dublinbikes
  map at check time; the station name from `docs/handover.md` (Phase 1).

## Unit tests to write (regression guards)

Regression guards — these do NOT satisfy the exit gate by themselves:
- Parsing a saved real API response (capture one JSON payload into
  `tests/fixtures/`) extracts the correct name, bikes, stands, timestamp.
- Persistence forecast returns exactly the current value and never a
  value < 0.
- The page route returns HTTP 200 and contains the station name when the
  live fetch is monkeypatched with the fixture.
- Live-fetch failure (timeout/non-200) renders an explicit "feed
  unavailable" state rather than a stack trace.

## Exit gate

The phase is done only when ALL of these hold:
1. The external anchor was **run** and the observed result matches the
   expected observation.
2. The observed result (what the phone actually showed, plus the map
   count) is **pasted into `docs/handover.md`** under Anchor Results.
3. The unit tests above exist and pass.
4. The close-out steps below are completed.

## Pre-mortem (likely failure modes)

1. If the Space build fails → probably the Dockerfile doesn't serve on
   port 7860 or `requirements.txt` is missing a package → check the
   Space's Build logs tab first.
2. If the page loads but shows "feed unavailable" → probably the
   `JCDECAUX_API_KEY` secret isn't set on the Space (local `.env` does
   not travel) → check Space Settings → Variables and secrets, then the
   Runtime logs.
3. If the page never loads on the phone → probably the Space is still
   building or sleeping → check the Space page shows status "Running";
   retry once after it does. If it runs but the URL 404s, re-copy the
   direct URL from "Embed this Space".
4. If the count mismatches the map by > 2 → probably comparing different
   stations (name collisions) or a stale cache in `app/live.py` → log
   the raw feed timestamp and station id; do not cache responses in this
   phase.

## Iteration & deferral notes

— (empty at planning time)

## Close-out (mandatory — the phase is not done until every step is done)

1. Run the external anchor above; paste the **observed** result into
   `docs/handover.md` → Anchor Results, with the date. Include the live
   public URL. A claim without the pasted observation does not count.
2. Update `docs/handover.md`: Current State, and set "The ONE next task"
   to the next phase (or a fix).
3. Run the **post-phase re-planning checklist** in `docs/handover.md`.
   Any YES → amend the affected downstream `docs/phase-*.md` files NOW.
4. Copy any deferrals from Iteration & deferral notes into
   `docs/handover.md` → Parking Lot.
5. Update assumption statuses in `docs/01-decisions.md` (A3 especially).
6. Stop. The user accepts the phase manually before the next one starts.
