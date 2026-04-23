from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WorkstreamORM(Base):
    __tablename__ = "workstreams"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    progress: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    blocker: Mapped[str | None] = mapped_column(Text, nullable=True)


class MilestoneORM(Base):
    __tablename__ = "milestones"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    due_week: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    workstream_id: Mapped[str] = mapped_column(String(50), nullable=False)
    depends_on: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class RAIDItemORM(Base):
    __tablename__ = "raid_items"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    urgency: Mapped[str] = mapped_column(String(50), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    mitigation: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)


class ChecklistItemORM(Base):
    __tablename__ = "checklist_items"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    item: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
