from uuid import uuid4

from werkzeug.security import generate_password_hash #Gera a senha em hash para user.password_hash

from sqlalchemy import Enum # type: ignore[import]
from sqlalchemy.orm import Mapped,registry

from app.config.database import db # type: ignore[import]
from app.models.enums.user_role import UserRole
from app.models.enums.user_role import TypeDocument
from app.models.enums.user_role import LogAction




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
        generate_password_hash("senha_recebida"),
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

def senha_para_hash(value):
    return generate_password_hash(value)

table_registry = registry()
