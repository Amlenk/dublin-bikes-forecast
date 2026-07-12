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
Render environment variable. Host was changed HF Spaces → Render
mid-Phase-2 (see Locked decisions & assumptions note below).

Phase 3 CLOSED (anchor PASS 2026-07-09): historical training data
secured — three monthly GBFS-style CSVs (Mar–May 2026, 1.88M rows, 115
stations) in `data/raw/` (gitignored, ~77 MB each; re-download URLs in
`data/DATA_AUDIT.md`). MOUNT STREET LOWER: 16,874 rows, 91-day span,
median cadence 10 min, σ=9.46 last week. Station names match the live
feed exactly.

Phase 4 CLOSED (anchor PASS 2026-07-09): trained model
(`HistGradientBoostingRegressor`, sklearn 1.9.0, 9 features) beats the
pre-committed persistence baseline on the held-out fortnight
2026-05-18..31: **model MAE 1.6150 vs baseline 2.0843 (−22.5%)**,
2016 identical eval rows. Artifacts in `model/artifacts/`
(`model_v1.joblib` — dict with model/feature_columns/metadata — and
`climatology.csv` hour-of-week means for Phase 5 serving lags).
Full record: `model/EVAL.md`.

Phase 5 CLOSED (anchor PASS 2026-07-09): **the walking skeleton is
complete in its final form** — the live page serves model v1 (lags via
train-time climatology; `POST /predict` parity endpoint returned the
pre-committed golden value 17.9037 exactly). sklearn pinned to 1.9.0
in requirements.txt; Docker image ships `model/artifacts/`. 20 unit
tests passing (`pytest`).

Phase 6 CLOSED (anchor PASS 2026-07-11, on the third attempt):
**unattended scheduled ingestion is live** — cron-job.org (user's free
account) POSTs `workflow_dispatch` to the `ingest` GitHub Actions
workflow every 30 min (fine-grained PAT, repo-scoped, Actions r/w;
stored only in cron-job.org); a `7,37 * * * *` GitHub cron remains as
backstop. Each run snapshots all 114 JCDecaux stations into Neon
free-tier Postgres (`snapshots` table, `ON CONFLICT DO NOTHING`).
GitHub's own cron proved unreliable for this repo (~2 h median gaps at
both `*/30` and off-peak minutes — see Anchor Results 2026-07-10 and
D7's two amendments). **All six planned phases are now CLOSED; the
Parking Lot is the menu.**

## The ONE next task

**Consult the user: the planned phases are complete.** The Parking
Lot below is the menu. Recommended first pick (per the Parking Lot's
own ordering): the recruiter-facing README + resume bullets, written
ONLY from measured numbers that now all exist — live URL, MAE
1.6150 vs baseline 2.0843 (−22.5%), and the ingestion pipeline's
observed run counts (30 runs / 100% success / 12 h window). The user
accepts Phase 6 manually before anything further (phase-6.md
close-out step 6).

## How to verify the previous phase actually works

Run (PowerShell, any machine):
`Invoke-RestMethod -Method Post -Uri https://dublin-bikes-forecast.onrender.com/predict -ContentType "application/json" -Body (Get-Content tests\fixtures\golden_input.json -Raw)`
Expected: `prediction = 17.9037`. Also open
https://dublin-bikes-forecast.onrender.com — label reads
`model v1 (trained 2026-07-09)`.

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

### 2026-07-09 — Phase 3 anchor

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

All five thresholds from docs/phase-3.md met (details in
data/DATA_AUDIT.md): 91 days ≥ 60; 10.0 min ≤ 60; values 0–40 within
[0,45]; σ 9.46 > 2.0; exact station-name match with the live feed.

Verdict: PASS

### 2026-07-09 — Phase 4 anchor

Step-1 baseline (committed 19a37c8, before any model code):
`persistence_baseline_mae=2.0843` (2016 rows). Then
`python model/train.py` observed output:

```
train rows: 10138  holdout rows: 2016
persistence on model holdout rows: mae=2.0843
baseline_mae=2.0843 (step-1 definition, rows=2016)
model_mae=1.6150
```

(a) baseline reproduced exactly (2.0843 vs 2.0843, tolerance ±0.01);
(b) model_mae 1.6150 < 2.0843 strictly (−22.5%);
(c) `model/artifacts/model_v1.joblib` exists; `model/EVAL.md` records
both numbers and the window.

Verdict: PASS

### 2026-07-09 — Phase 5 Step 1 (golden pair, recorded before serving code)

