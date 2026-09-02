"""
Streamlit dashboard for the Workforce Intelligence Platform.
Run with: streamlit run frontend/dashboard.py   (from the project root)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from app.services.engagement_service import (
    dashboard_summary, attrition_by_department, load_intelligence_table,
)
from app.services.skill_gap_service import org_skill_gaps
from app.services.recommendation_service import top_recommendations
from app.services.career_service import load_heatmap_table, career_path_for_employee
from app.services.policy_service import answer_policy_question

st.set_page_config(page_title="Workforce Intelligence Platform", page_icon="\U0001F9ED", layout="wide")

BG = "#0B0E14"
CARD = "#161B24"
BORDER = "#262B36"
TEXT = "#F1F5F9"
MUTED = "#8A94A6"
ACCENT = "#2DD4BF"
ACCENT_TINT = "rgba(45,212,191,0.12)"
RISK_RED = "#F87171"
RISK_AMBER = "#FBBF24"
RISK_GREEN = "#4ADE80"

plt.rcParams.update({
    "figure.facecolor": CARD, "axes.facecolor": CARD,
    "axes.edgecolor": BORDER, "axes.labelcolor": TEXT,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": TEXT,
})

st.markdown(f"""
<style>
.hero-title {{ font-size: 30px; font-weight: 800; color: {TEXT}; margin-bottom: 0; letter-spacing: -0.3px; }}
.hero-subtitle {{ font-size: 14px; color: {MUTED}; margin-top: 2px; }}

.kpi-card {{
    background: {CARD};
    border-radius: 14px;
    padding: 18px 20px;
    border: 1px solid {BORDER};
}}
.kpi-icon {{
    font-size: 17px; width: 36px; height: 36px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 12px; background: {ACCENT_TINT};
}}
.kpi-value {{ font-size: 27px; font-weight: 800; margin: 0; line-height: 1; color: {TEXT}; letter-spacing: -0.3px; }}
.kpi-label {{ font-size: 11.5px; color: {MUTED}; margin: 6px 0 0 0; text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600; }}

.section-label {{
    font-size: 12px; font-weight: 700; color: {ACCENT}; text-transform: uppercase;
    letter-spacing: 0.8px; margin-bottom: 6px;
}}

.col-guide {{
    background: {CARD};
    border-radius: 14px;
    padding: 18px 20px;
    border: 1px solid {BORDER};
}}
.col-guide-title {{
    font-size: 12.5px; font-weight: 700; color: {TEXT};
    text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px;
}}
.guide-row {{ padding: 9px 0; border-bottom: 1px solid {BORDER}; }}
.guide-row:last-child {{ border-bottom: none; padding-bottom: 0; }}
.guide-name {{ font-size: 12.5px; font-weight: 700; color: {ACCENT}; margin: 0 0 3px 0; }}
.guide-desc {{ font-size: 12px; color: {MUTED}; margin: 0; line-height: 1.5; }}
</style>
""", unsafe_allow_html=True)


def kpi_card(icon, label, value, is_risk=False):
    icon_bg = "rgba(248,113,113,0.15)" if is_risk else ACCENT_TINT
    value_color = RISK_RED if is_risk else TEXT
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon" style="background:{icon_bg}">{icon}</div>
        <p class="kpi-value" style="color:{value_color}">{value}</p>
        <p class="kpi-label">{label}</p>
    </div>
    """, unsafe_allow_html=True)


def color_risk(val):
    colors = {
        "HIGH": "rgba(248,113,113,0.16)",
        "MEDIUM": "rgba(251,191,36,0.16)",
        "LOW": "rgba(74,222,128,0.14)",
    }
    return f"background-color: {colors.get(val, 'transparent')}; color: {TEXT}"


def column_guide(title, descriptions):
    rows = "".join(
        f'<div class="guide-row"><p class="guide-name">{col}</p><p class="guide-desc">{desc}</p></div>'
        for col, desc in descriptions
    )
    st.markdown(f"""
    <div class="col-guide">
        <div class="col-guide-title">{title}</div>
        {rows}
    </div>
    """, unsafe_allow_html=True)


def section(icon, title):
    st.markdown(f'<p class="section-label">{icon} {title}</p>', unsafe_allow_html=True)


st.markdown('<p class="hero-title">Workforce Intelligence Platform</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Predictive attrition, skill gaps & career readiness -- one continuous view</p>', unsafe_allow_html=True)
st.write("")

df = load_intelligence_table()
summary = dashboard_summary()
heatmap_df = load_heatmap_table()

st.sidebar.header("Filters")
departments = ["All"] + sorted(df["Dept"].unique().tolist())
selected_dept = st.sidebar.selectbox("Department", departments)
risk_filter = st.sidebar.multiselect("Risk Level", ["HIGH", "MEDIUM", "LOW"], default=["HIGH", "MEDIUM", "LOW"])

# ---------------------------------------------------------------------------
# HR Policy Assistant -- sidebar chat, visible on every tab
# ---------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### \U0001F4AC HR Policy Assistant")

if "policy_chat_history" not in st.session_state:
    st.session_state.policy_chat_history = []

for msg in st.session_state.policy_chat_history[-6:]:
    with st.sidebar.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_q = st.sidebar.chat_input("Ask about HR policy...")
if user_q:
    st.session_state.policy_chat_history.append({"role": "user", "content": user_q})
    with st.spinner("Checking policy..."):
        policy_result = answer_policy_question(user_q)
    st.session_state.policy_chat_history.append({"role": "assistant", "content": policy_result["answer"]})
    st.rerun()

filtered = df.copy()
if selected_dept != "All":
    filtered = filtered[filtered["Dept"] == selected_dept]
filtered = filtered[filtered["Risk"].isin(risk_filter)]

