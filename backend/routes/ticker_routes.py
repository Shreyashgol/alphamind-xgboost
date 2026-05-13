from fastapi import APIRouter

from core.ticker_catalog import list_available_tickers


router = APIRouter()


@router.get("/tickers")
def tickers() -> dict:
    return {"tickers": list_available_tickers()}
