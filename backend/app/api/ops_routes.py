import csv
import io

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.auth.deps import require_roles
from app.db.session import get_db
from app.models import AuditLogORM, NotificationORM, UserORM
from app.schemas import AuditLogResponse, NotificationCreate
from app.services.audit_service import write_audit_log
from app.services.notification_service import create_notification, mark_sent

router = APIRouter(prefix="/v1/ops", tags=["operations"])


@router.get("/audit", response_model=list[AuditLogResponse])
def list_audit_logs(
    db: Session = Depends(get_db),
    _: UserORM = Depends(require_roles({"admin", "operator"})),
):
    return db.query(AuditLogORM).order_by(AuditLogORM.created_at.desc()).limit(200).all()


@router.post("/notifications")
def queue_notification(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(require_roles({"admin", "operator"})),
):
    notification = create_notification(db, payload)
    write_audit_log(
        db,
        current_user,
        "QUEUE_NOTIFICATION",
        "notification",
        str(notification.id),
        payload.model_dump_json(),
    )
    return {"id": notification.id, "status": notification.status}


@router.post("/notifications/{notification_id}/sent")
def mark_notification_sent(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(require_roles({"admin", "operator"})),
):
    record = mark_sent(db, notification_id)
    write_audit_log(db, current_user, "MARK_NOTIFICATION_SENT", "notification", str(notification_id))
    return {"id": notification_id, "status": record.status if record else "not_found"}


@router.get("/exports/audit.csv")
def export_audit_csv(
    db: Session = Depends(get_db),
    _: UserORM = Depends(require_roles({"admin", "operator"})),
):
    rows = db.query(AuditLogORM).order_by(AuditLogORM.created_at.desc()).all()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["id", "actor_user_id", "actor_role", "action", "resource_type", "resource_id", "created_at"]
    )
    for row in rows:
        writer.writerow(
            [
                row.id,
                row.actor_user_id,
                row.actor_role,
                row.action,
                row.resource_type,
                row.resource_id,
                row.created_at.isoformat(),
            ]
        )
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"},
    )


@router.get("/admin")
def admin_ui(_: UserORM = Depends(require_roles({"admin"}))):
    html = """
    <html><body>
    <h2>Growth Agent Admin</h2>
    <p>Use authenticated API routes for operational control:</p>
    <ul>
      <li>/v1/ops/audit</li>
      <li>/v1/ops/notifications</li>
      <li>/v1/workstreams, /v1/milestones, /v1/raid, /v1/checklist</li>
    </ul>
    </body></html>
    """
    return Response(content=html, media_type="text/html")
