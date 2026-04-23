from dataclasses import dataclass
from typing import Dict, List

from models.checklist import ChecklistItem
from models.milestone import Milestone
from models.raid import RAIDItem
from models.workstream import Workstream
from scoring.readiness import compute_readiness, get_resolution_impacts


_SEVERITY_POINTS: Dict[str, int] = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
}

_URGENCY_POINTS: Dict[str, int] = {
    "Immediate": 4,
    "This Week": 3,
    "This Sprint": 2,
    "Monitor": 1,
}

_WORKSTREAM_ACTIONS: Dict[str, str] = {
    "AI Model Development": "Run fairness retraining sprint and publish updated model card with cohort recall deltas.",
    "EHR Integration": "Escalate credential unblock and pair integration team with Epic liaison for daily defect burn-down.",
    "Patient Journey Automation": "Close unresolved touchpoints in a facilitated workshop and freeze automation trigger contract.",
}


@dataclass
class GrowthAction:
    title: str
    owner: str
    domain: str
    reason: str
    expected_delta: float
    priority_score: float
    urgency: str
    no_go_block: bool
    execution_note: str


def _build_owner_lookup(
    workstreams: List[Workstream],
    milestones: List[Milestone],
    raid_items: List[RAIDItem],
    checklist: List[ChecklistItem],
) -> Dict[str, Dict[str, str]]:
    lookup: Dict[str, Dict[str, str]] = {}

    for ws in workstreams:
        lookup[ws.name] = {
            "owner": ws.owner,
            "urgency": "This Week" if ws.status == "Blocked" else "This Sprint",
            "severity": ws.priority,
            "note": _WORKSTREAM_ACTIONS.get(
                ws.name,
                "Stabilize execution plan, remove blocker, and return this workstream to On Track.",
            ),
        }

    for ms in milestones:
        urgency = "Immediate" if ms.status == "Slipped" else "This Week"
        severity = "High" if ms.status == "Slipped" else "Medium"
        lookup[ms.name] = {
            "owner": ms.owner,
            "urgency": urgency,
            "severity": severity,
            "note": "Recover schedule, protect downstream dependencies, and confirm revised date with impacted owners.",
        }

    for item in raid_items:
        lookup[item.title] = {
            "owner": item.owner,
            "urgency": item.urgency,
            "severity": item.severity,
            "note": item.mitigation,
        }

    for ck in checklist:
        lookup[ck.item] = {
            "owner": ck.owner,
            "urgency": "Immediate" if ck.status == "Fail" else "This Week",
            "severity": "Critical" if ck.status == "Fail" else "High",
            "note": f"Collect evidence and move gate from {ck.status} to Pass.",
        }

    return lookup


def _priority_score(delta: float, severity: str, urgency: str, no_go_block: bool) -> float:
    base = delta * 40
    severity_boost = _SEVERITY_POINTS.get(severity, 2) * 9
    urgency_boost = _URGENCY_POINTS.get(urgency, 2) * 7
    no_go_boost = 25 if no_go_block else 0
    return round(base + severity_boost + urgency_boost + no_go_boost, 1)


def build_growth_actions(
    workstreams: List[Workstream],
    milestones: List[Milestone],
    raid_items: List[RAIDItem],
    checklist: List[ChecklistItem],
) -> List[GrowthAction]:
    impacts = get_resolution_impacts(workstreams, milestones, raid_items, checklist)
    owner_lookup = _build_owner_lookup(workstreams, milestones, raid_items, checklist)

    actions: List[GrowthAction] = []
    for impact in impacts:
        meta = owner_lookup.get(
            impact["label"],
            {
                "owner": "Program Manager",
                "urgency": "This Week",
                "severity": impact.get("severity", "Medium"),
                "note": impact["action"],
            },
        )
        score = _priority_score(
            impact["delta"],
            meta["severity"],
            meta["urgency"],
            impact["no_go_block"],
        )
        actions.append(
            GrowthAction(
                title=impact["label"],
                owner=meta["owner"],
                domain=impact["category"],
                reason=impact["action"],
                expected_delta=impact["delta"],
                priority_score=score,
                urgency=meta["urgency"],
                no_go_block=impact["no_go_block"],
                execution_note=meta["note"],
            )
        )

    return sorted(
        actions,
        key=lambda action: (0 if action.no_go_block else 1, -action.priority_score),
    )


def summarize_agent_brief(
    workstreams: List[Workstream],
    milestones: List[Milestone],
    raid_items: List[RAIDItem],
    checklist: List[ChecklistItem],
) -> Dict[str, object]:
    readiness = compute_readiness(workstreams, milestones, raid_items, checklist)
    actions = build_growth_actions(workstreams, milestones, raid_items, checklist)

    top_actions = actions[:5]
    projected = round(
        min(readiness["overall"] + sum(action.expected_delta for action in top_actions), 100.0), 1
    )
    no_go_actions = [a for a in top_actions if a.no_go_block]

    return {
        "readiness": readiness,
        "top_actions": top_actions,
        "projected_score_after_top_actions": projected,
        "no_go_actions_count": len(no_go_actions),
        "owner_queue": _owner_queue(top_actions),
        "command_rhythm": _command_rhythm(),
        "trigger_matrix": _trigger_matrix(),
    }


def _owner_queue(actions: List[GrowthAction]) -> Dict[str, List[GrowthAction]]:
    queue: Dict[str, List[GrowthAction]] = {}
    for action in actions:
        queue.setdefault(action.owner, []).append(action)
    return queue


def _command_rhythm() -> List[Dict[str, str]]:
    return [
        {
            "cadence": "Daily 08:30",
            "forum": "Stabilization huddle",
            "objective": "Review top blockers, assign owners, and lock 24-hour commitments.",
        },
        {
            "cadence": "Daily 16:00",
            "forum": "Dependency burn-down",
            "objective": "Check milestone chain impacts and trigger escalations if ETA slips.",
        },
        {
            "cadence": "Weekly Monday",
            "forum": "Clinical + technical control tower",
            "objective": "Validate fairness, adoption, and reliability signals before they become launch blockers.",
        },
        {
            "cadence": "Bi-weekly",
            "forum": "Steering committee",
            "objective": "Approve trade-offs, unlock cross-functional dependencies, and govern go/no-go trajectory.",
        },
    ]


def _trigger_matrix() -> List[Dict[str, str]]:
    return [
        {
            "signal": "Any Compliance / Legal / Clinical Safety checklist item = Fail",
            "action": "Initiate red-path escalation, assign executive owner, and run same-day remediation standup.",
            "sla": "4 hours",
        },
        {
            "signal": "EHR sync error rate > 0.5% or failed recommendations > 2%",
            "action": "Freeze non-critical feature work and prioritize integration defect triage.",
            "sla": "24 hours",
        },
        {
            "signal": "Demographic recall gap > 8%",
            "action": "Run fairness retraining and require CMO sign-off before releasing updated model.",
            "sla": "48 hours",
        },
        {
            "signal": "AI recommendation acceptance rate < 50%",
            "action": "Launch adoption intervention: workflow shadowing, retraining, and override reason audit.",
            "sla": "5 days",
        },
    ]
