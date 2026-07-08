# 01 — Decisions & Assumptions

## Rules for build sessions (do not edit this section)

- Do **not** relitigate a locked decision. If you believe one is wrong,
  check its "Reopen when" condition. If the condition has occurred, record
  the occurrence under the entry, THEN change it (and note the change in
  `docs/handover.md`). If the condition has not occurred, follow the
  decision as written.
- Treat every assumption below as true until its revisit trigger fires.
  When a trigger fires, update the entry's Status, and run the re-planning
  checklist in `docs/handover.md` before continuing.

## Locked decisions

### D1 — Data source order: JCDecaux primary, Smart Dublin fallback
- **Decision:** Use the JCDecaux Open Data API (contract `dublin`,
  free key from developer.jcdecaux.com) as the live feed; if it fails
  Phase 1's checks, use Smart Dublin's real-time dublinbikes API.
- **Alternatives rejected:** Scraping the dublinbikes website (fragile,
  ToS risk); GBFS aggregators (unofficial middlemen, adds a dependency).
- **Rationale (one line):** Official, documented, free, station-level JSON.
- **Reopen when:** Phase 1's anchor fails on BOTH endpoints — then pick a
  different live Irish dataset (e.g. EirGrid demand) and re-run planning.

### D2 — Modeling stack: Python + scikit-learn, no deep learning
- **Decision:** Python 3.12 (≥3.11 acceptable), pandas ≥2.2,
  scikit-learn ≥1.4 (`HistGradientBoostingRegressor` as the first model),
  joblib for artifacts.
- **Alternatives rejected:** PyTorch/LSTM (resume already demonstrates it
  twice; heavy for free CPU hosting; overkill for one tabular series).
- **Rationale (one line):** Small tabular time series + free CPU tier →
  gradient boosting is the boring, honest, deployable choice.
- **Reopen when:** Phase 4's model fails to beat the persistence baseline
  after two documented feature iterations.

