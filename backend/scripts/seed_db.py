import json
import sys
from pathlib import Path

from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.auth.security import hash_password
from app.db.session import SessionLocal
from app.models import ChecklistItemORM, MilestoneORM, RAIDItemORM, UserORM, WorkstreamORM


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"


def _load_json(filename: str) -> list[dict]:
    with (DATA_DIR / filename).open("r", encoding="utf-8") as file:
        return json.load(file)


def _seed_workstreams(db: Session) -> None:
    for row in _load_json("workstreams.json"):
        db.merge(WorkstreamORM(**row))


def _seed_milestones(db: Session) -> None:
    for row in _load_json("milestones.json"):
        row["depends_on"] = json.dumps(row.get("depends_on", []))
        db.merge(MilestoneORM(**row))


def _seed_raid_items(db: Session) -> None:
    for row in _load_json("raid.json"):
        db.merge(RAIDItemORM(**row))


def _seed_checklist_items(db: Session) -> None:
    for row in _load_json("checklist.json"):
        db.merge(ChecklistItemORM(**row))


def _seed_users(db: Session) -> None:
    admin = UserORM(
        id="admin-1",
        email="admin@example.com",
        full_name="Default Admin",
        role="admin",
        hashed_password=hash_password("admin123"),
        is_active=True,
    )
    operator = UserORM(
        id="operator-1",
        email="operator@example.com",
        full_name="Default Operator",
        role="operator",
        hashed_password=hash_password("operator123"),
        is_active=True,
    )
    viewer = UserORM(
        id="viewer-1",
        email="viewer@example.com",
        full_name="Default Viewer",
        role="viewer",
        hashed_password=hash_password("viewer123"),
        is_active=True,
    )
    db.merge(admin)
    db.merge(operator)
    db.merge(viewer)


def main() -> None:
    db = SessionLocal()
    try:
        _seed_workstreams(db)
        _seed_milestones(db)
        _seed_raid_items(db)
        _seed_checklist_items(db)
        _seed_users(db)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
