from uuid import uuid4

from app.config.database import db

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