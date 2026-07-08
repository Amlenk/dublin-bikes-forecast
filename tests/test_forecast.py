from app.forecast import forecast_bikes


def test_persistence_returns_current_value():
    assert forecast_bikes(18) == 18
    assert forecast_bikes(0) == 0


def test_forecast_never_negative():
    assert forecast_bikes(-3) == 0
