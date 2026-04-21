from dataclasses import replace
from typing import Dict, List

import pandas as pd
import streamlit as st

from models.checklist import ChecklistItem
from models.milestone import Milestone
from models.raid import RAIDItem
from models.workstream import Workstream
from scoring.readiness import compute_readiness
from utils.helpers import readiness_label, readiness_rag


def render(
    workstreams: List[Workstream],
    milestones: List[Milestone],
    raid_items: List[RAIDItem],
    checklist_items: List[ChecklistItem],
) -> None:
    st.title("Scenario Simulator")
    st.caption(
        "Test how specific slips or re-opened risks would affect the readiness score. "
        "Changes apply to this view only — no underlying data is modified."
    )

    baseline = compute_readiness(workstreams, milestones, raid_items, checklist_items)
    baseline_score = baseline["overall"]

    st.info(f"**Baseline: {baseline_score}%** — {readiness_label(baseline_score)}")
    st.divider()

    col_ms, col_risk = st.columns(2)

    milestone_overrides: Dict[str, str] = {}
    with col_ms:
        st.subheader("Mark as Slipped")
        st.caption("Select any in-progress milestone to model as slipped.")
        slippable = [
            ms for ms in milestones if ms.status not in ("Complete", "Slipped")
        ]
        for ms in slippable:
            if st.checkbox(f"Wk {ms.due_week} — {ms.name}", key=f"slip_{ms.id}"):
                milestone_overrides[ms.id] = "Slipped"

    raid_overrides: Dict[str, str] = {}
    with col_risk:
        st.subheader("Re-Open Resolved Risk or Issue")
        st.caption("Select any resolved item to model as re-opened.")
        reopenable = [
            r
            for r in raid_items
            if r.status != "Open" and r.category in ("Risk", "Issue")
        ]
        for risk in reopenable:
            if st.checkbox(f"[{risk.severity}] {risk.title}", key=f"reopen_{risk.id}"):
                raid_overrides[risk.id] = "Open"

    st.divider()

    sim_milestones = [
        replace(ms, status=milestone_overrides.get(ms.id, ms.status))
        for ms in milestones
    ]
    sim_raids = [
        replace(r, status=raid_overrides.get(r.id, r.status))
        for r in raid_items
    ]

    scenario = compute_readiness(workstreams, sim_milestones, sim_raids, checklist_items)
    scenario_score = scenario["overall"]
    delta = round(scenario_score - baseline_score, 1)

    _render_scenario_result(baseline, scenario, delta)
    _render_scenario_summary(milestones, raid_items, milestone_overrides, raid_overrides)


def _render_scenario_result(baseline: Dict, scenario: Dict, delta: float) -> None:
    baseline_score = baseline["overall"]
    scenario_score = scenario["overall"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Baseline", f"{baseline_score}%")
    col2.metric(
        "Scenario",
        f"{scenario_score}%",
        delta=f"{delta:+.1f}%",
        delta_color="normal",
    )
    col3.metric(
        "Status",
        readiness_rag(scenario_score),
        delta=(
            None
            if readiness_rag(scenario_score) == readiness_rag(baseline_score)
            else f"{readiness_rag(baseline_score)} → {readiness_rag(scenario_score)}"
        ),
        delta_color="inverse",
    )

    st.divider()
    st.subheader("Score Impact by Component")

    rows = []
    for component, base_val in baseline["breakdown"].items():
        sim_val = scenario["breakdown"][component]
        d = round(sim_val - base_val, 1)
        rows.append(
            {
                "Component": component,
                "Baseline": f"{base_val}%",
                "Scenario": f"{sim_val}%",
                "Delta": f"{d:+.1f}%",
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _render_scenario_summary(
    milestones: List[Milestone],
    raid_items: List[RAIDItem],
    milestone_overrides: Dict,
    raid_overrides: Dict,
) -> None:
    if not milestone_overrides and not raid_overrides:
        return

    st.divider()
    st.subheader("Scenario Summary")

    if milestone_overrides:
        slipped_names = [ms.name for ms in milestones if ms.id in milestone_overrides]
        st.warning(f"**Modelled as Slipped:** {', '.join(slipped_names)}")

    if raid_overrides:
        reopened = [r.title for r in raid_items if r.id in raid_overrides]
        st.warning(f"**Modelled as Re-opened:** {', '.join(reopened)}")