### D3 — Serving stack and host: FastAPI in Docker on Render (free tier)
- **REOPENED 2026-07-09:** the reopen condition fired — Hugging Face's
  New Space UI now offers only Static Spaces free; Docker/Gradio Space
  creation is a paid-plan benefit (observed by the user in the UI and
  corroborated by huggingface.co/pricing listing "Create Gradio & Docker
  Spaces" under paid team plans). Host changed to Render.
- **Decision:** FastAPI + Uvicorn (latest stable), packaged with a
  Dockerfile, deployed as a Render **free web service** connected to the
  GitHub repo (Render builds the Dockerfile remotely and auto-deploys on
  every push to `main`). No local Docker required. Free service sleeps
  after 15 min idle; 30–60 s cold start is accepted.
- **Alternatives rejected:** Hugging Face Spaces (Docker now paid —
  see above); Fly/Railway (card requirements); Streamlit Cloud (weak fit
  for an API + ML-engineer positioning).
- **Rationale (one line):** Free with no card (verified 2026-07-09),
  Docker-native, auto-deploy from GitHub, stable public URL.
- **Reopen when:** Phase 2's deploy fails on the free tier, requires
  payment/card, or first-load cold start exceeds 120 s measured on a
  phone.

### D4 — One station end-to-end before any multi-station work
- **Decision:** Everything through Phase 6 targets exactly one station,
  chosen in Phase 1 and recorded in `docs/handover.md`.
- **Alternatives rejected:** All-stations from the start.
- **Rationale (one line):** The CVT names one station; breadth multiplies
  every phase's surface for zero risk retired.
- **Reopen when:** Phase 5 has closed (skeleton complete) — multi-station
  is then a Parking Lot candidate.

### D5 — Free tier only, no credit card anywhere
- **Decision:** Every external service used must be free and must not
  require a credit card at signup.
- **Alternatives rejected:** ≤ €10/month budget (user chose free-only in
  intake, 2026-07-08).
- **Rationale (one line):** User's explicit intake answer.
- **Reopen when:** The user states a budget.

### D6 — Public GitHub repo under github.com/Amlenk
- **Decision:** The project lives in a public GitHub repository named
  `dublin-bikes-forecast` under the user's existing account
  (github.com/Amlenk); local working copy at `Z:\Claude\dublin-bikes-forecast`.
- **Alternatives rejected:** Private repo (recruiters can't see it); code
  only on the HF Space (GitHub is where recruiters look).
- **Rationale (one line):** The repo itself is a recruiter-facing artifact
  and GitHub Actions (Phase 6) needs it.
- **Reopen when:** Never expected; user request only.

### D7 — Scheduler: GitHub Actions cron at 30-minute intervals (Phase 6)
- **Decision:** Unattended ingestion runs as a GitHub Actions scheduled
  workflow (`cron: "*/30 * * * *"`) in the public repo, writing to a Neon
  free-tier Postgres database.
- **Alternatives rejected:** Always-on VM (not free); running on the HF
  Space (Spaces sleep; not a scheduler); Windows Task Scheduler on the
  laptop (defeats "unattended cloud pipeline" resume claim).
- **Rationale (one line):** Free, unattended, and itself a resume-visible
  CI/CD artifact.
- **Reopen when:** Phase 6 observes a median gap between snapshots
  > 60 minutes over a 12-hour window, or Neon signup requires a card
  (then: commit snapshots to the repo as CSV from the workflow instead).

## Intake assumption ledger

### A1 — JCDecaux still operates the `dublin` contract with a free API
- **Assumed:** `api.jcdecaux.com/vls/v1/stations?contract=dublin` serves
  live station data to holders of a free developer key.
- **Default source:** JCDecaux has historically operated dublinbikes and
  published this API; cheapest primary candidate.
- **Revisit trigger:** Phase 1's probe returns HTTP 403/404 or the
  contracts list lacks `dublin`.
- **Status:** CONFIRMED by Phase 1 anchor (2026-07-09): HTTP 200, 114
  stations, count matched the official map exactly.

### A2 — Usable historical data exists on data.gov.ie / Smart Dublin
- **Assumed:** A downloadable historical dublinbikes dataset provides
  station-level availability at ≤ 60-minute granularity covering ≥ 60
  consecutive days.
- **Default source:** Smart Dublin has published quarterly dublinbikes
  archives on data.gov.ie; cheapest training-data route.
- **Revisit trigger:** Phase 3's audit finds no dataset meeting the
  thresholds in `docs/phase-3.md`.
- **Status:** STANDING

### A3 — HF Spaces free tier suffices, no card
- **Assumed:** A free Hugging Face account (no card) can create a Docker
  Space on the free CPU tier that serves this FastAPI app publicly.
- **Default source:** HF Spaces' documented free tier; cheapest host
  satisfying D5.
- **Revisit trigger:** Phase 2's deploy requires payment, fails to build,
  or the public URL is unreachable from a phone.
- **Status:** TRIGGERED (2026-07-09 — Docker Space creation is now a
  paid-plan feature per the New Space UI and huggingface.co/pricing).
  Superseded by A3b below; D3 reopened and changed to Render.

### A3b — Render free web service suffices, no card
- **Assumed:** A free Render account (GitHub sign-in, no card) can run
  this Dockerized FastAPI app as a free web service with a public URL;
  free services sleep after 15 min idle and cold-start in 30–60 s.
- **Default source:** Render free-tier documentation and third-party
  guides, checked 2026-07-09.
- **Revisit trigger:** Phase 2's deploy requires a card, the build
  fails on the free instance, or measured cold start exceeds 120 s.
- **Status:** STANDING

### A4 — Station identity joins across live feed and historical data
- **Assumed:** The station chosen in Phase 1 appears in the historical
  dataset with a matching name or a documentable ID mapping.
- **Default source:** Both publishers describe the same physical network.
- **Revisit trigger:** Phase 3 finds no row for the chosen station (then:
  choose a station present in both, update handover).
- **Status:** STANDING

### A5 — No fixed application deadline
- **Assumed:** There is no hard date by which this project must be on the
  resume; phases proceed at the user's pace.
- **Default source:** Intake mentioned no deadline ("help me find a job").
- **Revisit trigger:** The user names a date — then re-scope: skeleton
  (Phases 1–2) only, park Phases 3–6.
- **Status:** STANDING

### A6 — Neon free-tier Postgres needs no credit card
- **Assumed:** A Neon free-tier Postgres database (≥ 0.5 GB) can be
  created with email-only signup and accepts connections from GitHub
  Actions runners.
- **Default source:** Neon's documented free tier; cheapest managed
  Postgres satisfying D5.
- **Revisit trigger:** Phase 6 signup requires a card or connections from
  Actions are blocked (then D7's CSV-in-repo fallback applies).
- **Status:** STANDING

### A7 — Dev environment: Windows 11, Python ≥3.11, git; no local Docker
- **Assumed:** The build machine is Windows 11 with Python ≥3.11 and git
  available; Docker is NOT required locally because HF Spaces builds the
  image remotely.
- **Default source:** This workspace's machine (Windows 11 Home per
  environment); remote builds are HF Spaces' documented behavior.
- **Revisit trigger:** Any phase file's run commands fail because a tool
  is missing — record what was installed in `docs/handover.md`.
- **Status:** STANDING

### A8 — The chosen station is busy enough to be interesting
- **Assumed:** A high-traffic city-centre station (to be chosen in
  Phase 1 from the live feed, e.g. one with capacity ≥ 30) shows enough
  variation for forecasting to be meaningful.
- **Default source:** City-centre stations dominate usage in any bike
  scheme; cheapest selection rule.
- **Revisit trigger:** Phase 3's audit shows the chosen station's
  availability variance is near zero across a week (then pick another
  station present in both sources).
- **Status:** STANDING
