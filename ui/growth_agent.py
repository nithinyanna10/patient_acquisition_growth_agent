from typing import List

import pandas as pd
import streamlit as st

from models.checklist import ChecklistItem
from models.milestone import Milestone
from models.raid import RAIDItem
from models.workstream import Workstream
from scoring.growth_agent import GrowthAction, summarize_agent_brief


def render(
    workstreams: List[Workstream],
    milestones: List[Milestone],
    raid_items: List[RAIDItem],
    checklist: List[ChecklistItem],
) -> None:
    brief = summarize_agent_brief(workstreams, milestones, raid_items, checklist)

    st.title("Patient Acquisition Growth Agent")
    st.caption(
        "Autonomous launch-control copilot: prioritizes interventions, assigns owners, and triggers escalation logic."
    )

    _render_hero(brief)
    st.divider()
    _render_priority_backlog(brief["top_actions"])
    st.divider()
    _render_owner_queues(brief["owner_queue"])
    st.divider()
    _render_trigger_matrix(brief["trigger_matrix"])
    st.divider()
    _render_command_rhythm(brief["command_rhythm"])


def _render_hero(brief: dict) -> None:
    readiness = brief["readiness"]["overall"]
    projected = brief["projected_score_after_top_actions"]
    no_go_count = brief["no_go_actions_count"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Readiness", f"{readiness}%")
    col2.metric("Projected (Top 5 Actions)", f"{projected}%")
    col3.metric("Top-5 NO-GO Block Removals", no_go_count)

    st.info(
        "The agent prioritizes by combined impact score: expected readiness delta, severity, urgency, and launch-blocking status."
    )


def _render_priority_backlog(actions: List[GrowthAction]) -> None:
    st.subheader("72-Hour Action Backlog")
    rows = []
    for idx, action in enumerate(actions, start=1):
        rows.append(
            {
                "Rank": idx,
                "Action": action.title,
                "Owner": action.owner,
                "Domain": action.domain,
                "Urgency": action.urgency,
                "Expected Readiness Gain": f"+{action.expected_delta}%",
                "Priority Score": action.priority_score,
                "NO-GO Block": "Yes" if action.no_go_block else "No",
                "Execution Note": action.execution_note,
            }
        )

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _render_owner_queues(owner_queue: dict) -> None:
    st.subheader("Owner Command Queues")
    st.caption("Each owner receives a focused execution queue with the highest impact interventions first.")

    for owner, actions in owner_queue.items():
        with st.expander(f"{owner} · {len(actions)} assigned action(s)", expanded=False):
            for action in actions:
                no_go = " `[NO-GO]`" if action.no_go_block else ""
                st.markdown(
                    f"- **{action.title}**{no_go} · {action.domain} · {action.urgency} · +{action.expected_delta}%"
                )
                st.caption(action.execution_note)


def _render_trigger_matrix(triggers: list) -> None:
    st.subheader("Autonomous Escalation Triggers")
    st.caption("When a threshold is breached, the agent promotes incident mode with predefined response SLAs.")

    st.dataframe(
        pd.DataFrame(
            [
                {"Signal": row["signal"], "Action": row["action"], "Response SLA": row["sla"]}
                for row in triggers
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )


def _render_command_rhythm(rhythm: list) -> None:
    st.subheader("Operating Rhythm")
    st.caption("Cadence the agent uses to keep delivery pressure high and risk transparent.")

    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Cadence": item["cadence"],
                    "Forum": item["forum"],
                    "Objective": item["objective"],
                }
                for item in rhythm
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )
