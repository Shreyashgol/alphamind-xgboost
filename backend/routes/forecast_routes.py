from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query

from core.automl_engine import run_forecast


router = APIRouter()


class ForecastRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    horizon: int = Field(default=7, ge=1, le=30)


def _run(ticker: str, horizon: int) -> dict:
    normalized_ticker = ticker.strip().upper()
    if not normalized_ticker:
        raise HTTPException(status_code=400, detail="Ticker is required.")

    try:
        return run_forecast(normalized_ticker, horizon)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/forecast")
def forecast_get(ticker: str, horizon: int = Query(default=7, ge=1, le=30)) -> dict:
    return _run(ticker, horizon)


@router.post("/forecast")
def forecast(payload: ForecastRequest) -> dict:
    return _run(payload.ticker, payload.horizon)
