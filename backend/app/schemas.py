from datetime import datetime

from pydantic import BaseModel, EmailStr


class HealthResponse(BaseModel):
    status: str


class GrowthActionResponse(BaseModel):
    title: str
    owner: str
    domain: str
    reason: str
    expected_delta: float
    priority_score: float
    urgency: str
    no_go_block: bool
    execution_note: str


class GrowthBriefResponse(BaseModel):
    readiness: dict
    projected_score_after_top_actions: float
    no_go_actions_count: int
    top_actions: list[GrowthActionResponse]
    owner_queue: dict
    command_rhythm: list[dict]
    trigger_matrix: list[dict]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str = "viewer"
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WorkstreamPayload(BaseModel):
    id: str
    name: str
    owner: str
    status: str
    progress: int
    priority: str
    blocker: str | None = None


class MilestonePayload(BaseModel):
    id: str
    name: str
    due_week: int
    status: str
    owner: str
    workstream_id: str
    depends_on: list[str] = []


class RAIDItemPayload(BaseModel):
    id: str
    category: str
    title: str
    description: str
    severity: str
    urgency: str
    owner: str
    mitigation: str
    status: str


class ChecklistItemPayload(BaseModel):
    id: str
    category: str
    item: str
    status: str
    owner: str
    evidence: str | None = None


class AuditLogResponse(BaseModel):
    id: int
    actor_user_id: str
    actor_role: str
    action: str
    resource_type: str
    resource_id: str | None
    details: str
    created_at: datetime

    class Config:
        from_attributes = True


class PlannerRequest(BaseModel):
    objective: str
    horizon_days: int = 14


class PlannerStep(BaseModel):
    step: str
    owner: str
    due_in_days: int
    expected_delta: float
    policy_checks: list[str]


class PlannerResponse(BaseModel):
    objective: str
    generated_at: datetime
    steps: list[PlannerStep]


class ScenarioSimulationRequest(BaseModel):
    resolve_raid_ids: list[str] = []
    pass_checklist_ids: list[str] = []
    recover_milestone_ids: list[str] = []
    recover_workstream_ids: list[str] = []


class ScenarioSimulationResponse(BaseModel):
    baseline_score: float
    projected_score: float
    delta: float
    policy_warnings: list[str]


class RecommendationMemoryUpsert(BaseModel):
    recommendation_key: str
    context: str
    recommendation: str
    outcome: str | None = None
    score_delta: float = 0.0
    feedback_rating: int | None = None


class NotificationCreate(BaseModel):
    channel: str
    recipient: str
    subject: str
    body: str
