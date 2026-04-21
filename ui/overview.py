from typing import Dict, List

import streamlit as st

from models.checklist import ChecklistItem
from models.milestone import Milestone
from models.raid import RAIDItem
from models.workstream import Workstream
from scoring.readiness import SEVERITY_DEDUCTIONS, get_resolution_impacts
from utils.helpers import readiness_color, readiness_label

GO_THRESHOLD = 80.0


def render(
    workstreams: List[Workstream],
    milestones: List[Milestone],
    raid_items: List[RAIDItem],
    checklist_items: List[ChecklistItem],
    readiness: Dict,
    history: Dict = None,
) -> None:
    st.title("Executive Overview")
    st.caption("Meridian Health System — Patient Acquisition & Growth Agent · Week 4 of 8")

    impacts = get_resolution_impacts(workstreams, milestones, raid_items, checklist_items)

    _render_score_hero(readiness, history)
    st.divider()
    _render_launch_decision(readiness, checklist_items, impacts)
    st.divider()
    _render_score_breakdown(readiness, history)
    st.divider()
    _render_status_drivers(workstreams, milestones, raid_items, checklist_items, readiness)
    st.divider()
    _render_summary_metrics(workstreams, milestones, raid_items, checklist_items)
    st.divider()
    _render_resolution_impacts(readiness, impacts)
    if history:
        st.divider()
        _render_what_changed(history)
    st.divider()
    _render_open_blockers(workstreams)


