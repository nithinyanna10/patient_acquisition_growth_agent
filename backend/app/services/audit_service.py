from sqlalchemy.orm import Session

from app.models import AuditLogORM, UserORM


def write_audit_log(
    db: Session,
    actor: UserORM,
    action: str,
    resource_type: str,
    resource_id: str | None,
    details: str = "{}",
) -> AuditLogORM:
    log = AuditLogORM(
        actor_user_id=actor.id,
        actor_role=actor.role,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
