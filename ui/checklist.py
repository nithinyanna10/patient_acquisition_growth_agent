from typing import List

import streamlit as st

from models.checklist import ChecklistItem
from scoring.readiness import CRITICAL_CHECKLIST_CATEGORIES, has_critical_fail


def render(checklist_items: List[ChecklistItem]) -> None:
    st.title("Go / No-Go Checklist")
    st.caption(
        "All criteria must pass before a Go decision can be issued. "
        "A single failure in Compliance, Legal, or Clinical Safety blocks launch regardless of overall score."
    )

    _render_verdict(checklist_items)
    st.divider()
    _render_pass_fail_summary(checklist_items)
    st.divider()
    _render_items_by_category(checklist_items)


def _render_verdict(checklist_items: List[ChecklistItem]) -> None:
    critical_blocked = has_critical_fail(checklist_items)
    failed = [c for c in checklist_items if c.status == "Fail"]
    pending = [c for c in checklist_items if c.status == "Pending"]

    if critical_blocked:
        st.error(
            "**NO-GO — LAUNCH BLOCKED.** "
            "A critical compliance, legal, or clinical safety gate is failing. "
            "Score is not a factor until this is resolved."
        )
    elif failed:
        st.error(
            f"**NO-GO.** {len(failed)} gate(s) failing — "
            "all must be resolved before a launch decision can be issued."
        )
    elif pending:
        st.warning(
            f"**PENDING.** {len(pending)} item(s) in progress. "
            "Launch readiness cannot be confirmed until all criteria are resolved."
        )
    else:
        st.success("**GO.** All criteria passed. System is cleared for launch.")


def _render_pass_fail_summary(checklist_items: List[ChecklistItem]) -> None:
    passed = sum(1 for c in checklist_items if c.status == "Pass")
    failed = sum(1 for c in checklist_items if c.status == "Fail")
    pending = sum(1 for c in checklist_items if c.status == "Pending")
    total = len(checklist_items)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Criteria", total)
    col2.metric("Pass", passed)
    col3.metric("Fail", failed)
    col4.metric("Pending", pending)


def _render_items_by_category(checklist_items: List[ChecklistItem]) -> None:
    categories = sorted({c.category for c in checklist_items})

    for cat in categories:
        cat_items = [c for c in checklist_items if c.category == cat]
        is_critical = cat in CRITICAL_CHECKLIST_CATEGORIES

        gate_tag = "  `[launch-blocking gate]`" if is_critical else ""
        st.subheader(f"{cat}{gate_tag}")

        for item in cat_items:
            _render_item_row(item)

        st.divider()


def _render_item_row(item: ChecklistItem) -> None:
    status_labels = {"Pass": "Pass", "Fail": "FAIL", "Pending": "Pending"}
    status_colors = {"Pass": "#16A34A", "Fail": "#DC2626", "Pending": "#D97706"}
    icon = {"Pass": "✓", "Fail": "✗", "Pending": "○"}.get(item.status, "?")
    color = status_colors.get(item.status, "#6b7280")

    col_status, col_item, col_owner, col_evidence = st.columns([0.5, 3, 1, 2])

    with col_status:
        st.markdown(
            f'<span style="color:{color};font-weight:700;font-size:16px">{icon}</span>',
            unsafe_allow_html=True,
        )

    with col_item:
        st.markdown(item.item)

    with col_owner:
        st.caption(f"{item.owner}")

    with col_evidence:
        if item.evidence:
            st.caption(f"_{item.evidence}_")
