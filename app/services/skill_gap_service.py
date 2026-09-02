"""
Rebuilds the "organisation-wide missing skill" view (Day 3, Section 14)
directly from `employee_intelligence.csv`'s `Skill_Gap` column, rather than
re-loading the role/skills reference tables -- one less dependency for the
API to carry, and the numbers are guaranteed to match what Day 3 computed.
"""
import pandas as pd

from app.services.engagement_service import load_intelligence_table


def _severity(missing_pct: float) -> str:
    """Same scaled-percentage rule as Day 3, Section 14.2."""
    if missing_pct >= 4:
        return "HIGH"
    if missing_pct >= 2:
        return "MEDIUM"
    return "LOW"


def org_skill_gaps() -> list[dict]:
    df = load_intelligence_table()
    total_workforce = len(df)

    gaps = (
        df.loc[df["Skill_Gap"] != "(none)", "Skill_Gap"]
        .str.split(", ")
        .explode()
    )
    counts = gaps.value_counts().reset_index()
    counts.columns = ["Skill", "MissingCount"]
    counts["MissingPct"] = (counts["MissingCount"] / total_workforce * 100).round(1)
    counts["Severity"] = counts["MissingPct"].apply(_severity)
    counts = counts.sort_values("MissingCount", ascending=False).reset_index(drop=True)
    return counts.to_dict(orient="records")
