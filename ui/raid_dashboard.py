from typing import List

import streamlit as st

from models.raid import RAIDItem
from utils.helpers import SEVERITY_COLORS

_SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
_URGENCY_ORDER = {"Immediate": 0, "This Week": 1, "This Sprint": 2, "Monitor": 3}


def render(raid_items: List[RAIDItem]) -> None:
    st.title("RAID Log")
    st.caption(
        "Open Risks and Issues reduce the readiness score. "
        "Assumptions and Dependencies are tracked but do not affect scoring."
    )

    _render_raid_summary(raid_items)
    st.divider()

    tab_r, tab_i, tab_a, tab_d = st.tabs(["Risks", "Issues", "Assumptions", "Dependencies"])

    for tab, category in zip(
        [tab_r, tab_i, tab_a, tab_d],
        ["Risk", "Issue", "Assumption", "Dependency"],
    ):
        subset = [r for r in raid_items if r.category == category]
        with tab:
            _render_category(subset, category)


def _render_raid_summary(raid_items: List[RAIDItem]) -> None:
    open_items = [r for r in raid_items if r.status == "Open"]
    open_critical = [r for r in open_items if r.severity == "Critical"]
    open_high = [r for r in open_items if r.severity == "High"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Items", len(raid_items))
    col2.metric("Open", len(open_items))
    col3.metric("Open Critical", len(open_critical))
    col4.metric("Open High", len(open_high))


def _render_category(items: List[RAIDItem], category: str) -> None:
    if not items:
        st.info(f"No {category.lower()} items recorded.")
        return

    open_items = [r for r in items if r.status == "Open"]
    resolved = [r for r in items if r.status != "Open"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total", len(items))
    col2.metric("Open", len(open_items))
    col3.metric("Resolved", len(resolved))

    st.divider()

    sorted_items = sorted(
        items,
        key=lambda r: (
            0 if r.status == "Open" else 1,
            _SEVERITY_ORDER.get(r.severity, 99),
            _URGENCY_ORDER.get(r.urgency, 99),
        ),
    )
    for item in sorted_items:
        _render_item_card(item)


def _render_item_card(item: RAIDItem) -> None:
    is_open = item.status == "Open"
    color = SEVERITY_COLORS.get(item.severity, "#6b7280")

    status_label = "Open" if is_open else item.status
    auto_expand = is_open and item.severity in ("Critical", "High")
    label = f"[{item.severity}]  {item.title}  —  {status_label}"

    with st.expander(label, expanded=auto_expand):
        col_main, col_meta = st.columns([3, 1])

        with col_main:
            st.markdown(f"**Context:** {item.description}")
            st.markdown(f"**Response:** {item.mitigation}")

        with col_meta:
            severity_html = (
                f'<span style="'
                f"background:{color};color:white;"
                f'padding:2px 10px;border-radius:10px;font-size:12px;font-weight:600">'
                f"{item.severity}</span>"
            )
            st.markdown(severity_html, unsafe_allow_html=True)
            st.markdown(f"**Urgency:** {item.urgency}")
            st.markdown(f"**Owner:** {item.owner}")
            st.markdown(f"**Status:** `{item.status}`")
