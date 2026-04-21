from typing import Dict, List

import pandas as pd
import streamlit as st

from models.milestone import Milestone

_STATUS_LABEL = {
    "Complete": "Complete",
    "On Track": "On Track",
    "At Risk": "At Risk",
    "Slipped": "Slipped",
}


def render(milestones: List[Milestone]) -> None:
    st.title("Milestone Tracker")
    st.caption(
        "Delivery timeline with dependency chain tracking. "
        "A slipped or at-risk milestone propagates to any downstream milestone that depends on it."
    )

    weeks = sorted({ms.due_week for ms in milestones})
    selected_weeks = st.multiselect("Filter by Week", weeks, default=weeks, key="ms_weeks")
    filtered = sorted(
        [ms for ms in milestones if ms.due_week in selected_weeks],
        key=lambda m: m.due_week,
    )

    st.divider()
    _render_milestone_summary(milestones)
    st.divider()
    _render_milestone_table(filtered, milestones)
    st.divider()
    _render_dependency_warnings(milestones)


def _render_milestone_summary(milestones: List[Milestone]) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Complete", sum(1 for m in milestones if m.status == "Complete"))
    col2.metric("On Track", sum(1 for m in milestones if m.status == "On Track"))
    col3.metric("At Risk", sum(1 for m in milestones if m.status == "At Risk"))
    col4.metric("Slipped", sum(1 for m in milestones if m.status == "Slipped"))


def _render_milestone_table(
    filtered: List[Milestone], all_milestones: List[Milestone]
) -> None:
    milestone_by_id: Dict[str, Milestone] = {m.id: m for m in all_milestones}

    rows = []
    for ms in filtered:
        if ms.depends_on:
            dep_labels = []
            for dep_id in ms.depends_on:
                dep = milestone_by_id.get(dep_id)
                if dep:
                    dep_labels.append(f"{dep.name} [{dep.status}]")
            dep_display = " · ".join(dep_labels)
        else:
            dep_display = "—"

        rows.append(
            {
                "Week": f"Wk {ms.due_week}",
                "Status": _STATUS_LABEL.get(ms.status, ms.status),
                "Milestone": ms.name,
                "Owner": ms.owner,
                "Workstream": ms.workstream_id,
                "Depends On": dep_display,
            }
        )

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_dependency_warnings(milestones: List[Milestone]) -> None:
    ms_by_id = {m.id: m for m in milestones}
    at_risk_with_prereqs = [
        ms for ms in milestones if ms.is_at_risk() and ms.has_prerequisites()
    ]

    if not at_risk_with_prereqs:
        return

    st.subheader("Cascading Risk — Dependency Chain")
    st.caption(
        "At-risk milestones with unresolved prerequisites. "
        "Each one below may delay dependent work further down the chain."
    )
    for ms in at_risk_with_prereqs:
        prereq_names = []
        for dep_id in ms.depends_on:
            dep = ms_by_id.get(dep_id)
            if dep:
                prereq_names.append(f"**{dep.name}** ({dep.status})")
        prereq_str = " · ".join(prereq_names)
        st.warning(
            f"**{ms.name}** (Wk {ms.due_week} · {ms.status}) — "
            f"depends on: {prereq_str}"
        )
