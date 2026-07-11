import uuid
import pytest
from unittest.mock import patch, MagicMock

from app import create_app
from app.extensions import db

from app.models.selection import Selection
from app.models.user import User
from app.models.document import Document
from app.models.audit_log import AuditLog
from sqlalchemy import text

from app.models.enums.user_role import (
    UserRole,
    TypeDocument,
    DocStatus,
    LogAction,
)

from app.services.auth import hash_password, create_access_token, user_to_token_payload


# ----------------------------------------------------------------------
# APP
# ----------------------------------------------------------------------

@pytest.fixture
def app():

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "STORAGE_BACKEND": "local",
        "LOCAL_STORAGE_PATH": "/tmp/test_uploads",
    })

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


# ----------------------------------------------------------------------
# CLIENT
# ----------------------------------------------------------------------

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(name="db")
def db_session(app):
    with app.app_context():
        yield db.session


# ----------------------------------------------------------------------
# SELECTIONS
# ----------------------------------------------------------------------

@pytest.fixture
def selection_bra(app):

    with app.app_context():

        selection = Selection(
            name="Brazil",
            code="BRA"
        )

        db.session.add(selection)
        db.session.commit()

        return selection.id


@pytest.fixture
def selection_arg(app):

    with app.app_context():

        selection = Selection(
            name="Argentina",
            code="ARG"
        )

        db.session.add(selection)
        db.session.commit()

        return selection.id


# ----------------------------------------------------------------------
# USERS
# ----------------------------------------------------------------------

@pytest.fixture
def bra_staff(app, selection_bra):

    with app.app_context():

        user = User(
            full_name="Brazil Technical Staff",
            email="bra.staff@test.com",
            password_hash=hash_password("123456"),
            role=UserRole.TECHNICAL_STAFF,
            selection_id=selection_bra
        )

        db.session.add(user)
        db.session.commit()

        db.session.refresh(user)
        db.session.expunge(user)

        return user


@pytest.fixture
def organizer(app):

    with app.app_context():

        user = User(
            full_name="Organizer",
            email="organizer@test.com",
            password_hash=hash_password("123456"),
            role=UserRole.ORGANIZER,
            selection_id=None
        )

        db.session.add(user)
        db.session.commit()

        db.session.refresh(user)
        db.session.expunge(user)

        return user

@pytest.fixture
def auditor(app):
    with app.app_context():
        user = User(
            full_name="Auditor do Sistema",
            email="auditor@test.com",
            password_hash=hash_password("123456"),
            role=UserRole.AUDITOR,
            selection_id=None
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        db.session.expunge(user)
        return user


@pytest.fixture
def bra_auditor(app, selection_bra):
    with app.app_context():
        user = User(
            full_name="Auditor Brasil",
            email="auditor.bra@test.com",
            password_hash=hash_password("123456"),
            role=UserRole.AUDITOR,
            selection_id=selection_bra
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        db.session.expunge(user)
        return user


@pytest.fixture
def arg_staff(app, selection_arg):

    with app.app_context():

        user = User(
            full_name="Argentina Technical Staff",
            email="arg.staff@test.com",
            password_hash=hash_password("123456"),
            role=UserRole.TECHNICAL_STAFF,
            selection_id=selection_arg
        )

        db.session.add(user)
        db.session.commit()

        db.session.refresh(user)
        db.session.expunge(user)

        return user


# ----------------------------------------------------------------------
# TOKENS
# ----------------------------------------------------------------------

@pytest.fixture
def token_bra_staff(bra_staff):
    return create_access_token(user_to_token_payload(bra_staff))


@pytest.fixture
def token_arg_staff(arg_staff):

    return create_access_token(user_to_token_payload(arg_staff))

@pytest.fixture
def token_auditor(auditor):
    return create_access_token(user_to_token_payload(auditor))

@pytest.fixture
def token_bra_auditor(bra_auditor):
    return create_access_token(user_to_token_payload(bra_auditor))

@pytest.fixture
def token_organizer(organizer):

    return create_access_token(user_to_token_payload(organizer))


# ----------------------------------------------------------------------
# DOCUMENTOS
# ----------------------------------------------------------------------

@pytest.fixture
def arg_document(app, arg_staff, selection_arg):

    with app.app_context():

        document = Document(
            selection_id=selection_arg,
            uploaded_by=arg_staff.id,
            type=TypeDocument.RELATORIO_TATICO,
            original_name="relatorio.pdf",
            storage_path="/tmp/relatorio.pdf",
            status=DocStatus.APPROVED.value
        )

        db.session.add(document)
        db.session.commit()

        db.session.refresh(document)
        db.session.expunge(document)

        return document


@pytest.fixture
def arg_document_id(arg_document):

    return str(arg_document.id)

@pytest.fixture
def gcs_app(app):
    app.config.update({
        "STORAGE_BACKEND": "gcs",
        "GCS_BUCKET_NAME": "test-bucket",
        "GCP_PROJECT_ID": "test-project",
    })
    return app


@pytest.fixture
def gcs_client(gcs_app):
    return gcs_app.test_client()


@pytest.fixture
def mock_gcs_storage():
    with patch("app.services.storage_factory.GCSStorageService") as mock_cls:
        service = MagicMock()
        service.save_file.return_value = "gs://bucket/BRA/doc.pdf"
        service.get_signed_url.return_value = "https://signed-url"
        mock_cls.return_value = service
        yield service


def create_test_document(db, **overrides):
    defaults = dict(
        id=uuid.uuid4(),
        type=TypeDocument.CONVOCADO,
        original_name="doc.pdf",
        storage_path="gs://bucket/BRA/doc.pdf",
        storage_url="gs://bucket/BRA/doc.pdf",
        status=DocStatus.APPROVED.value,
    )
    defaults.update(overrides)
    doc = Document(**defaults)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_latest_audit_log(db, *, action=None, user_id=None, status=None):
    query = db.query(AuditLog)
    if action is not None:
        query = query.filter_by(action=action)
    if user_id is not None:
        query = query.filter_by(user_id=user_id)
    if status is not None:
        query = query.filter_by(status=status)
    return query.order_by(AuditLog.created_at.desc()).first()

def get_latest_audit_log(db, *, action=None, user_id=None, status=None):
    rows = db.execute(text("""
        SELECT *
        FROM audit_log
    """)).fetchall()

    print("AUDIT_LOG:", rows)
    schema = db.execute(text("PRAGMA table_info(audit_log)")).fetchall()
    print(schema)
    print(
    db.execute(text("PRAGMA table_info(audit_log)")).fetchall()
    )

    query = db.query(AuditLog)

    if action is not None:
        query = query.filter_by(action=action)
    if user_id is not None:
        query = query.filter_by(user_id=user_id)
    if status is not None:
        query = query.filter_by(status=status)

    return query.order_by(AuditLog.created_at.desc()).first()