def _render_score_hero(readiness: Dict, history: Dict = None) -> None:
    score = readiness["overall"]
    color = readiness_color(score)
    label = readiness_label(score)

    delta_html = ""
    if history:
        prev = history["scores"]["overall"]
        delta = round(score - prev, 1)
        sign = "+" if delta >= 0 else ""
        delta_color = "#16A34A" if delta >= 0 else "#DC2626"
        delta_html = (
            f'<div style="font-size:15px;color:{delta_color};margin-top:6px;font-weight:600">'
            f"{sign}{delta}% since Week {history['week']}"
            f"</div>"
        )

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(
            f"""
            <div style="
                text-align:center;padding:36px 24px;
                background:#f8fafc;border-radius:16px;
                border:2px solid {color};
            ">
                <div style="font-size:80px;font-weight:800;color:{color};line-height:1">{score}%</div>
                <div style="font-size:20px;font-weight:700;color:{color};margin-top:10px">{label}</div>
                {delta_html}
                <div style="font-size:13px;color:#6b7280;margin-top:6px">
                    Weighted launch readiness — recomputed from live delivery data · April 20, 2026
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_launch_decision(
    readiness: Dict,
    checklist_items: List[ChecklistItem],
    impacts: List[Dict],
) -> None:
    score = readiness["overall"]
    gap = round(GO_THRESHOLD - score, 1)
    failing = [c for c in checklist_items if c.status == "Fail"]
    pending = [c for c in checklist_items if c.status == "Pending"]
    is_go = score >= GO_THRESHOLD and not failing and not readiness.get("critical_fail")

    verdict_color = "#16A34A" if is_go else "#DC2626"
    verdict_text = "GO" if is_go else "NO-GO"

    st.markdown(
        f"""
        <div style="
            background:#fafafa;border:1px solid #e5e7eb;
            border-left:5px solid {verdict_color};
            border-radius:8px;padding:18px 22px;
        ">
            <span style="font-size:20px;font-weight:800;color:{verdict_color}">
                LAUNCH DECISION: {verdict_text}
            </span>
            <span style="font-size:13px;color:#6b7280;margin-left:16px">
                Score: {score}% · GO threshold: {GO_THRESHOLD}% · Gap: {gap} pts
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not is_go:
        st.markdown("**Blocking conditions:**")
        if score < GO_THRESHOLD:
            st.markdown(
                f"- Score **{score}%** — {gap} points below GO threshold of **{GO_THRESHOLD}%**"
            )
        for item in failing:
            st.markdown(
                f"- **{item.item}** [{item.category}] — gate failure, blocks launch"
            )
        if readiness.get("critical_fail"):
            st.markdown(
                "- Critical Compliance, Legal, or Clinical Safety gate failing — "
                "launch blocked regardless of overall score"
            )
        if pending:
            st.markdown(
                f"- **{len(pending)} criteria pending** — all must reach Pass before "
                "a Go decision can be issued"
            )

        top_actions = [i for i in impacts if i["delta"] >= 0.5][:3]
        if top_actions:
            st.markdown("**Path to GO:**")
            for rank, action in enumerate(top_actions, 1):
                flag = "  — *removes active NO-GO block*" if action["no_go_block"] else ""
                st.markdown(
                    f"{rank}. **{action['label']}** `{action['category']}` "
                    f"→ **+{action['delta']}%**{flag}"
                )
            cumulative = round(sum(i["delta"] for i in top_actions), 1)
            projected = round(min(score + cumulative, 100.0), 1)
            st.caption(
                f"These 3 actions add {cumulative} pts — projected score: **{projected}%**"
            )


def _render_status_drivers(
    workstreams: List[Workstream],
    milestones: List[Milestone],
    raid_items: List[RAIDItem],
    checklist_items: List[ChecklistItem],
    readiness: Dict,
) -> None:
    st.subheader("Status Drivers")
    st.caption(
        "The factors most directly responsible for the current readiness position."
    )

    drivers = []

    at_risk_ws = [ws for ws in workstreams if ws.status in ("At Risk", "Blocked")]
    ws_score = readiness["breakdown"]["Workstream Health"]
    if at_risk_ws:
        drag_names = ", ".join(
            ws.name
            for ws in sorted(at_risk_ws, key=lambda w: w.effective_progress())[:2]
        )
        drivers.append(
            f"{len(at_risk_ws)} workstreams at risk pull workstream health to **{ws_score}%**. "
            f"Primary drag: {drag_names}."
        )

    slipped = [ms for ms in milestones if ms.status == "Slipped"]
    at_risk_ms = [ms for ms in milestones if ms.status == "At Risk"]
    ms_score = readiness["breakdown"]["Milestone Completion"]
    if slipped or at_risk_ms:
        cascade = [ms for ms in at_risk_ms if ms.has_prerequisites()]
        cascade_note = (
            f" {len(cascade)} dependent milestone(s) at risk downstream." if cascade else ""
        )
        drivers.append(
            f"{len(slipped)} slipped + {len(at_risk_ms)} at-risk milestone(s) bring "
            f"milestone completion to **{ms_score}%**.{cascade_note}"
        )

    open_scoring = [
        r
        for r in raid_items
        if r.status == "Open"
        and r.category in ("Risk", "Issue")
        and r.severity in ("Critical", "High")
    ]
    raid_score = readiness["breakdown"]["RAID Risk Score"]
    if open_scoring:
        total_ded = sum(SEVERITY_DEDUCTIONS.get(r.severity, 0) for r in open_scoring)
        drivers.append(
            f"{len(open_scoring)} open Critical/High item(s) deducting **{total_ded} pts** "
            f"from RAID — component at **{raid_score}%**."
        )

    failing = [c for c in checklist_items if c.status == "Fail"]
    pending = [c for c in checklist_items if c.status == "Pending"]
    ck_score = readiness["breakdown"]["Go/No-Go Readiness"]
    if failing:
        gate_names = "; ".join(c.item[:55] for c in failing[:2])
        drivers.append(
            f"{len(failing)} gate failure(s) — *{gate_names}* — active NO-GO condition "
            f"independent of score. {len(pending)} further criteria pending."
        )
    elif pending:
        drivers.append(
            f"{len(pending)} criteria pending sign-off. Go/No-Go readiness at **{ck_score}%** — "
            "no failures, but launch cannot be confirmed until all are resolved."
        )

    for d in drivers:
        st.markdown(f"- {d}")


def _render_score_breakdown(readiness: Dict, history: Dict = None) -> None:
    st.subheader("Score Composition")
    st.caption(
        "Workstream Health (30%) · Milestone Completion (25%) · "
        "RAID Risk Score (20%) · Go/No-Go Readiness (25%)"
    )

    weight_map = {
        "Workstream Health": readiness["weights"]["workstream"],
        "Milestone Completion": readiness["weights"]["milestone"],
        "RAID Risk Score": readiness["weights"]["raid"],
        "Go/No-Go Readiness": readiness["weights"]["checklist"],
    }
    component_notes = {
        "Workstream Health": "3 workstreams At Risk; progress dampened in scoring",
        "Milestone Completion": "1 slipped + 3 at-risk of 12 milestones",
        "RAID Risk Score": "2 High risks + 1 High issue open; deducting 19 pts",
        "Go/No-Go Readiness": "1 gate failing; 4 pending sign-off",
    }
    history_key_map = {
        "Workstream Health": "workstream",
        "Milestone Completion": "milestone",
        "RAID Risk Score": "raid",
        "Go/No-Go Readiness": "checklist",
    }

    cols = st.columns(4)
    for i, (label, component_score) in enumerate(readiness["breakdown"].items()):
        weight_pct = int(weight_map[label] * 100)
        color = readiness_color(component_score)
        note = component_notes.get(label, "")

        delta_html = ""
        if history:
            prev = history["scores"].get(history_key_map.get(label, ""), component_score)
            d = round(component_score - prev, 1)
            sign = "+" if d >= 0 else ""
            d_color = "#16A34A" if d >= 0 else "#DC2626"
            delta_html = (
                f'<div style="font-size:11px;color:{d_color};font-weight:600">'
                f"{sign}{d}% vs Wk {history['week']}</div>"
            )

        with cols[i]:
            st.markdown(
                f"""
                <div style="
                    text-align:center;padding:16px 8px;
                    background:#f8fafc;border-radius:12px;
                    border-left:4px solid {color};
                ">
                    <div style="font-size:32px;font-weight:700;color:{color}">{component_score}%</div>
                    <div style="font-size:12px;font-weight:600;color:#374151;margin-top:4px">{label}</div>
                    <div style="font-size:11px;color:#9ca3af">{weight_pct}% weight</div>
                    {delta_html}
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption(note)


def _render_summary_metrics(
    workstreams, milestones, raid_items, checklist_items
) -> None:
    st.subheader("Delivery State")

    col1, col2, col3, col4, col5 = st.columns(5)

    at_risk_ws = sum(1 for ws in workstreams if ws.status == "At Risk")
    blocked = sum(1 for ws in workstreams if ws.status == "Blocked")
    slipped = sum(1 for ms in milestones if ms.status == "Slipped")
    open_critical = sum(
        1 for r in raid_items if r.status == "Open" and r.severity == "Critical"
    )
    checklist_pass = sum(1 for c in checklist_items if c.status == "Pass")
    checklist_fail = sum(1 for c in checklist_items if c.status == "Fail")

    col1.metric("At-Risk Workstreams", at_risk_ws)
    col2.metric("Blocked Workstreams", blocked)
    col3.metric("Slipped Milestones", slipped)
    col4.metric("Open Critical Risks", open_critical)
    col5.metric(
        "Go/No-Go Gate",
        f"{checklist_pass}/{len(checklist_items)} Pass",
        delta=f"-{checklist_fail} Fail" if checklist_fail else None,
        delta_color="inverse",
    )


def _render_resolution_impacts(readiness: Dict, impacts: List[Dict]) -> None:
    if not impacts:
        return

    st.subheader("Highest-Impact Actions")
    st.caption(
        "Each item re-runs the scoring model with one change applied. "
        "Items marked [NO-GO] are gate failures — resolving them removes the launch block "
        "in addition to adding score points."
    )

    for item in impacts[:9]:
        col_flag, col_content, col_delta = st.columns([0.4, 5.5, 1.1])

        with col_flag:
            if item["no_go_block"]:
                st.markdown("**[!]**")
            elif item["severity"] in ("Critical", "High"):
                st.markdown("▲")
            else:
                st.markdown("△")

        with col_content:
            no_go_tag = " `[NO-GO]`" if item["no_go_block"] else ""
            st.markdown(f"**{item['label']}**{no_go_tag}")
            st.caption(f"`{item['category']}` — {item['action']}")

        with col_delta:
            st.markdown(
                f"<div style='text-align:right;font-weight:700;color:#16A34A;font-size:15px'>"
                f"+{item['delta']}%</div>",
                unsafe_allow_html=True,
            )

    total_recoverable = round(sum(i["delta"] for i in impacts), 1)
    projected = round(min(readiness["overall"] + total_recoverable, 100.0), 1)
    st.caption(
        f"All open items resolved: projected readiness **~{projected}%** "
        f"(+{total_recoverable} pts from current {readiness['overall']}%)"
    )


def _render_what_changed(history: Dict) -> None:
    with st.expander(f"Changes Since Week {history['week']}", expanded=False):
        for event in history.get("events", []):
            is_negative = any(
                w in event for w in ("Slipped", "Fail", "delayed", "blocked")
            )
            prefix = "−" if is_negative else "+"
            st.markdown(f"{prefix} {event}")


def _render_open_blockers(workstreams: List[Workstream]) -> None:
    blockers = [ws for ws in workstreams if ws.blocker]
    if not blockers:
        return

    st.subheader("Open Blockers")
    for ws in blockers:
        st.warning(f"**{ws.name}** — {ws.blocker}  *(Owner: {ws.owner})*")
