"""
Post-launch operational dashboard mockup.
Uses hardcoded 30-day pilot data — replace with live queries in production.
"""
import streamlit as st
import pandas as pd


_METRICS = {
    "model": [
        {"metric": "Overall AUC", "value": "0.84", "target": "≥ 0.85", "status": "At Risk", "note": "Slight drop from 0.87 baseline — monitoring"},
        {"metric": "Recall gap (Hispanic cohort)", "value": "9%", "target": "< 5%", "status": "Alert", "note": "Retraining job queued"},
        {"metric": "Recall gap (Black cohort)", "value": "4%", "target": "< 5%", "status": "Pass", "note": "Within threshold"},
        {"metric": "Feature drift score (PSI)", "value": "0.08", "target": "< 0.10", "status": "Pass", "note": "Stable"},
    ],
    "business": [
        {"metric": "Appointment conversion rate", "value": "+11%", "target": "+15%", "status": "At Risk", "note": "vs. pre-AI baseline"},
        {"metric": "Patient no-show rate", "value": "−17%", "target": "−20%", "status": "At Risk", "note": "Trending in right direction"},
        {"metric": "Time to first appointment", "value": "−1.8 days", "target": "−2 days", "status": "At Risk", "note": "Close to target"},
        {"metric": "Referral pipeline volume", "value": "+13%", "target": "+10%", "status": "Pass", "note": "Exceeding target"},
    ],
    "reliability": [
        {"metric": "API uptime", "value": "99.94%", "target": "≥ 99.9%", "status": "Pass", "note": "One 12-min outage, Wk 2"},
        {"metric": "Inference latency P95", "value": "1.8s", "target": "< 2.0s", "status": "Pass", "note": "Post-optimisation"},
        {"metric": "EHR sync error rate", "value": "0.3%", "target": "< 0.1%", "status": "Alert", "note": "Scheduling rule mismatch — investigation open"},
        {"metric": "Failed recommendations (EHR rejection)", "value": "2.1%", "target": "< 2%", "status": "Alert", "note": "Related to sync errors"},
    ],
    "adoption": [
        {"metric": "AI recommendation acceptance rate", "value": "61%", "target": "≥ 70%", "status": "At Risk", "note": "Low in Clinic B — change mgmt focus"},
        {"metric": "Active users / trained staff", "value": "78%", "target": "≥ 90%", "status": "At Risk", "note": "3 coordinators not yet active"},
        {"metric": "Override rate", "value": "24%", "target": "Track only", "status": "Watch", "note": "71% of overrides have documented reason"},
        {"metric": "Avg time per recommendation review", "value": "48s", "target": "Baseline TBD", "status": "Watch", "note": "Establishing baseline"},
    ],
}

_STATUS_EMOJI = {
    "Pass": "✅",
    "At Risk": "🟡",
    "Alert": "🔴",
    "Watch": "🔵",
}

_STATUS_COLOR = {
    "Pass": "#16A34A",
    "At Risk": "#D97706",
    "Alert": "#DC2626",
    "Watch": "#2563EB",
}


def render() -> None:
    st.title("Post-Launch Operational Dashboard")
    st.caption(
        "Meridian Health System · Patient Acquisition Agent · "
        "30-Day Pilot Review · May 20, 2026"
    )
    st.info(
        "**Mockup:** This page uses illustrative 30-day pilot data. "
        "In production, connect to the EHR analytics API and model monitoring service."
    )

    _render_health_summary()
    st.divider()
    _render_category("Model Performance", _METRICS["model"])
    st.divider()
    _render_category("Business Outcomes", _METRICS["business"])
    st.divider()
    _render_category("System Reliability", _METRICS["reliability"])
    st.divider()
    _render_category("Clinical Adoption", _METRICS["adoption"])
    st.divider()
    _render_top_concerns()


def _render_health_summary() -> None:
    all_metrics = [m for group in _METRICS.values() for m in group]
    counts = {s: sum(1 for m in all_metrics if m["status"] == s) for s in _STATUS_EMOJI}

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Metrics", len(all_metrics))
    col2.metric("✅ Pass", counts.get("Pass", 0))
    col3.metric("🟡 At Risk", counts.get("At Risk", 0))
    col4.metric("🔴 Alert", counts.get("Alert", 0))
    col5.metric("🔵 Watch", counts.get("Watch", 0))


def _render_category(title: str, metrics: list) -> None:
    st.subheader(title)
    rows = []
    for m in metrics:
        rows.append({
            "Status": f"{_STATUS_EMOJI[m['status']]} {m['status']}",
            "Metric": m["metric"],
            "Value": m["value"],
            "Target": m["target"],
            "Note": m["note"],
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _render_top_concerns() -> None:
    st.subheader("Needs Immediate Attention")
    st.caption("Items in Alert state at 30-day review — require remediation plan before 60-day review.")

    all_metrics = [m for group in _METRICS.values() for m in group]
    alerts = [m for m in all_metrics if m["status"] == "Alert"]

    for m in alerts:
        st.error(f"**{m['metric']}** — {m['value']} (target: {m['target']})  ·  {m['note']}")

    st.markdown("**Key judgment call at 30 days:**")
    st.markdown(
        "The EHR sync error rate (0.3%) and failed recommendation rate (2.1%) are related. "
        "Both trace to scheduling rule mismatches — slots the model recommends that the EHR "
        "rejects as unavailable. This was the integration risk flagged pre-launch. "
        "It needs an owner and a remediation timeline before coordinators lose confidence in the tool."
    )
