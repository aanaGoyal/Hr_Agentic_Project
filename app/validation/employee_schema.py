"""
Every request to /predict/attrition gets checked against this model before
it touches any business logic or the ML model -- bad data gets a 422
response and never reaches the model, instead of quietly producing a
garbage prediction. Ranges match Day 1 Section 2's validation rules
(Age 18-100, satisfaction/balance on a 1-4 scale, engagement 0-100).
"""
from typing import Literal

from pydantic import BaseModel, Field


class EmployeePredictionInput(BaseModel):
    Department: str
    JobRole: str
    OverTime: Literal["Yes", "No"]

    Age: int = Field(ge=18, le=100)
    MonthlyIncome: float = Field(gt=0)
    DistanceFromHome: int = Field(ge=0, le=100)
    YearsAtCompany: int = Field(ge=0, le=50)
    YearsSinceLastPromotion: int = Field(ge=0, le=50)
    JobSatisfaction: int = Field(ge=1, le=4)
    WorkLifeBalance: int = Field(ge=1, le=4)
    NumCompaniesWorked: int = Field(ge=0, le=20)
    EngagementScore: float = Field(ge=0, le=100)
    PerformanceRating: int = Field(ge=1, le=4)
    ManagerRating: int = Field(ge=1, le=4)
    TrainingHoursLastYear: int = Field(ge=0, le=200)

    model_config = {
        "json_schema_extra": {
            "example": {
                "Department": "IT", "JobRole": "ML Engineer", "OverTime": "Yes",
                "Age": 29, "MonthlyIncome": 6000, "DistanceFromHome": 8,
                "YearsAtCompany": 2, "YearsSinceLastPromotion": 2,
                "JobSatisfaction": 2, "WorkLifeBalance": 2, "NumCompaniesWorked": 3,
                "EngagementScore": 55.0, "PerformanceRating": 3,
                "ManagerRating": 3, "TrainingHoursLastYear": 20,
            }
        }
    }