```
$ python scripts/golden_offline.py
golden_prediction=17.9037
```

Input: `tests/fixtures/golden_input.json` (bikes_now 18, lag_1h 17,
lag_2h 16, lag_24h 15, lag_1w 14, roll_3h 16.5, hour 9, dow 2,
is_weekend 0). The Phase 5 anchor requires the deployed
`POST /predict` to return 17.9037 for this input, to 4 decimals.

### 2026-07-09 — Phase 5 anchor

Deployed parity check (golden pair committed 90ac245, before serving
code):

```
POST https://dublin-bikes-forecast.onrender.com/predict  <- golden_input.json
deployed prediction: 17.9037
golden (pre-committed): 17.9037
PARITY: EXACT MATCH
```

Live page at the same time (remote fetch): `MOUNT STREET LOWER`,
bikes 22, forecast 25 (within [0, 40]), `Feed updated 0 min ago`,
label `model v1 (trained 2026-07-09)`. All three expected
observations met: (a) parity to 4 decimals; (b) model-v1 label +
in-range forecast; (c) feed age < 15 min.

Verdict: PASS

### 2026-07-10 — Phase 6 anchor

Unattended window: 2026-07-09 09:05 UTC → 2026-07-10 10:39 UTC
(~25.5 h, more than double the required 12 h; dev machine off).

GitHub Actions tab (via public API, `ingest` workflow, run start times
UTC):

```
2026-07-10 08:22  schedule  success
2026-07-10 04:33  schedule  success
2026-07-10 00:05  schedule  success
2026-07-09 22:50  schedule  success
2026-07-09 21:04  schedule  success
2026-07-09 19:07  schedule  success
2026-07-09 17:01  schedule  success
2026-07-09 14:05  schedule  success
2026-07-09 11:07  schedule  success
```

9 scheduled runs over the full 25.5 h window (expected ≥ 18 per
12 h), 9/9 success (100%), zero manual runs inside the window. Gaps
between runs: 1h15–4h28, median ≈ 2h31 — not the 30-minute cadence.

Neon SQL (psycopg via `.env` DATABASE_URL, station_id 56 = MOUNT
STREET LOWER, run 2026-07-10 10:40 UTC):

```
SELECT count(*), min(ts), max(ts), count(DISTINCT ts) FROM snapshots
 WHERE station_id = 56 AND ts > now() - interval '12 hours';
-- count 4 | min 2026-07-09 22:46:23+00 | max 2026-07-10 08:21:30+00
-- distinct 4 | span 9 h 35 m
```

Expected count ≥ 15, distinct ≥ 15, span ≥ 10 h → not met. Full
window since 09:05 UTC: 9 rows, 9 distinct ts, span 21 h 17 m; table
total 1,254 rows = 228 pre-window + 9 × 114 (every scheduled run
wrote all 114 stations; write path is 100% sound).

Verdict: **FAIL on cadence** — checks (a) and (b) missed; check (c)
(all runs `schedule`-triggered, 100% success) passed. Failure mode is
exactly pre-mortem #4: GitHub's cron scheduler ran the `*/30` workflow
every ~1–4.5 h, not every 30 min (documented best-effort behavior on
free/public repos). Median gap 2h31 > 60 min → **D7's reopen
condition FIRED**; scheduler must be re-planned before the phase can
close. The pipeline itself (workflow → JCDecaux feed → Neon insert) is
proven end-to-end by 9/9 green unattended runs.

### 2026-07-11 — Phase 6 anchor (third attempt, after D7's second amendment)

Unattended window: 2026-07-10 21:29 UTC → 2026-07-11 09:46 UTC
(12 h 17 m; dev machine off; trigger = cron-job.org pinger).

GitHub Actions (via public API, `ingest` workflow, runs since window
start): **30 runs, 30/30 success (100%)** — 24 `workflow_dispatch`
runs from the pinger landing exactly on the :00/:30 marks
(22:00:32, 22:30:28, 23:00:33, … 09:00:30, 09:30:29 — no missed
slot in 12 h) plus 6 `schedule` runs from the backstop cron.

Neon SQL (psycopg via `.env` DATABASE_URL, station_id 56 = MOUNT
STREET LOWER, run 2026-07-11 09:47 UTC):

```
SELECT count(*), min(ts), max(ts), count(DISTINCT ts) FROM snapshots
 WHERE station_id = 56 AND ts > now() - interval '12 hours';
-- count 28 | distinct 28
-- min 2026-07-10 21:55:49+00 | max 2026-07-11 09:26:57+00
-- span 11:31:08
```

