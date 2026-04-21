from typing import List

import streamlit as st

from models.workstream import Workstream
from utils.helpers import STATUS_EMOJI


def render(workstreams: List[Workstream]) -> None:
    st.title("Workstream Health")
    st.caption(
        "Progress across all delivery workstreams. "
        "At Risk workstreams score at 70% of reported progress; Blocked at 40%. "
        "This dampening flows directly into the overall readiness score."
    )

    statuses = sorted({ws.status for ws in workstreams})
    selected = st.multiselect("Filter by Status", statuses, default=statuses, key="ws_filter")
    filtered = [ws for ws in workstreams if ws.status in selected]

    st.divider()
    _render_status_summary(workstreams)
    st.divider()

    for ws in filtered:
        _render_workstream_card(ws)


def _render_status_summary(workstreams: List[Workstream]) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("On Track", sum(1 for ws in workstreams if ws.status == "On Track"))
    col2.metric("At Risk", sum(1 for ws in workstreams if ws.status == "At Risk"))
    col3.metric("Blocked", sum(1 for ws in workstreams if ws.status == "Blocked"))
    col4.metric("Complete", sum(1 for ws in workstreams if ws.status == "Complete"))


def _render_workstream_card(ws: Workstream) -> None:
    status_icon = STATUS_EMOJI.get(ws.status, "")
    auto_expand = ws.status in ("Blocked", "At Risk")

    with st.expander(
        f"{status_icon} **{ws.name}** — {ws.owner}  ·  {ws.priority}",
        expanded=auto_expand,
    ):
        col_left, col_right = st.columns([3, 1])

        with col_left:
            st.progress(
                ws.progress / 100,
                text=f"Reported progress: {ws.progress}%",
            )
            eff = ws.effective_progress()
            multiplier_note = {
                "At Risk": "scored at 70% of reported progress (At Risk multiplier)",
                "Blocked": "scored at 40% of reported progress (Blocked multiplier)",
                "On Track": "full reported progress applied",
                "Complete": "full reported progress applied",
            }.get(ws.status, "")
            st.caption(f"Score contribution: **{eff:.0f}%** — {multiplier_note}")

            if ws.blocker:
                st.error(f"**Blocking issue:** {ws.blocker}")

        with col_right:
            st.markdown(f"**Status:** {ws.status}")
            st.markdown(f"**Priority:** {ws.priority}")
            st.markdown(f"**Owner:** {ws.owner}")
