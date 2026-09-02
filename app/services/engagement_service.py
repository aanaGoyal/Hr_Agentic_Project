"""
Serves views over `employee_intelligence.csv` -- Day 3's final table. Per
the project notes, "the eventual dashboard is basically just a view onto
it", so this service does no recomputation, only aggregation for display.
"""
import pandas as pd

from app.utils.config import INTELLIGENCE_TABLE

_table = None  # loaded once, reused across requests


def load_intelligence_table() -> pd.DataFrame:
    global _table
    if _table is None:
        _table = pd.read_csv(INTELLIGENCE_TABLE)
    return _table


def dashboard_summary() -> dict:
    df = load_intelligence_table()
    return {
        "total_employees": int(len(df)),
        "high_risk_employees": int((df["Risk"] == "HIGH").sum()),
        "average_engagement": round(float(df["Engagement"].mean()), 1),
    }


def attrition_by_department() -> list[dict]:
    df = load_intelligence_table()
    by_dept = (
        df.groupby("Dept")
        .agg(
            employee_count=("Employee_ID", "count"),
            avg_attrition_prob=("Attrition_Prob", "mean"),
            high_risk_count=("Risk", lambda s: (s == "HIGH").sum()),
        )
        .reset_index()
        .sort_values("avg_attrition_prob", ascending=False)
    )
    by_dept["avg_attrition_prob"] = by_dept["avg_attrition_prob"].round(3)
    return by_dept.to_dict(orient="records")


def get_employee(employee_id: int) -> dict | None:
    df = load_intelligence_table()
    row = df[df["Employee_ID"] == employee_id]
    if row.empty:
        return None
    return row.iloc[0].to_dict()
