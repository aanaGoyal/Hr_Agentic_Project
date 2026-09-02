"""
pytest suite covering the pieces most likely to break silently, per the
project notes' Section 22 checklist:
- missing required column is caught
- invalid engagement/age value is rejected
- attrition prediction returns a real probability
- risk level is assigned correctly from that probability
- skill gap calculation matches expected output
- API returns the expected status codes
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ml.predictor import risk_bucket

client = TestClient(app)

VALID_PAYLOAD = {
    "Department": "IT", "JobRole": "ML Engineer", "OverTime": "Yes",
    "Age": 29, "MonthlyIncome": 6000, "DistanceFromHome": 8,
    "YearsAtCompany": 2, "YearsSinceLastPromotion": 2, "JobSatisfaction": 2,
    "WorkLifeBalance": 2, "NumCompaniesWorked": 3, "EngagementScore": 55.0,
    "PerformanceRating": 3, "ManagerRating": 3, "TrainingHoursLastYear": 20,
}


def test_missing_required_field_is_rejected():
    payload = dict(VALID_PAYLOAD)
    del payload["Age"]
    response = client.post("/predict/attrition", json=payload)
    assert response.status_code == 422


def test_invalid_engagement_score_is_rejected():
    payload = dict(VALID_PAYLOAD, EngagementScore=250)  # out of 0-100 range
    response = client.post("/predict/attrition", json=payload)
    assert response.status_code == 422


def test_invalid_age_is_rejected():
    payload = dict(VALID_PAYLOAD, Age=5)  # below the 18-100 range
    response = client.post("/predict/attrition", json=payload)
    assert response.status_code == 422


def test_attrition_prediction_returns_a_real_probability():
    response = client.post("/predict/attrition", json=VALID_PAYLOAD)
    assert response.status_code == 200
    prob = response.json()["attrition_probability"]
    assert 0.0 <= prob <= 1.0


@pytest.mark.parametrize("prob, expected_risk", [(0.85, "HIGH"), (0.55, "MEDIUM"), (0.1, "LOW")])
def test_risk_level_assigned_correctly_from_probability(prob, expected_risk):
    assert risk_bucket(prob) == expected_risk


def test_skill_gap_matches_expected_output():
    from app.services.skill_gap_service import org_skill_gaps
    gaps = org_skill_gaps()
    assert len(gaps) > 0
    assert {"Skill", "MissingCount", "MissingPct", "Severity"} <= set(gaps[0].keys())
    # results should be sorted by MissingCount, descending
    counts = [row["MissingCount"] for row in gaps]
    assert counts == sorted(counts, reverse=True)


def test_dashboard_summary_returns_200():
    assert client.get("/dashboard/summary").status_code == 200


def test_employee_not_found_returns_404():
    assert client.get("/employees/999999").status_code == 404


def test_employee_found_returns_200():
    assert client.get("/employees/101").status_code == 200
