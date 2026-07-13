from uuid import uuid4
from app.extensions import db

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
        nullable=True
    )

    selection = db.relationship(
        "Selection",
        backref="documents"
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

    # filename = db.Column(     # NOME COM O ID -> ENCRIPITADO
    #     db.String(255),
    #     nullable=False
    # )

    original_name = db.Column(
        db.String(255), 
        nullable=True
    )

    storage_path = db.Column(
        db.String(255),
        nullable=True
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="PENDING"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
    deleted_at = db.Column(
        db.DateTime,
        nullable = True
    )

    reviewed_by = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("users.id"),
        nullable=True
    )

    reviewed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    storage_url = db.Column(
        db.String(500),
        nullable=True
    )