from sqlalchemy.orm import Session

from app.models import NotificationORM
from app.schemas import NotificationCreate


def create_notification(db: Session, payload: NotificationCreate) -> NotificationORM:
    notification = NotificationORM(
        channel=payload.channel,
        recipient=payload.recipient,
        subject=payload.subject,
        body=payload.body,
        status="queued",
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def mark_sent(db: Session, notification_id: int) -> NotificationORM | None:
    record = db.get(NotificationORM, notification_id)
    if not record:
        return None
    record.status = "sent"
    db.commit()
    db.refresh(record)
    return record
