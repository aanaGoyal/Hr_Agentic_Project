"""
FastAPI backend for the Workforce Intelligence Platform. Serves the Day 3
`employee_intelligence.csv` table to the dashboard and exposes a live
attrition-prediction endpoint backed by the Day 2 model.

Run with: uvicorn app.main:app --reload   (from the project root)
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import attrition, dashboard
from app.services.engagement_service import load_intelligence_table
from app.ml.model_loader import load_attrition_model
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Startup: loading intelligence table and attrition model")
    load_intelligence_table()
    load_attrition_model()
    logger.info("Startup complete -- ready to serve requests")
    yield


app = FastAPI(
    title="Workforce Intelligence Platform API",
    description="Attrition prediction, engagement, skill-gap, and "
                 "recommendation endpoints for the HR AI platform.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(dashboard.router)
app.include_router(attrition.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "workforce-intelligence-platform"}
