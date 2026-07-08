# Dublin Bikes Forecast

Live availability + one-hour-ahead forecast for a Dublin Bikes station,
served as a public Dockerized FastAPI app on Render (auto-deployed from
this repo on every push to `main`).

**Live demo:** _URL added after first deploy._

Status: walking skeleton (live feed + persistence placeholder forecast).
The trained model, evaluation numbers, and data pipeline land in later
phases — see `docs/` for the full build plan and verified progress log
(`docs/handover.md`).

Data: [JCDecaux Open Data API](https://developer.jcdecaux.com) (contract
`dublin`), verified live on 2026-07-09.
