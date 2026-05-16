from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.explain_routes import router as explain_router
from routes.forecast_routes import router as forecast_router
from routes.query_routes import router as query_router
from routes.ticker_routes import router as ticker_router
from routes.train_routes import router as train_router
from utils.settings import get_settings


settings = get_settings()


app = FastAPI(
    title=f"{settings.app_name} API",
    version="0.1.0",
    description="Forecasting, explanation, and retrieval APIs for stock analysis.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(forecast_router, prefix="/api", tags=["forecast"])
app.include_router(explain_router, prefix="/api", tags=["explain"])
app.include_router(query_router, prefix="/api", tags=["query"])
app.include_router(ticker_router, prefix="/api", tags=["tickers"])
app.include_router(train_router, prefix="/api", tags=["train"])


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
