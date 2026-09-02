"""
Separately from the application logs, keep a record of every prediction --
timestamp, model version, probability, risk level -- under
`data/predictions/`. This is what lets a later check on the prediction
distribution catch anything unexpected, an early warning sign of drift.
"""
import csv
import os
from datetime import datetime, timezone

from app.utils.config import PREDICTION_LOG_FILE, MODEL_VERSION

_FIELDNAMES = ["timestamp", "model_version", "department", "job_role", "probability", "risk"]


def log_prediction(department: str, job_role: str, probability: float, risk: str) -> None:
    file_exists = os.path.exists(PREDICTION_LOG_FILE)
    with open(PREDICTION_LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model_version": MODEL_VERSION,
            "department": department,
            "job_role": job_role,
            "probability": probability,
            "risk": risk,
        })
