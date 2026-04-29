from fastapi import APIRouter

from app.schemas import HealthResponse

router = APIRouter(prefix="/v1", tags=["platform"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")
