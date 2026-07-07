"""
main.py — FastAPI application entry point for CP Analytics Dashboard.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import cf_data, analytics, sentiment

# Create all DB tables on startup (idempotent)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CP Analytics Dashboard API",
    description=(
        "Codeforces analytics API — rating progression, topic breakdown, "
        "verdict analysis, weak topic identification, and NLP community sentiment."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cf_data.router, prefix="/api/cf", tags=["Codeforces Data"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(sentiment.router, prefix="/api/sentiment", tags=["Sentiment"])


@app.get("/", tags=["Health"])
async def root():
    """Health-check / welcome endpoint."""
    return {"status": "ok", "message": "CP Analytics API is running 🚀"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
