from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from rag.rag_pipeline import answer_query


router = APIRouter()


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3)
    ticker: str | None = Field(default=None, max_length=10)
    recency_days: int | None = Field(default=None, ge=1, le=365)


@router.post("/query")
def query(payload: QueryRequest) -> dict:
    ticker = payload.ticker.strip().upper() if payload.ticker else None
    try:
        return answer_query(
            payload.question,
            ticker,
            payload.recency_days,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
