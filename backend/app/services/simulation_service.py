from dataclasses import replace

from scoring.readiness import compute_readiness

from app.schemas import ScenarioSimulationRequest, ScenarioSimulationResponse
from app.services.growth_agent_service import load_domain_data
from app.services.policy_service import evaluate_policy_warnings


def run_simulation(db, request: ScenarioSimulationRequest) -> ScenarioSimulationResponse:
    workstreams, milestones, raid_items, checklist = load_domain_data(db)
    baseline = compute_readiness(workstreams, milestones, raid_items, checklist)["overall"]

    sim_workstreams = [
        replace(ws, status="On Track") if ws.id in request.recover_workstream_ids else ws
        for ws in workstreams
    ]
    sim_milestones = [
        replace(ms, status="On Track") if ms.id in request.recover_milestone_ids else ms
        for ms in milestones
    ]
    sim_raid = [
        replace(item, status="Mitigated") if item.id in request.resolve_raid_ids else item
        for item in raid_items
    ]
    sim_checklist = [
        replace(item, status="Pass") if item.id in request.pass_checklist_ids else item
        for item in checklist
    ]

    projected = compute_readiness(sim_workstreams, sim_milestones, sim_raid, sim_checklist)[
        "overall"
    ]
    warnings = evaluate_policy_warnings(sim_checklist, projected)

    return ScenarioSimulationResponse(
        baseline_score=baseline,
        projected_score=projected,
        delta=round(projected - baseline, 1),
        policy_warnings=warnings,
    )
