"""GET endpoints that serve views over the Day 3 intelligence table."""
from fastapi import APIRouter, HTTPException

from app.services.engagement_service import (
    dashboard_summary, attrition_by_department, get_employee,
)
from app.services.skill_gap_service import org_skill_gaps
from app.services.recommendation_service import top_recommendations

router = APIRouter()


@router.get("/dashboard/summary")
def dashboard_summary_route():
    return dashboard_summary()


@router.get("/dashboard/attrition-by-department")
def attrition_by_department_route():
    return attrition_by_department()


@router.get("/dashboard/skill-gaps")
def skill_gaps_route():
    return org_skill_gaps()


@router.get("/dashboard/recommendations")
def recommendations_route(limit: int = 10):
    return top_recommendations(limit)

@router.get("/dashboard/skill-heatmap")
def skill_heatmap_route():
    return org_skill_heatmap()


@router.get("/employees/{employee_id}/career-path")
def career_path_route(employee_id: int):
    result = career_path_for_employee(employee_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No career path data for employee {employee_id}")
    return result

@router.get("/employees/{employee_id}")
def employee_route(employee_id: int):
    employee = get_employee(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    return employee
