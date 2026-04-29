from models.checklist import ChecklistItem


def evaluate_policy_warnings(checklist: list[ChecklistItem], projected_score: float) -> list[str]:
    warnings: list[str] = []
    failing_critical = [
        item
        for item in checklist
        if item.status == "Fail" and item.category in {"Compliance", "Legal", "Clinical Safety"}
    ]
    if failing_critical:
        warnings.append(
            "Critical gate failures remain in Compliance/Legal/Clinical Safety."
        )
    if projected_score < 80:
        warnings.append("Projected readiness remains below go-live threshold (80%).")
    if not warnings:
        warnings.append("No blocking policy violations detected.")
    return warnings
