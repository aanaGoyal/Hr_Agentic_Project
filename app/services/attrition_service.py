"""
The live-prediction path: validated input -> feature engineering ->
model -> risk bucket -> prediction log. Everything the /predict/attrition
endpoint needs, kept out of the route function so it's testable on its
own (see Section 22's unit tests).
"""
from app.ml.model_loader import load_attrition_model
from app.ml.predictor import predict_attrition
from app.utils.logger import get_logger
from app.utils.prediction_logger import log_prediction
from app.validation.employee_schema import EmployeePredictionInput

logger = get_logger(__name__)


def predict_employee_risk(employee: EmployeePredictionInput) -> dict:
    logger.info("Prediction request received")

    model = load_attrition_model()
    logger.info("Model %s loaded", "attrition_pipeline")

    prob, risk = predict_attrition(model, employee.model_dump())
    log_prediction(employee.Department, employee.JobRole, prob, risk)

    logger.info("Prediction completed -- risk=%s prob=%.4f", risk, prob)
    return {"attrition_probability": prob, "risk_level": risk}
