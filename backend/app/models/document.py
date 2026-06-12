from uuid import uuid4

from app.config.database import db

from app.models.enums.user_role import TypeDocument
from sqlalchemy import Enum # type: ignore[import]

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
        db.ForeignKey("users.id"),
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
    deleted_at = db.Column(
        db.DateTime,
        nullable = True
    )