total_employees = summary["total_employees"]
high_risk = summary["high_risk_employees"]
avg_engagement = summary["average_engagement"]
critical_gaps = int((heatmap_df["Severity"] == "HIGH").sum())

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("\U0001F465", "Employees", f"{total_employees:,}")
with c2: kpi_card("\u26A0", "High Risk", high_risk, is_risk=True)
with c3: kpi_card("\U0001F4C8", "Avg Engagement", f"{avg_engagement}%")
with c4: kpi_card("\U0001F9E9", "Critical Skill Gaps", critical_gaps)

st.write("")

tab_overview, tab_attrition, tab_skills, tab_career = st.tabs(
    ["Overview", "Attrition Risk", "Skills & Recommendations", "Career Path"]
)

# ---------------------------------------------------------------------------
with tab_overview:
    col1, col2 = st.columns(2)
    with col1:
        section("\U0001F4CA", "Risk Distribution")
        risk_counts = df["Risk"].value_counts().reindex(["HIGH", "MEDIUM", "LOW"]).fillna(0)
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.bar(risk_counts.index, risk_counts.values, color=[RISK_RED, RISK_AMBER, RISK_GREEN], width=0.55)
        ax.set_ylabel("Employees")
        ax.spines[["top", "right"]].set_visible(False)
        for i, v in enumerate(risk_counts.values):
            ax.text(i, v + 2, str(int(v)), ha="center", fontweight="bold", color=TEXT)
        st.pyplot(fig)
    with col2:
        section("\U0001F3E2", "Attrition Risk by Department")
        by_dept = pd.DataFrame(attrition_by_department()).set_index("Dept")
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        ax2.barh(by_dept.index, by_dept["avg_attrition_prob"], color=ACCENT, height=0.55)
        ax2.set_xlabel("Avg Attrition Probability")
        ax2.spines[["top", "right"]].set_visible(False)
        st.pyplot(fig2)

# ---------------------------------------------------------------------------
with tab_attrition:
    main_col, guide_col = st.columns([4, 1])
    with main_col:
        section("\U0001F4CB", f"Employees ({len(filtered)} shown)")
        display_cols = ["Employee_ID", "Dept", "Role", "Attrition_Prob", "Risk", "Engagement"]
        styled = filtered[display_cols].sort_values("Attrition_Prob", ascending=False) \
            .style.map(color_risk, subset=["Risk"])
        st.dataframe(styled, use_container_width=True, height=420)

        st.write("")
        section("\U0001F50D", "Look up an employee")
        lookup_id = st.number_input("Employee ID", min_value=1, step=1, key="risk_lookup")
        if st.button("Show details", key="risk_lookup_btn"):
            emp = df[df["Employee_ID"] == lookup_id]
            if emp.empty:
                st.warning("Employee not found.")
            else:
                row = emp.iloc[0]
                rc1, rc2, rc3 = st.columns(3)
                rc1.metric("Attrition Probability", f"{row['Attrition_Prob']*100:.1f}%")
                rc2.metric("Risk", row["Risk"])
                rc3.metric("Engagement", f"{row['Engagement']}%")
    with guide_col:
        column_guide("Column Guide", [
            ("Employee_ID", "Unique employee identifier"),
            ("Dept", "Department the employee belongs to"),
            ("Role", "Current job role"),
            ("Attrition_Prob", "Predicted probability the employee leaves"),
            ("Risk", "HIGH / MEDIUM / LOW -- percentile rank vs. peers"),
            ("Engagement", "Engagement score (0-100%)"),
        ])

# ---------------------------------------------------------------------------
with tab_skills:
    main_col, guide_col = st.columns([4, 1])
    with main_col:
        section("\U0001F5FA", "Organization Skill Heatmap")
        st.dataframe(heatmap_df.style.map(color_risk, subset=["Severity"]), use_container_width=True)
        st.caption(f"Recommended: reskill {heatmap_df['ReskillCount'].sum()} internally, hire {heatmap_df['HireCount'].sum()} externally.")

        st.write("")
        section("\U0001F4A1", "Top Recommendations")
        recs = pd.DataFrame(top_recommendations(15))
        st.dataframe(recs, use_container_width=True)
    with guide_col:
        column_guide("Skill Heatmap", [
            ("Skill", "Skill tracked org-wide"),
            ("Required", "Employees whose role requires it"),
            ("Available", "How many already have it"),
            ("MissingCount", "How many don't have it"),
            ("MissingPct", "% of whole workforce missing it"),
            ("Severity", "HIGH/MEDIUM/LOW based on MissingPct"),
            ("ReskillCount", "Recommended to train internally"),
            ("HireCount", "Recommended to hire externally"),
        ])
        st.write("")
        column_guide("Recommendations", [
            ("Skill_Gap", "Employee's missing skill(s)"),
            ("Gap_Severity", "Higher = more urgent"),
            ("Recommendation", "Suggested course or action"),
        ])

# ---------------------------------------------------------------------------
with tab_career:
    section("\U0001F9ED", "Career Path Readiness")
    career_emp_id = st.number_input("Employee ID", min_value=1, step=1, key="career_lookup")
    if st.button("Show career path"):
        path = career_path_for_employee(int(career_emp_id))
        if path is None:
            st.warning("No career path defined for this employee's current role.")
        else:
            cc1, cc2, cc3 = st.columns(3)
            cc1.metric("Current Role", path["CurrentRole"])
            cc2.metric("Target Role", path["TargetRole"])
            cc3.metric("Readiness Today", f"{path['ReadinessToday']}%")
            st.progress(path["ReadinessToday"] / 100)
            st.write(f"**Projected after training:** {path['ReadinessAfterTraining']}%")
            st.write(f"**Missing skills:** {path['MissingSkills']}")
