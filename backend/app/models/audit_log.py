from uuid import uuid4
from app.extensions import db
from app.models.enums.user_role import LogAction
from sqlalchemy import Enum # type: ignore[import]

class AuditLog(db.Model):
    __tablename__ = "audit_log"

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )   

    user_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("users.id"),
        nullable=True
    )

    action = db.Column(
        Enum(LogAction),
        nullable=False
    )

    resource_id = db.Column(
        db.UUID(as_uuid=True),
        nullable=False
    )

    selection_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("selection.id"),
        nullable=True
    )

    ip_address = db.Column(
        db.String(45),
        nullable=False
    )

    status = db.Column(
        db.String(255),
        nullable=False
    )

    details = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )