"""Placeholder forecast: persistence (baseline v0).

Predicted available bikes at t+60 minutes = current available bikes.
The trained model replaces this in Phase 5 (see docs/phase-5.md).
"""
MODEL_LABEL = "baseline v0 (persistence)"
HORIZON_MINUTES = 60


def forecast_bikes(current_bikes: int) -> int:
    return max(0, int(current_bikes))
