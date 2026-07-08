from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.forecast import HORIZON_MINUTES, MODEL_LABEL, forecast_bikes
from app.live import LiveFeedError, get_snapshot

app = FastAPI(title="Dublin Bikes Forecast")
templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parents[1] / "templates")
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    try:
        snap = get_snapshot()
        ctx = {
            "error": None,
            "snapshot": snap,
            "forecast": forecast_bikes(snap.bikes),
            "model_label": MODEL_LABEL,
            "horizon": HORIZON_MINUTES,
        }
    except LiveFeedError as exc:
        ctx = {"error": str(exc), "snapshot": None}
    return templates.TemplateResponse(request, "index.html", ctx)
