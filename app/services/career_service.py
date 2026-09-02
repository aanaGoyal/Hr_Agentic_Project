"""Career path readiness and org skill heatmap -- Day 3, Sections 16.5-16.6."""
import pandas as pd

from app.utils.config import PROCESSED_PATH

_career_table = None
_heatmap_table = None


def load_career_table() -> pd.DataFrame:
    global _career_table
    if _career_table is None:
        _career_table = pd.read_csv(f"{PROCESSED_PATH}/career_path_intelligence.csv")
    return _career_table


def load_heatmap_table() -> pd.DataFrame:
    global _heatmap_table
    if _heatmap_table is None:
        _heatmap_table = pd.read_csv(f"{PROCESSED_PATH}/org_skill_heatmap.csv")
    return _heatmap_table


def career_path_for_employee(employee_id: int) -> dict | None:
    df = load_career_table()
    row = df[df["EmployeeID"] == employee_id]
    if row.empty:
        return None
    return row.iloc[0].to_dict()


def org_skill_heatmap() -> list[dict]:
    return load_heatmap_table().to_dict(orient="records")
