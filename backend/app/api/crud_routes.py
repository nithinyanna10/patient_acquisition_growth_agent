import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import require_roles
from app.db.session import get_db
from app.models import ChecklistItemORM, MilestoneORM, RAIDItemORM, UserORM, WorkstreamORM
from app.schemas import (
    ChecklistItemPayload,
    MilestonePayload,
    RAIDItemPayload,
    WorkstreamPayload,
)
from app.services.audit_service import write_audit_log

router = APIRouter(prefix="/v1", tags=["crud"])


@router.get("/workstreams", response_model=list[WorkstreamPayload])
def list_workstreams(
    db: Session = Depends(get_db), _: UserORM = Depends(require_roles({"admin", "operator", "viewer"}))
):
    return db.query(WorkstreamORM).all()


@router.put("/workstreams/{workstream_id}", response_model=WorkstreamPayload)
def upsert_workstream(
    workstream_id: str,
    payload: WorkstreamPayload,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(require_roles({"admin", "operator"})),
):
    if workstream_id != payload.id:
        raise HTTPException(status_code=400, detail="Path ID mismatch")
    record = db.get(WorkstreamORM, payload.id) or WorkstreamORM(id=payload.id)
    for key, value in payload.model_dump().items():
        setattr(record, key, value)
    db.add(record)
    db.commit()
    db.refresh(record)
    write_audit_log(db, current_user, "UPSERT", "workstream", payload.id)
    return record


@router.get("/milestones", response_model=list[MilestonePayload])
def list_milestones(
    db: Session = Depends(get_db), _: UserORM = Depends(require_roles({"admin", "operator", "viewer"}))
):
    rows = db.query(MilestoneORM).all()
    return [
        MilestonePayload(
            id=r.id,
            name=r.name,
            due_week=r.due_week,
            status=r.status,
            owner=r.owner,
            workstream_id=r.workstream_id,
            depends_on=json.loads(r.depends_on or "[]"),
        )
        for r in rows
    ]


@router.put("/milestones/{milestone_id}", response_model=MilestonePayload)
def upsert_milestone(
    milestone_id: str,
    payload: MilestonePayload,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(require_roles({"admin", "operator"})),
):
    if milestone_id != payload.id:
        raise HTTPException(status_code=400, detail="Path ID mismatch")
    record = db.get(MilestoneORM, payload.id) or MilestoneORM(id=payload.id)
    dumped = payload.model_dump()
    dumped["depends_on"] = json.dumps(payload.depends_on)
    for key, value in dumped.items():
        setattr(record, key, value)
    db.add(record)
    db.commit()
    db.refresh(record)
    write_audit_log(db, current_user, "UPSERT", "milestone", payload.id)
    return payload


@router.get("/raid", response_model=list[RAIDItemPayload])
def list_raid(
    db: Session = Depends(get_db), _: UserORM = Depends(require_roles({"admin", "operator", "viewer"}))
):
    return db.query(RAIDItemORM).all()


@router.put("/raid/{raid_id}", response_model=RAIDItemPayload)
def upsert_raid(
    raid_id: str,
    payload: RAIDItemPayload,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(require_roles({"admin", "operator"})),
):
    if raid_id != payload.id:
        raise HTTPException(status_code=400, detail="Path ID mismatch")
    record = db.get(RAIDItemORM, payload.id) or RAIDItemORM(id=payload.id)
    for key, value in payload.model_dump().items():
        setattr(record, key, value)
    db.add(record)
    db.commit()
    db.refresh(record)
    write_audit_log(db, current_user, "UPSERT", "raid_item", payload.id)
    return record


@router.get("/checklist", response_model=list[ChecklistItemPayload])
def list_checklist(
    db: Session = Depends(get_db), _: UserORM = Depends(require_roles({"admin", "operator", "viewer"}))
):
    return db.query(ChecklistItemORM).all()


@router.put("/checklist/{item_id}", response_model=ChecklistItemPayload)
def upsert_checklist(
    item_id: str,
    payload: ChecklistItemPayload,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(require_roles({"admin", "operator"})),
):
    if item_id != payload.id:
        raise HTTPException(status_code=400, detail="Path ID mismatch")
    record = db.get(ChecklistItemORM, payload.id) or ChecklistItemORM(id=payload.id)
    for key, value in payload.model_dump().items():
        setattr(record, key, value)
    db.add(record)
    db.commit()
    db.refresh(record)
    write_audit_log(db, current_user, "UPSERT", "checklist_item", payload.id)
    return record
