from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import GrowthBriefResponse, HealthResponse
from app.services.growth_agent_service import get_growth_brief

router = APIRouter(prefix="/v1", tags=["growth-agent"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/agent/brief", response_model=GrowthBriefResponse)
def growth_agent_brief(db: Session = Depends(get_db)) -> GrowthBriefResponse:
    payload = get_growth_brief(db)
    return GrowthBriefResponse(**payload)
