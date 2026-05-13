from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from core.automl_engine import train_models


router = APIRouter()


class TrainRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)


@router.post("/train")
def train(payload: TrainRequest) -> dict:
    ticker = payload.ticker.strip().upper()
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker is required.")

    try:
        return train_models(ticker)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
