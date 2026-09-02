"""
Centralized path configuration for the app.

Same directories Day 1-3 already used (all notebooks and this app live
directly at the project root), just resolved once here instead of being
re-typed at the top of every notebook. PROJECT_ROOT is resolved from this
file's own location (not the process's cwd), so it works the same whether
the app is imported from a notebook, from pytest in tests/, or run
directly with `uvicorn app.main:app` from the project root.
"""
import os
from pathlib import Path

PROJECT_ROOT = Path(os.environ.get("HR_AI_BASE") or Path(__file__).resolve().parents[2])

PROCESSED_PATH = str(PROJECT_ROOT / "data" / "processed")
EXTERNAL_PATH = str(PROJECT_ROOT / "data" / "external")
MODELS_PATH = str(PROJECT_ROOT / "models")
PREDICTIONS_PATH = str(PROJECT_ROOT / "data" / "predictions")
LOGS_PATH = str(PROJECT_ROOT / "logs")

INTELLIGENCE_TABLE = f"{PROCESSED_PATH}/employee_intelligence.csv"
ATTRITION_MODEL_FILE = f"{MODELS_PATH}/attrition_pipeline.joblib"
PREDICTION_LOG_FILE = f"{PREDICTIONS_PATH}/prediction_log.csv"
APP_LOG_FILE = f"{LOGS_PATH}/app.log"

MODEL_VERSION = "v1.0"

for _path in (PREDICTIONS_PATH, LOGS_PATH):
    os.makedirs(_path, exist_ok=True)
