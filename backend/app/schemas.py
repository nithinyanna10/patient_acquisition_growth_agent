from pydantic import BaseModel


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
