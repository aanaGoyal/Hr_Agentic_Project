"""POST /predict/attrition -- runs the model on a single employee."""
from fastapi import APIRouter

from app.services.attrition_service import predict_employee_risk
from app.validation.employee_schema import EmployeePredictionInput

router = APIRouter()


@router.post("/predict/attrition")
def predict_attrition_route(employee: EmployeePredictionInput):
    return predict_employee_risk(employee)
