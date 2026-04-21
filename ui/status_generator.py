from datetime import date
from typing import Dict, List

import streamlit as st

from models.checklist import ChecklistItem
from models.milestone import Milestone
from models.raid import RAIDItem
from models.workstream import Workstream
from utils.helpers import readiness_label, readiness_rag


def render(
    workstreams: List[Workstream],
    milestones: List[Milestone],
    raid_items: List[RAIDItem],
    checklist_items: List[ChecklistItem],
    readiness: Dict,
) -> None:
    st.title("Client Status Update")
    st.caption(
        "Generates a structured weekly update from live delivery data. "
        "Review and adjust before sending."
    )

    col1, col2 = st.columns(2)
    with col1:
        current_week = st.number_input(
            "Current Delivery Week", min_value=1, max_value=12, value=4
        )
        program_manager = st.text_input("Program Manager", value="Sarah Okonkwo")
    with col2:
        report_date = st.date_input("Report Date", value=date.today())
        client_name = st.text_input(
            "Client / Hospital", value="Meridian Health System"
        )

    additional_notes = st.text_area(
        "Additional Notes / Context (optional)",
        placeholder="e.g., Executive sponsor confirmed budget for Phase 2 expansion...",
        height=80,
    )

    if st.button("Generate Client Update", type="primary", use_container_width=True):
        update_text = _build_update(
            workstreams,
            milestones,
            raid_items,
            readiness,
            current_week=int(current_week),
            pm=program_manager,
            report_date=report_date,
            client=client_name,
            notes=additional_notes,
        )
        st.divider()
        st.subheader("Generated Status Update")
        st.markdown(update_text)
        st.divider()
        st.code(update_text, language=None)
        st.caption("Copy the raw text above to paste into email, Confluence, or a client portal.")


def _build_update(
    workstreams: List[Workstream],
    milestones: List[Milestone],
    raid_items: List[RAIDItem],
    readiness: Dict,
    current_week: int,
    pm: str,
    report_date: date,
    client: str,
    notes: str,
) -> str:
    score = readiness["overall"]
    rag = readiness_rag(score)
    label = readiness_label(score)

    recently_completed = [ms for ms in milestones if ms.status == "Complete"][-3:]
    upcoming = [ms for ms in milestones if ms.due_week == current_week + 1]
    active_blockers = [ws for ws in workstreams if ws.blocker]
    open_critical_high = [
        r
        for r in raid_items
        if r.status == "Open" and r.severity in ("Critical", "High")
    ][:4]

    lines = [
        f"## WEEK {current_week} STATUS UPDATE — Patient Acquisition & Growth Agent",
        f"**Client:** {client}  |  **Prepared by:** {pm}  |  **Date:** {report_date.strftime('%B %d, %Y')}",
        "",
        f"**Overall Readiness: {score}%  ·  RAG Status: {rag}**",
        f"*{label}*",
        "",
        "---",
        "",
        "### This Week's Accomplishments",
    ]

    if recently_completed:
        for ms in recently_completed:
            lines.append(f"- ✅ {ms.name} *(Owner: {ms.owner})*")
    else:
        lines.append("- No milestones completed this week.")

    lines += ["", "### Active Blockers"]
    if active_blockers:
        for ws in active_blockers:
            lines.append(f"- 🔴 **{ws.name}:** {ws.blocker}")
    else:
        lines.append("- No active blockers this week.")

    lines += ["", "### Risks Requiring Stakeholder Attention"]
    if open_critical_high:
        for risk in open_critical_high:
            lines.append(
                f"- **[{risk.severity}]** {risk.title} "
                f"*(Owner: {risk.owner})* — {risk.mitigation}"
            )
    else:
        lines.append("- No Critical or High risks currently open.")

    lines += ["", "### Next Week Focus"]
    if upcoming:
        for ms in upcoming:
            lines.append(f"- 🎯 {ms.name} *(Owner: {ms.owner})*")
    else:
        lines.append("- Continue current sprint deliverables.")

    if notes.strip():
        lines += ["", "### Additional Notes"]
        lines.append(notes.strip())

    lines += [
        "",
        "---",
        f"*Next update: Week {current_week + 1}  |  Questions: contact {pm}*",
    ]

    return "\n".join(lines)
