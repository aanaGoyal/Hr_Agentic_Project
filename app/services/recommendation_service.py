"""
Serves the per-employee recommendations Day 3's rule-based engine
(Section 15.1) already computed into `employee_intelligence.csv`.
"""
from app.services.engagement_service import load_intelligence_table


def top_recommendations(limit: int = 10) -> list[dict]:
    """Employees with a real skill gap (not '(none)'), ranked by how
    severe that gap is -- the list HR would actually act on first."""
    df = load_intelligence_table()
    has_gap = df[df["Skill_Gap"] != "(none)"]
    ranked = has_gap.sort_values("Gap_Severity", ascending=False).head(limit)
    return ranked[
        ["Employee_ID", "Dept", "Role", "Skill_Gap", "Gap_Severity", "Recommendation"]
    ].to_dict(orient="records")
