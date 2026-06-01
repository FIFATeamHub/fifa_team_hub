from uuid import uuid4

from sqlalchemy import Enum # type: ignore[import]

from app.config.database import db # type: ignore[import]
from app.models.enums.user_role import UserRole
from app.models.enums.user_role import TypeDocument
from app.models.enums.user_role import LogAction


class Selection(db.Model):
    __tablename__ = "selection"

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    name = db.Column(
        db.String(255),
        nullable=False
    )

    code = db.Column(
        db.String(3),
        unique=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    full_name = db.Column(
        db.String(255),
        nullable=False
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        Enum(UserRole),
        nullable=False
    )

    selection_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("selection.id"),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )


class Document(db.Model):
    __tablename__ = "document"

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    selection_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("selection.id"),
        nullable=False
    )

    uploaded_by = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("user.id"),
        nullable=False
    )

    type = db.Column(
        Enum(TypeDocument),
        nullable=False
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    storage_url = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

class AuditLog(db.Model):
    __tablename__ = "audit_log"

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )   

    user_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("user.id"),
        nullable=False
    )

    action = db.Column(
        Enum(LogAction),
        nullable=False
    )

    resource_id = db.Column(
        db.UUID(as_uuid=True),
        nullable=False
    )

    ip_address = db.Column(
        db.String(45),
        nullable=False
    )

    status = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )