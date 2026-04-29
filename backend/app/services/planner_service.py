from datetime import datetime

from app.schemas import PlannerResponse, PlannerStep
from app.services.growth_agent_service import get_growth_brief


def build_execution_plan(db, objective: str, horizon_days: int) -> PlannerResponse:
    brief = get_growth_brief(db)
    actions = brief["top_actions"][: min(8, max(3, horizon_days // 2))]
    policy_checks = [
        "No unresolved Compliance/Legal/Clinical Safety failures before go-live.",
        "Fairness recall gap must be within approved threshold.",
        "EHR integration error rates must remain below SLO.",
    ]

    steps: list[PlannerStep] = []
    for idx, action in enumerate(actions, start=1):
        due_in_days = min(horizon_days, idx * 2)
        title = action["title"] if isinstance(action, dict) else action.title
        note = action["execution_note"] if isinstance(action, dict) else action.execution_note
        owner = action["owner"] if isinstance(action, dict) else action.owner
        delta = action["expected_delta"] if isinstance(action, dict) else action.expected_delta
        steps.append(
            PlannerStep(
                step=f"{title}: {note}",
                owner=owner,
                due_in_days=due_in_days,
                expected_delta=delta,
                policy_checks=policy_checks,
            )
        )

    return PlannerResponse(objective=objective, generated_at=datetime.utcnow(), steps=steps)
