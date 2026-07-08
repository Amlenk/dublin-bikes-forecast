# Handover — living state document

## Update protocol (do not edit this section; follow it)

**When to update:** at the end of every build session — whether or not the
phase finished — and immediately after running any phase's external anchor.

**What to update, in order:**
1. **Anchor Results** — paste the observed output of any anchor you ran
   (actual terminal output or a concrete description of what you saw),
   dated. Rule: **a phase is not "done" until its anchor has been RUN and
   the observed result is pasted here.** "All tests pass" or "verified
   working" without the pasted observation does not close a phase.
2. **Current State** — rewrite to reflect reality now (what exists, what is
   proven by which anchor, what is mid-flight).
3. **The ONE next task** — exactly one item. If the session ended
   mid-phase, the next task is "resume phase N at [specific point]".
4. **Parking Lot** — add anything deferred this session.
5. Run the **post-phase re-planning checklist** below if a phase closed.

## Current State

Phases 1 and 2 CLOSED (anchors PASS — see Anchor Results). **The
walking skeleton is live: https://dublin-bikes-forecast.onrender.com**
— a Dockerized FastAPI app on a Render free web service (region
Frankfurt), auto-deployed from the public GitHub repo
`Amlenk/dublin-bikes-forecast` on every push to `main`. It shows MOUNT
STREET LOWER's live availability (JCDecaux feed) + a persistence
placeholder forecast labeled `baseline v0 (persistence)`, with feed age
in minutes and Dublin wall-clock time. `JCDECAUX_API_KEY` is set as a
Render environment variable. 7 unit tests passing (`pytest`). Host was
changed HF Spaces → Render mid-Phase-2 (see Locked decisions &
assumptions note below). Not yet: historical data, trained model,
database, scheduled ingestion.

## The ONE next task

Execute `docs/phase-3.md` — obtain and audit a historical dublinbikes
dataset (data.gov.ie / Smart Dublin) covering MOUNT STREET LOWER at
≤ 60-min granularity for ≥ 60 days. Its anchor: audit script output
meets the thresholds fixed in the phase file.

## How to verify the previous phase actually works

Open https://dublin-bikes-forecast.onrender.com on a phone using mobile
data (allow up to ~60 s if the free service is waking). Expected: page
shows `MOUNT STREET LOWER`, a bikes-now integer 0–40 that matches the
official dublinbikes map ±2 at the same minute, a forecast integer
0–40, `Feed updated N min ago` with N < 15, and the label
`baseline v0 (persistence)`.

## Anchor Results (append-only log)

### 2026-07-09 — Phase 1 anchor

```
HTTP status: 200
stations: 114
local time now: 2026-07-09 00:00:56
MOUNT STREET LOWER      capacity= 40 bikes= 18 stands= 22 last_update=2026-07-08 23:55:37
```

Official dublinbikes map, read by the user in the same minute:
MOUNT STREET LOWER = 9 mechanical + 9 electric = **18 bikes**, "22P"
(22 stands). Difference vs API: 0 bikes (tolerance ±2), stands match
22 = 22. Feed timestamp ~5.3 min old (< 15 min threshold).

Verdict: PASS

Note for later phases: the official map splits mechanical vs electric
bikes; the JCDecaux v1 API reports only the combined total. The model
forecasts the combined total.

### 2026-07-09 — Phase 2 anchor

User observation on a phone over mobile data (Wi-Fi off), page
https://dublin-bikes-forecast.onrender.com, ~20:31 Dublin time:

```
Bikes available now: 20
Forecast in 60 min: 20
Free stands: 20
Feed updated 4 min ago (20:27 Dublin time)
Model: baseline v0 (persistence) · Station capacity: 40
Load time: "almost instantly"
```

Official dublinbikes map, same minutes: MOUNT STREET LOWER =
mechanical + electric = **20 bikes**. Difference vs page: 0 (tolerance
±2). All five expected observations met: (a) load ≪ 120 s on mobile
data; (b) count match exact; (c) forecast integer within [0, 40];
(d) feed age 4 min < 15; (e) baseline label visible.

Verdict: PASS

## Locked decisions & assumptions

All locked decisions and standing assumptions live in
`docs/01-decisions.md`. Do not relitigate them here; if one changed this
session (its reopen/revisit condition fired), note the change here with a
pointer:

- 2026-07-09 — **D3 reopened and changed: host is now Render, not
  Hugging Face Spaces.** HF's New Space UI offers Docker/Gradio Spaces
  only on paid plans (user observation, corroborated by
  huggingface.co/pricing). A3 TRIGGERED; A3b (Render free tier, no
  card) added. `docs/phase-2.md`, `docs/phase-5.md`,
  `docs/00-essential-path.md`, `Dockerfile` (PORT env var), and
  `README.md` amended accordingly. The unused `space` git remote was
  removed; the HF write token is no longer needed (user may revoke it).

## Parking Lot (deferred items & future ideas)

