from dataclasses import replace
from typing import Dict, List

from models.checklist import ChecklistItem
from models.milestone import Milestone
from models.raid import RAIDItem
from models.workstream import Workstream

# Contribution of each domain to the overall readiness score
WEIGHTS: Dict[str, float] = {
    "workstream": 0.30,
    "milestone": 0.25,
    "raid": 0.20,
    "checklist": 0.25,
}

# Point deductions per open Risk or Issue item, by severity
SEVERITY_DEDUCTIONS: Dict[str, int] = {
    "Critical": 15,
    "High": 8,
    "Medium": 3,
    "Low": 1,
}

# Failures in these categories block launch regardless of overall score
CRITICAL_CHECKLIST_CATEGORIES = {"Compliance", "Legal", "Clinical Safety"}

# Status-to-score mapping for milestones
_MILESTONE_STATUS_SCORES: Dict[str, float] = {
    "Complete": 1.0,
    "On Track": 0.8,
    "At Risk": 0.4,
    "Slipped": 0.0,
}


def score_workstreams(workstreams: List[Workstream]) -> float:
    if not workstreams:
        return 0.0
    return min(
        sum(ws.effective_progress() for ws in workstreams) / len(workstreams),
        100.0,
    )


def score_milestones(milestones: List[Milestone]) -> float:
    if not milestones:
        return 0.0
    total = sum(_MILESTONE_STATUS_SCORES.get(m.status, 0.5) for m in milestones)
    return (total / len(milestones)) * 100.0


def score_raid(raid_items: List[RAIDItem]) -> float:
    """
    Starts at 100 and deducts for every open Risk or Issue by severity.
    Assumptions and Dependencies are tracked for visibility but don't penalise the score.
    """
    score = 100.0
    for item in raid_items:
        if item.status == "Open" and item.category in ("Risk", "Issue"):
            score -= SEVERITY_DEDUCTIONS.get(item.severity, 0)
    return max(score, 0.0)


def score_checklist(items: List[ChecklistItem]) -> float:
    if not items:
        return 0.0
    passed = sum(1 for item in items if item.status == "Pass")
    return (passed / len(items)) * 100.0


def has_critical_fail(items: List[ChecklistItem]) -> bool:
    """True if any Compliance, Legal, or Clinical Safety item is failing."""
    return any(
        item.status == "Fail" and item.category in CRITICAL_CHECKLIST_CATEGORIES
        for item in items
    )


def compute_readiness(
    workstreams: List[Workstream],
    milestones: List[Milestone],
    raid_items: List[RAIDItem],
    checklist_items: List[ChecklistItem],
) -> Dict:
    ws_score = score_workstreams(workstreams)
    ms_score = score_milestones(milestones)
    raid_score = score_raid(raid_items)
    ck_score = score_checklist(checklist_items)

    overall = (
        ws_score * WEIGHTS["workstream"]
        + ms_score * WEIGHTS["milestone"]
        + raid_score * WEIGHTS["raid"]
        + ck_score * WEIGHTS["checklist"]
    )

    return {
        "overall": round(overall, 1),
        "breakdown": {
            "Workstream Health": round(ws_score, 1),
            "Milestone Completion": round(ms_score, 1),
            "RAID Risk Score": round(raid_score, 1),
            "Go/No-Go Readiness": round(ck_score, 1),
        },
        "weights": WEIGHTS,
        "critical_fail": has_critical_fail(checklist_items),
    }


def get_resolution_impacts(
    workstreams: List[Workstream],
    milestones: List[Milestone],
    raid_items: List[RAIDItem],
    checklist_items: List[ChecklistItem],
) -> List[Dict]:
    """
    For every item pulling the score down, compute the exact readiness gain
    by re-running compute_readiness with that one item resolved.
    Sorted: NO-GO blockers first, then by delta descending.
    """
    baseline = compute_readiness(workstreams, milestones, raid_items, checklist_items)["overall"]
    impacts = []

    for ws in workstreams:
        if ws.status in ("At Risk", "Blocked"):
            sim = [replace(w, status="On Track") if w.id == ws.id else w for w in workstreams]
            delta = round(
                compute_readiness(sim, milestones, raid_items, checklist_items)["overall"] - baseline, 1
            )
            if delta > 0:
                impacts.append({
                    "label": ws.name,
                    "category": "Workstream",
                    "action": f"Recover to On Track (currently {ws.status})",
                    "delta": delta,
                    "severity": ws.priority,
                    "no_go_block": False,
                })

    for ms in milestones:
        if ms.status in ("At Risk", "Slipped"):
            sim = [replace(m, status="On Track") if m.id == ms.id else m for m in milestones]
            delta = round(
                compute_readiness(workstreams, sim, raid_items, checklist_items)["overall"] - baseline, 1
            )
            if delta > 0:
                impacts.append({
                    "label": ms.name,
                    "category": f"Milestone — Wk {ms.due_week}",
                    "action": f"Recover to On Track (currently {ms.status})",
                    "delta": delta,
                    "severity": "High" if ms.status == "Slipped" else "Medium",
                    "no_go_block": False,
                })

    for item in raid_items:
        if item.status == "Open" and item.category in ("Risk", "Issue"):
            sim = [replace(r, status="Mitigated") if r.id == item.id else r for r in raid_items]
            delta = round(
                compute_readiness(workstreams, milestones, sim, checklist_items)["overall"] - baseline, 1
            )
            if delta > 0:
                impacts.append({
                    "label": item.title,
                    "category": f"{item.category} [{item.severity}]",
                    "action": f"Mitigate — {item.urgency}",
                    "delta": delta,
                    "severity": item.severity,
                    "no_go_block": False,
                })

    for ck in checklist_items:
        if ck.status in ("Fail", "Pending"):
            sim = [replace(c, status="Pass") if c.id == ck.id else c for c in checklist_items]
            delta = round(
                compute_readiness(workstreams, milestones, raid_items, sim)["overall"] - baseline, 1
            )
            if delta > 0:
                impacts.append({
                    "label": ck.item,
                    "category": f"Checklist [{ck.category}] — {ck.status}",
                    "action": "Resolve and mark Pass",
                    "delta": delta,
                    "severity": "Critical" if ck.status == "Fail" else "Medium",
                    "no_go_block": ck.status == "Fail",
                })

    return sorted(impacts, key=lambda x: (0 if x["no_go_block"] else 1, -x["delta"]))
