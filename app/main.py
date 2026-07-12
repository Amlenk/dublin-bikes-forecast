from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.forecast import (
    HORIZON_MINUTES,
    MODEL_LABEL,
    forecast_bikes,
    predict_from_features,
)
from app.lags import recent_lags
from app.live import STATION_NAME, LiveFeedError, get_snapshot

app = FastAPI(title="Dublin Bikes Forecast")
templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parents[1] / "templates")
)


class Features(BaseModel):
    bikes_now: float
    lag_1h: float
    lag_2h: float
    lag_24h: float
    lag_1w: float
    roll_3h: float
    hour: float
    dow: float
    is_weekend: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(features: Features):
    return {"prediction": round(predict_from_features(features.model_dump()), 4)}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    try:
        snap = get_snapshot()
        age_min = int(
            (datetime.now(timezone.utc) - snap.updated).total_seconds() // 60
        )
        real_lags, live_lag_names = recent_lags(STATION_NAME, snap.updated)
        ctx = {
            "error": None,
            "snapshot": snap,
            "age_minutes": age_min,
            "forecast": forecast_bikes(
                snap.bikes, snap.updated, snap.capacity, real_lags
            ),
            "model_label": MODEL_LABEL,
            "horizon": HORIZON_MINUTES,
            "live_lag_names": live_lag_names,
        }
    except LiveFeedError as exc:
        ctx = {"error": str(exc), "snapshot": None}
    return templates.TemplateResponse(request, "index.html", ctx)
