"""
Feature engineering + risk bucketing for the attrition model.

This is the exact same logic as Day 3, Section 16.1 -- moved here so the
API and any future batch job call one shared function instead of copying
the four engineered-feature lines around. The pipeline expects to see the
same shape of data it was trained on, so this step can't be skipped even
though the raw fields look "ready" on their own.
"""
import pandas as pd

CATEGORICAL_COLS = ["Department", "JobRole", "OverTime"]

# Raw numeric fields the model was trained on, before engineered columns
# are added. Must match Day 1/2's `employee_attrition_processed.csv` +
# `engagement_processed.csv` columns (minus EmployeeID/Attrition).
RAW_NUMERIC_COLS = [
    "Age", "MonthlyIncome", "DistanceFromHome", "YearsAtCompany",
    "YearsSinceLastPromotion", "JobSatisfaction", "WorkLifeBalance",
    "NumCompaniesWorked", "EngagementScore", "PerformanceRating",
    "ManagerRating", "TrainingHoursLastYear",
]


def engineer_features(record: dict) -> pd.DataFrame:
    """Turns one employee record into the single-row DataFrame the
    pipeline expects -- same four engineered features as Day 3."""
    df = pd.DataFrame([record])

    df["IncomePerYear"] = df["MonthlyIncome"] * 12 / df["YearsAtCompany"].replace(0, 1)
    df["PromotionGapRatio"] = df["YearsSinceLastPromotion"] / df["YearsAtCompany"].replace(0, 1)
    df["OverallSatisfaction"] = (df["JobSatisfaction"] + df["WorkLifeBalance"]) / 2
    df["ExperienceRatio"] = df["YearsAtCompany"] / (df["NumCompaniesWorked"] + 1)

    numeric_cols = RAW_NUMERIC_COLS + [
        "IncomePerYear", "PromotionGapRatio", "OverallSatisfaction", "ExperienceRatio",
    ]
    return df[CATEGORICAL_COLS + numeric_cols]


def risk_bucket(prob: float) -> str:
    """Identical thresholds to Day 3, Section 16.1."""
    if prob >= 0.7:
        return "HIGH"
    if prob >= 0.4:
        return "MEDIUM"
    return "LOW"


def predict_attrition(model, record: dict):
    """Returns (probability, risk_bucket) for one employee record."""
    X = engineer_features(record)
    prob = round(float(model.predict_proba(X)[:, 1][0]), 4)
    return prob, risk_bucket(prob)
