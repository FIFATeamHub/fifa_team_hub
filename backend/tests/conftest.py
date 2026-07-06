import pytest

from app import create_app
from app.extensions import db

from app.models.selection import Selection
from app.models.user import User
from app.models.document import Document

from app.models.enums.user_role import (
    UserRole,
    TypeDocument,
    DocStatus,
)

from app.services.auth import (
    hash_password,
    create_access_token,
)


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

    return create_access_token(bra_staff)


@pytest.fixture
def token_arg_staff(arg_staff):

    return create_access_token(arg_staff)


@pytest.fixture
def token_organizer(organizer):

    return create_access_token(organizer)


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
            storage_url="/tmp/relatorio.pdf",
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