- Recruiter-facing README + resume bullets written ONLY from measured
  numbers (MAE vs baseline, live URL, pipeline run counts); add the live
  URL to `Z:\Claude\resume` and LinkedIn — why deferred: needs real
  metrics that exist only after Phase 6 — earliest: after Phase 6.
- Automated weekly retraining (GitHub Actions job retrains on ingested
  Postgres data, versions the artifact) — deferred: CVT completes with a
  once-trained model — earliest: after Phase 6.
- Serving reads recent lags from Postgres instead of climatology lookup —
  deferred: flesh for the CVT — earliest: after Phase 6.
- Historical backfill of `data/raw/` into Postgres — deferred: flesh —
  earliest: after Phase 6.
- Multi-station support + map UI — deferred: CVT names one station
  (decision D4) — earliest: after Phase 5 closes (D4 reopen).
- History charts / sparklines on the page — deferred: flesh — after
  skeleton.
- Uncertainty intervals (quantile models) — deferred: flesh — after
  Phase 6.
- CI: pytest on push + badge in README — deferred: flesh (resume
  keyword, cheap to add) — any time after Phase 2.
- Drift monitoring / ingestion-failure alerting — deferred: flesh —
  after Phase 6.
- Deep-learning model comparison (LSTM vs gradient boosting write-up) —
  deferred: D2 locks sklearn — only if D2 reopens.
- Custom domain for the demo — deferred: flesh — any time.
- Load testing / caching of live-feed calls — deferred: flesh — after
  Phase 6.
- Broader job-search asset work (ATS keyword pass over the three
  tailored resumes, LinkedIn kit refresh) — deferred: outside this
  project's build plan — user-scheduled.

## Post-phase re-planning checklist (run after EVERY phase close)

Answer each question in writing below the checklist. Any YES → amend the
affected downstream `docs/phase-*.md` files in the same session, and note
what changed.

1. Did this phase's outcome (anchor result, iteration notes) invalidate any
   assumption in `docs/01-decisions.md`? (If yes: update its Status there,
   then check which phases relied on it.)
2. Does the NEXT phase's anchor still make sense — do its expected values,
   prerequisites, and scope still match reality as just observed?
3. Did anything land differently than the next phase file assumes (paths,
   schema, API shapes, commands)? (If yes: fix the next phase file's
   Cold-start context now.)
4. Does any Parking Lot item now block the spine? (If yes: it was
   mis-tagged as flesh — promote it to a phase.)
5. Is there now a riskier open assumption than the one the next phase
   targets? (If yes: re-order or re-scope the next phase.)

### Re-planning answers log

### 2026-07-09 — after Phase 1

1. NO — no assumption invalidated; A1 CONFIRMED (status updated in
   `docs/01-decisions.md`).
2. YES (minor) — Phase 2's anchor is fine, but its cold-start context
   assumed the station name would need reading from handover: it is
   `MOUNT STREET LOWER`. Also learned: the feed's own `last_update` can
   lag ~5 min behind wall clock; Phase 2's "< 15 min" threshold already
   absorbs this. No file edits needed beyond this note.
3. NO — JCDecaux endpoint/fields are exactly what `docs/phase-2.md` and
   `docs/phase-6.md` assume (`name`, `available_bikes`,
   `available_bike_stands`, `bike_stands`, `last_update` epoch-ms).
   Python is 3.14.4, within the files' "≥3.11".
4. NO.
5. NO — next-riskiest is A3 (HF Spaces free tier), which Phase 2 targets.

### 2026-07-09 — after Phase 2

1. YES (already handled mid-phase) — A3 (HF Spaces free Docker tier)
   was invalidated during this phase; D3 reopened per its condition,
   host changed to Render, A3b added and now CONFIRMED by this anchor.
   All affected files were amended in the same session (see Locked
   decisions & assumptions note).
2. NO — Phase 3's anchor (historical-data audit thresholds) is
   host-independent and unchanged.
3. NO — nothing Phase 3 assumes landed differently; deploy flow is now
   `git push origin main` → Render auto-deploy, already reflected in
   `docs/phase-5.md`.
4. NO.
5. NO — next-riskiest standing assumption is A2 (historical data
   exists at usable granularity), which is exactly Phase 3's target.

## Session log (brief)

- 2026-07-08 — Planning session: docs bundle created; no code written.
- 2026-07-08/09 — Build session: Phase 1 executed and closed. Probe
  script written, JCDecaux feed verified live, anchor PASS (18 vs 18
  bikes, same minute). Station locked: MOUNT STREET LOWER.
- 2026-07-09 — Build session (continued): Phase 2 executed and closed.
  FastAPI app + Docker + tests built; HF Spaces found paid mid-phase →
  re-planned to Render (D3/A3/A3b); UTC-timestamp display bug found on
  the deployed page and fixed (Dublin-time + minutes-ago). Anchor PASS
  (20 vs 20 bikes on mobile data). Live URL:
  https://dublin-bikes-forecast.onrender.com
