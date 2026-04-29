import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

backend_dir = Path(__file__).resolve().parents[1]
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(backend_dir))
sys.path.insert(1, str(repo_root))

from app.auth.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import (
    ChecklistItemORM,
    MilestoneORM,
    RAIDItemORM,
    UserORM,
    WorkstreamORM,
)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db: Session = TestingSessionLocal()
    db.add(
        UserORM(
            id="admin-1",
            email="admin@example.com",
            full_name="Admin",
            role="admin",
            hashed_password=hash_password("admin123"),
            is_active=True,
        )
    )
    db.add(
        WorkstreamORM(
            id="ws-1",
            name="EHR Integration",
            owner="Owner",
            status="At Risk",
            progress=65,
            priority="High",
            blocker="Credential delay",
        )
    )
    db.add(
        MilestoneORM(
            id="ms-1",
            name="UAT",
            due_week=4,
            status="At Risk",
            owner="Owner",
            workstream_id="ws-1",
            depends_on=json.dumps([]),
        )
    )
    db.add(
        RAIDItemORM(
            id="risk-1",
            category="Risk",
            title="Rate limit",
            description="desc",
            severity="High",
            urgency="Immediate",
            owner="Owner",
            mitigation="mitigate",
            status="Open",
        )
    )
    db.add(
        ChecklistItemORM(
            id="ck-1",
            category="Compliance",
            item="HIPAA",
            status="Pass",
            owner="Owner",
            evidence="evidence",
        )
    )
    db.commit()
    db.close()


@pytest.fixture()
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
