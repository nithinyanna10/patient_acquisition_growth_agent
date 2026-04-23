import json
import sys
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import ChecklistItemORM, MilestoneORM, RAIDItemORM, WorkstreamORM

# Allow backend service to import shared domain/scoring modules from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from models.checklist import ChecklistItem
from models.milestone import Milestone
from models.raid import RAIDItem
from models.workstream import Workstream
from scoring.growth_agent import summarize_agent_brief


def _load_workstreams(db: Session) -> list[Workstream]:
    rows = db.query(WorkstreamORM).all()
    return [
        Workstream(
            id=row.id,
            name=row.name,
            owner=row.owner,
            status=row.status,
            progress=row.progress,
            priority=row.priority,
            blocker=row.blocker,
        )
        for row in rows
    ]


def _load_milestones(db: Session) -> list[Milestone]:
    rows = db.query(MilestoneORM).all()
    milestones: list[Milestone] = []
    for row in rows:
        milestones.append(
            Milestone(
                id=row.id,
                name=row.name,
                due_week=row.due_week,
                status=row.status,
                owner=row.owner,
                workstream_id=row.workstream_id,
                depends_on=json.loads(row.depends_on or "[]"),
            )
        )
    return milestones


def _load_raid_items(db: Session) -> list[RAIDItem]:
    rows = db.query(RAIDItemORM).all()
    return [
        RAIDItem(
            id=row.id,
            category=row.category,
            title=row.title,
            description=row.description,
            severity=row.severity,
            urgency=row.urgency,
            owner=row.owner,
            mitigation=row.mitigation,
            status=row.status,
        )
        for row in rows
    ]


def _load_checklist(db: Session) -> list[ChecklistItem]:
    rows = db.query(ChecklistItemORM).all()
    return [
        ChecklistItem(
            id=row.id,
            category=row.category,
            item=row.item,
            status=row.status,
            owner=row.owner,
            evidence=row.evidence,
        )
        for row in rows
    ]


def get_growth_brief(db: Session) -> dict:
    workstreams = _load_workstreams(db)
    milestones = _load_milestones(db)
    raid_items = _load_raid_items(db)
    checklist = _load_checklist(db)
    return summarize_agent_brief(workstreams, milestones, raid_items, checklist)
