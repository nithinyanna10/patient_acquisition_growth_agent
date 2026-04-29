from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.deps import require_roles
from app.db.session import get_db
from app.models import RecommendationMemoryORM, UserORM
from app.schemas import (
    GrowthBriefResponse,
    PlannerRequest,
    PlannerResponse,
    RecommendationMemoryUpsert,
    ScenarioSimulationRequest,
    ScenarioSimulationResponse,
)
from app.services.audit_service import write_audit_log
from app.services.growth_agent_service import get_growth_brief
from app.services.planner_service import build_execution_plan
from app.services.simulation_service import run_simulation

router = APIRouter(prefix="/v1/agent", tags=["agent-intelligence"])


@router.get("/brief", response_model=GrowthBriefResponse)
def growth_agent_brief(
    db: Session = Depends(get_db),
    _: UserORM = Depends(require_roles({"admin", "operator", "viewer"})),
):
    payload = get_growth_brief(db)
    return GrowthBriefResponse(**payload)


@router.post("/plan", response_model=PlannerResponse)
def planner(
    payload: PlannerRequest,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(require_roles({"admin", "operator"})),
):
    plan = build_execution_plan(db, payload.objective, payload.horizon_days)
    write_audit_log(db, current_user, "PLAN", "agent", None, payload.model_dump_json())
    return plan


@router.post("/simulate", response_model=ScenarioSimulationResponse)
def simulate(
    payload: ScenarioSimulationRequest,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(require_roles({"admin", "operator"})),
):
    result = run_simulation(db, payload)
    write_audit_log(db, current_user, "SIMULATE", "agent", None, payload.model_dump_json())
    return result


@router.get("/memory", response_model=list[RecommendationMemoryUpsert])
def list_memory(
    db: Session = Depends(get_db),
    _: UserORM = Depends(require_roles({"admin", "operator", "viewer"})),
):
    rows = db.query(RecommendationMemoryORM).all()
    return [
        RecommendationMemoryUpsert(
            recommendation_key=row.recommendation_key,
            context=row.context,
            recommendation=row.recommendation,
            outcome=row.outcome,
            score_delta=row.score_delta,
            feedback_rating=row.feedback_rating,
        )
        for row in rows
    ]


@router.put("/memory/{recommendation_key}", response_model=RecommendationMemoryUpsert)
def upsert_memory(
    recommendation_key: str,
    payload: RecommendationMemoryUpsert,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(require_roles({"admin", "operator"})),
):
    record = (
        db.query(RecommendationMemoryORM)
        .filter(RecommendationMemoryORM.recommendation_key == recommendation_key)
        .first()
    )
    if not record:
        record = RecommendationMemoryORM(recommendation_key=recommendation_key)
    for key, value in payload.model_dump().items():
        setattr(record, key, value)
    db.add(record)
    db.commit()
    write_audit_log(db, current_user, "UPSERT_MEMORY", "recommendation_memory", recommendation_key)
    return payload
