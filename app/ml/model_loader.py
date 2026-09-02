"""
Loads the Day 2 attrition pipeline (`models/attrition_pipeline.joblib`).
Kept as its own tiny module so swapping in versioned models later
(Section 9's `models/v1/`, `v2/`, ...) only touches this one function.
"""
import joblib

from app.utils.config import ATTRITION_MODEL_FILE

_model = None  # loaded once, reused across requests


def load_attrition_model():
    global _model
    if _model is None:
        _model = joblib.load(ATTRITION_MODEL_FILE)
    return _model