Table total 5,098 rows. Against expected: (a) ≥ 18 runs ≥ 90%
success → 30 at 100% ✓; (b) count ≥ 15, distinct ≥ 15, span ≥ 10 h →
28 / 28 / 11h31m ✓; (c) as amended in D7 (Event `workflow_dispatch`
on the pinger's 30-min cadence, machine off) → 24/24 slots hit ✓.
Unit tests: 20/20 pass (`pytest`, includes the three Phase 6 guards).

Verdict: **PASS**

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
- 2026-07-10 — **D7 reopened and AMENDED: cron moved to off-peak
  minutes `7,37 * * * *`.** The Phase 6 anchor observed median
  snapshot gap ≈ 2h31 with `*/30` (> 60 min threshold), firing D7's
  reopen. User chose the congestion-mitigation option over an external
  cron pinger (kept as fallback). `docs/01-decisions.md` D7 and
  `.github/workflows/ingest.yml` amended; second anchor window
  pending.
- 2026-07-10/11 — **D7 amended a second time (external cron-job.org
  pinger → `workflow_dispatch`; GitHub cron kept as backstop), then
  CONFIRMED in amended form by the Phase 6 anchor PASS** (24/24 pinger
  slots in 12 unattended hours). Full detail in `docs/01-decisions.md`
  D7. Operational dependency added: the pinger uses a fine-grained
  PAT that expires ~2026-10-08 — see Parking Lot.

## Parking Lot (deferred items & future ideas)

- ~~Recruiter-facing README + resume bullets~~ — **DONE 2026-07-11**:
  README rewritten from measured numbers; Dublin Bikes project added to
  all three tailored resumes in `Z:\Claude\resume-tailored\` (DOCX+PDF
  regenerated, 2 pages each) and to `Z:\Claude\LINKEDIN_PROFILE_KIT.md`
  (About bullet, ready-to-paste Projects entry, skills keywords). User
  confirmed LinkedIn itself updated 2026-07-11 (project + skill tags).
- Automated weekly retraining (GitHub Actions job retrains on ingested
  Postgres data, versions the artifact) — deferred: CVT completes with a
  once-trained model — earliest: after Phase 6.
- ~~Serving reads recent lags from Postgres instead of climatology
  lookup~~ — **DONE 2026-07-12 (anchor PASS)**: user set DATABASE_URL
  on Render; deployed page shows "Lags: live history (lag_1h,
  lag_24h, lag_2h, roll_3h), climatology for the rest"; deployed
  golden /predict = 17.9037 exact; independent local recomputation
  from the same Neon rows + live feed reproduced the deployed
  forecast exactly (bikes=1 → forecast=1, same lag set). lag_1w goes
  live automatically ~2026-07-16. Original build notes:
  `app/lags.py` rebuilds the exact training grid (10-min buckets,
  ffill limit 3) from the station's recent `snapshots` rows and
  overlays real values per-lag onto climatology (missing lags — e.g.
  lag_1w until ~2026-07-16 — stay climatology); the page's meta line
  names which lags are live. No DATABASE_URL ⇒ behavior identical to
  before (verified: same forecast, golden 17.9037 intact; 6 new unit
  tests, 29 total). **USER STEP: add DATABASE_URL (Neon connection
  string from `.env`) as an environment variable on the Render
  service.** Anchor to run after that: deployed page's meta line
  shows "live history (…)" lag names, golden /predict still 17.9037,
  and the shown forecast reproducible locally from the same Neon rows.
- ~~Historical backfill of `data/raw/` into Postgres~~ — **DONE
  2026-07-11**: `scripts/backfill_history.py` loaded 1,880,190 rows /
  115 stations (2026-03-01..2026-05-31) into a new `history` table
  (schema in db/schema.sql; COPY-based, refuses to run twice).
  Deliberately SEPARATE from `snapshots`: Smart Dublin and JCDecaux
  use different station-id spaces — join on station_name (Phase 3
  verified exact match). External check: MOUNT STREET LOWER count in
  Neon = 16,874, exactly matching DATA_AUDIT.md's Phase 3 audit.
  Neon usage after load: 208 MB of the free 512 MB. 3 new unit tests
  (23 total).
- Multi-station support + map UI — deferred: CVT names one station
  (decision D4) — earliest: after Phase 5 closes (D4 reopen).
- ~~History charts / sparklines on the page~~ — **DONE 2026-07-12**:
  server-rendered inline-SVG 24h availability sparkline
  (`app/sparkline.py`, no JS, native tooltip hovers, y = 0..capacity,
  true time-scale x) fed by the same single snapshots query as the
  real lags. Anchor: deployed page rendered 56 points = 56 Neon rows
  in the window (exact match); visual check via browser screenshot;
  endpoint labels made relative (24 h ago / now) after the check.
  5 new tests (34 total). Omitted entirely without DATABASE_URL.
- Uncertainty intervals (quantile models) — deferred: flesh — after
  Phase 6.
- ~~CI: pytest on push + badge in README~~ — **DONE 2026-07-11**:
  `.github/workflows/ci.yml` runs the 20-test suite on every push/PR
  (needs `httpx` + `psycopg[binary]` beyond requirements.txt); first
  run green on 21e0f11 (GitHub Actions record); badge in README.
  NOTE for user: Render dashboard → the service → Settings → Build &
  Deploy → set Auto-Deploy to "After CI Checks Pass" to make broken
  pushes unable to reach the live site.
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
- **Rotate the cron-job.org PAT before it expires (~2026-10-08,
  90-day fine-grained token created 2026-07-11)** — when it expires
  the pinger's dispatches start returning 401 and ingestion silently
  degrades to the unreliable backstop cron. Regenerate the token in
  GitHub → update the Authorization header in the cron-job.org job.
  (Pairs naturally with the ingestion-failure-alerting item above.)

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

### 2026-07-09 — after Phase 3

1. NO — nothing invalidated; A2, A4, A8 all CONFIRMED (statuses updated
   in `docs/01-decisions.md`).
2. YES (minor) — Phase 4's anchor procedure is unchanged, but its
   held-out window is now concrete (last 14 full days = 2026-05-18 to
   2026-05-31) and the irregular cadence needed a resampling rule.
   Added a Data-cadence note to `docs/phase-4.md` cold-start context:
   resample to a regular 10-min grid, forward-fill ≤ 3 steps, baseline
   computed on the same grid.
3. NO — paths and schema match what `docs/phase-4.md` assumes.
4. NO.
5. NO — Phase 4's target (model beats baseline) is the next open risk
   on the spine.

### 2026-07-09 — after Phase 4

1. NO — nothing invalidated. D2 (sklearn, no deep learning) held: the
   first iteration beat the baseline; its reopen condition never fired.
2. YES (minor) — Phase 5's anchor is unchanged, but its cold-start
   context now records the artifact's actual structure (joblib dict,
   9 feature columns, sklearn 1.9.0 to pin) and the climatology CSV
   schema. `docs/phase-5.md` amended.
3. NO — paths landed exactly as `docs/phase-5.md` assumes
   (`model/artifacts/model_v1.joblib`, `climatology.csv`).
4. NO.
5. NO — remaining open assumptions (A6 Neon, GHA cron) belong to
   Phase 6; Phase 5 (serving parity) is the next spine gap.

### 2026-07-09 — after Phase 5

1. NO — nothing invalidated. D4's reopen condition occurred (skeleton
   complete); noted in `docs/01-decisions.md`, decision stands pending
   user choice.
2. NO — Phase 6's anchor (GitHub Actions runs + Neon SQL counts) is
   unaffected by anything Phase 5 changed.
3. NO — Phase 6 touches `scripts/` and `.github/workflows/` only; the
   app layout it assumes is unchanged.
4. NO.
5. NO — A6 (Neon, no card) and A4/D7 (GHA cron reliability) are the
   open assumptions and Phase 6 targets exactly them.

### 2026-07-11 — after Phase 6

1. YES (handled in-session) — D7's embedded assumption that GitHub's
   cron alone delivers ~30-min cadence was invalidated by two failed
   windows; D7 amended twice (final form: cron-job.org pinger →
   `workflow_dispatch`, GitHub cron as backstop) and CONFIRMED by the
   passing anchor. A6 CONFIRMED. No downstream phase files exist to
   amend — this was the last planned phase.
2. N/A — no next phase; the Parking Lot is the menu (user consulted).
3. N/A for phase files; recorded for future work: ingestion runs show
   Event `workflow_dispatch` (not `schedule`), cadence is owned by
   cron-job.org, and rows accrue ~48/day/station in `snapshots`.
4. NO — the spine is complete; nothing in the Parking Lot blocks it.
   One time-bomb noted as a dated Parking Lot item: PAT expiry
   ~2026-10-08.
5. N/A — no next phase to re-order; riskiest standing item is the
   PAT-expiry/silent-degradation pair, mitigated by the dated Parking
   Lot entry and the alerting idea.

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
- 2026-07-09 — Build session (continued): Phase 3 executed and closed.
  Located Smart Dublin monthly GBFS files (current through May 2026),
  downloaded Mar–May 2026 (~232 MB, gitignored), audit script + tests
  written, anchor PASS on all five thresholds. DATA_AUDIT.md records
  schema, URLs, and observed stats.
- 2026-07-09 — Build session (continued): Phase 4 executed and closed.
  Baseline (2.0843) committed before model code; features + trainer +
  4 tests written; first model beat baseline: MAE 1.6150 (−22.5%).
  Artifacts + climatology exported for Phase 5.
- 2026-07-09 — Build session (continued): Phase 5 executed and closed.
  Golden pair (17.9037) committed before serving code; model v1 now
  live with climatology serving lags + /predict endpoint; deployed
  parity EXACT. Skeleton complete in final form.
- 2026-07-09 — Build session (continued): Phase 6 pipeline built and
  deployed. Schema applied to Neon; local ingest inserted 114 rows;
  manual workflow_dispatch run from GitHub's runner inserted 114 more
  (228 total) — secrets verified in CI. Unattended 12-hour anchor
  window started ~09:05 UTC; anchor to be run next session.
- 2026-07-10 — Anchor session: Phase 6 anchor RUN → FAIL on cadence
  (9 scheduled runs in 25.5 h, median gap 2h31; every run green and
  every write landed — pipeline sound, GitHub `*/30` cron unreliable).
  D7 reopened and amended per user: cron → `7,37 * * * *` (off-peak
  minutes). Second unattended anchor window started at push (commit
  b44b2d3), 2026-07-10 11:09 UTC; re-run the anchor next session
  (fallback if it fails again: external cron pinger →
  workflow_dispatch).
- 2026-07-10 (late) — Second window abandoned mid-flight as
  mathematically failed: `7,37` cron produced 4 runs in 10 h (same
  ~2 h gaps — GitHub throttles this repo's schedule regardless of
  minute choice). D7 amended a second time: user created a
  fine-grained PAT (Actions r/w, repo-scoped) + cron-job.org account;
  pinger POSTs workflow_dispatch every 30 min. Test trigger 21:27 UTC:
  HTTP 204, run green. Third anchor window started 21:29 UTC;
  anchor re-run due any time from 2026-07-11 09:29 UTC. Check (c)
  amended (Event = workflow_dispatch now expected; see D7).
- 2026-07-11 — Anchor session: **Phase 6 anchor PASS — phase CLOSED;
  all six planned phases done.** 30/30 green runs in the 12-h window
  (24/24 pinger slots hit exactly), Neon 28 rows / 28 distinct ts /
  11h31m span, 20/20 tests. A6 CONFIRMED; D7 confirmed in
  twice-amended form. **Phase 6 accepted by the user same session.**
  Next: user picks from the Parking Lot (README/resume bullets
  recommended first).
- 2026-07-11 (later) — Parking Lot session: README/resume/LinkedIn
  item DONE (see Parking Lot). CI DONE: pytest on every push + README
  badge, first run green (21e0f11). Historical backfill DONE:
  1,880,190 rows into new `history` table, externally cross-checked
  against DATA_AUDIT.md (16,874 MOUNT STREET LOWER rows exact match);
  Neon at 208/512 MB. User-approved sequence continues with:
  serving lags from Postgres → weekly retraining → alerting. NOTE:
  serving-lags changes live prediction behavior — needs a fresh
  golden-value protocol and its own anchor; plan before building.
- 2026-07-12 — Serving-lags session: built, tested (29/29), CI green
  (c7c33af), deployed. Design: /predict parity endpoint takes explicit
  features, so the golden value 17.9037 is UNAFFECTED (verified on the
  deployed endpoint post-deploy); only the homepage's feature-building
  changes, and only when DATABASE_URL is present. Deployed page
  currently shows "Lags: climatology" (env var not yet set on Render).
  AWAITING USER: add DATABASE_URL on the Render service (dashboard →
  Environment), then run the activation anchor in the Parking Lot
  entry.
- 2026-07-12 (later) — User set DATABASE_URL on Render; activation
  anchor PASS (see Parking Lot entry): live-history lags shown on the
  deployed page, golden intact, forecast independently reproduced.
  The live site now serves real recent lags. Next in the approved
  sequence: automated weekly retraining, then alerting.
